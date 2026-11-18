"""Recuperação textual de PPCs, independente do índice vetorial."""
from collections import Counter
from importlib.metadata import PackageNotFoundError, version
from math import log
from pathlib import Path
import hashlib
import re
import subprocess

from resposta_estruturada import norm


TERMOS_COMUNS = set(
    "a as o os de da das do dos e em no na nos nas para por com um uma que qual "
    "quais como quanto quantos quantas tem sao ser pode fazer curso sobre me "
    "diga quero saber ppc".split()
)
TOTAL_EXPLICITO = re.compile(
    r"\bcarga horaria total (?:do|para o) curso\b"
    r"|\btotal de creditos.{0,50}\bhoras?\b"
)
TOTAL_CURSO = re.compile(
    r"\b(?:carga horaria|horas?)\b.*\b(?:total|integraliz\w*)\b|"
    r"\b(?:total|integraliz\w*)\b.*\b(?:carga horaria|horas?)\b"
)


def ler_ppc(pdf):
    pdf = Path(pdf)
    try:
        chave = hashlib.sha256(pdf.read_bytes()).hexdigest()
        cache = Path("cache_ppcs") / f"{chave}-{version('docling')}.md"
        if cache.is_file():
            return cache.read_text(encoding="utf-8")
    except (OSError, PackageNotFoundError):
        pass
    try:
        resultado = subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"],
            capture_output=True, check=True, timeout=25,
        )
        return resultado.stdout.decode("utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return ""


def _termos(texto):
    return set(re.findall(r"[a-z0-9]+", norm(texto))) - TERMOS_COMUNS


def preparar_trechos(texto):
    trechos = []
    for pagina in texto.split("\f"):
        linhas = pagina.splitlines()
        for inicio in range(0, len(linhas), 5):
            trecho = "\n".join(linhas[inicio:inicio + 8]).strip()
            if trecho:
                trecho = trecho[:2400]
                trechos.append((trecho, _termos(trecho)))
    frequencias = Counter(termo for _, termos in trechos for termo in termos)
    return trechos, frequencias


def buscar_trechos(pergunta, indice, limite=5):
    trechos, frequencias = indice
    relevantes = _termos(pergunta)
    pergunta_normalizada = norm(pergunta)
    palavras = set(pergunta_normalizada.split())
    total_curso = TOTAL_CURSO.search(pergunta_normalizada) and (
        "curso" in palavras or relevantes <= {"carga", "horaria", "total", "horas"}
    )
    pesos = {termo: log(1 + len(trechos) / (1 + frequencias[termo])) for termo in relevantes}

    candidatos = []
    for trecho, termos in trechos:
        comuns = relevantes & termos
        if not comuns:
            continue
        pontos = sum(pesos[termo] for termo in comuns)
        if total_curso:
            linhas = [norm(linha) for linha in trecho.splitlines()]
            if any(TOTAL_EXPLICITO.search(linha) for linha in linhas):
                pontos += 12
            elif any(TOTAL_CURSO.search(linha) for linha in linhas):
                pontos += 2
        candidatos.append((pontos, trecho))

    selecionados = []
    for _, trecho in sorted(candidatos, reverse=True):
        linhas = {linha.strip() for linha in trecho.splitlines() if linha.strip()}
        if any(len(linhas & anteriores) > 1 for anteriores, _ in selecionados):
            continue
        selecionados.append((linhas, trecho))
        if len(selecionados) == limite:
            break
    return [trecho for _, trecho in selecionados]
