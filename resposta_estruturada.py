"""
resposta_estruturada.py — Camada de resposta direta por metadados
=====================================================================
Ideia trazida do rag_core.py da colega (fuzzy matching de disciplina +
detecção de intenção) e reescrita para usar o schema de metadados que já
existe neste projeto (tabela_utils.py): "disciplina", "periodo", "cr",
"ch", "apcc", "total", "curso".

Por que existe: perguntas do tipo "qual a carga horária de Cálculo I?"
não deveriam depender do LLM — ele pode arredondar, inventar ou misturar
disciplinas parecidas. Aqui a resposta vem direto dos metadados extraídos
da grade curricular (tabela.py de cada curso), sem chance de alucinação.

Se a camada não conseguir identificar com confiança a disciplina + a
intenção da pergunta, devolve None — quem chamar cai no fallback semântico
(RAG + LLM) normalmente.
"""

from __future__ import annotations

import re
import unicodedata
import difflib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_chroma import Chroma

# palavra-chave da pergunta -> campo de metadado correspondente
CAMPO_POR_INTENCAO = {
    "cr": ["credito", "créditos", "quantos creditos", "quantos créditos"],
    "ch": ["carga horaria", "carga horária", "quantas horas teoricas", "horas teoricas"],
    "apcc": ["apcc", "horas praticas", "horas práticas", "atividade pratica"],
    "total": ["carga horaria total", "total de horas", "quantas horas"],
    "periodo": ["periodo", "período", "qual periodo", "que periodo", "semestre"],
    "prereq": ["pre-requisito", "pre requisito", "prerequisito", "requisito"],
}

# a ordem importa: intenções mais específicas (ex: "carga horaria total")
# precisam ser checadas antes das mais genéricas (ex: "carga horaria")
ORDEM_INTENCAO = ["prereq", "apcc", "total", "cr", "ch", "periodo"]

PALAVRAS_LISTAGEM = [
    "liste", "listar", "lista de", "quais materias", "quais matérias",
    "quais disciplinas", "quais sao as", "quais são as", "todas as materias",
    "todas as matérias", "todas as disciplinas", "mostre as materias",
    "mostre as disciplinas", "me liste", "me mostre",
]

ORDINAIS_PERIODO = {
    "primeiro": "1", "segundo": "2", "terceiro": "3", "quarto": "4",
    "quinto": "5", "sexto": "6", "setimo": "7", "oitavo": "8",
}

LABEL_CAMPO = {
    "cr": "Créditos",
    "ch": "Carga horária teórica",
    "apcc": "Carga horária de APCC (prática)",
    "total": "Carga horária total",
    "periodo": "Período",
    "prereq": "Pré-requisito(s)",
}


def norm(txt: str) -> str:
    if not txt:
        return ""
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("utf-8")
    txt = txt.lower()
    return re.sub(r"\s+", " ", txt).strip()


class BaseDisciplinas:
    """Índice em memória, por curso, de disciplina normalizada -> metadados.
    Construído a partir dos metadados já gravados no Chroma (não precisa
    reprocessar o PDF nem o tabela.py)."""

    def __init__(self):
        self.por_curso: dict[str, dict[str, dict]] = {}
        self.todas_por_curso: dict[str, list[dict]] = {}

    @classmethod
    def carregar(cls, db: "Chroma") -> "BaseDisciplinas":
        base = cls()
        registros = db.get(include=["metadatas"])
        metadatas = registros.get("metadatas", []) or []

        for meta in metadatas:
            nome = meta.get("disciplina")
            curso_id = meta.get("curso")
            if not nome or not curso_id:
                continue  # chunk genérico do PDF, sem ficha de disciplina

            por_nome = base.por_curso.setdefault(curso_id, {})
            todas = base.todas_por_curso.setdefault(curso_id, [])

            por_nome[norm(nome)] = meta
            if not any(t.get("disciplina") == nome for t in todas):
                todas.append(meta)

        return base

    def buscar_disciplina(self, curso_id: str, pergunta_normalizada: str, corte: float = 0.72):
        nomes = list(self.por_curso.get(curso_id, {}).keys())
        if not nomes:
            return None

        candidatos_substring = [n for n in nomes if n and n in pergunta_normalizada]
        if candidatos_substring:
            melhor = max(candidatos_substring, key=len)
            return self.por_curso[curso_id][melhor]

        palavras = pergunta_normalizada.split()
        melhor_nome, melhor_score = None, 0.0
        for nome in nomes:
            tam = len(nome.split())
            janelas = [" ".join(palavras[i:i + tam]) for i in range(len(palavras) - tam + 1)] or [pergunta_normalizada]
            for janela in janelas:
                score = difflib.SequenceMatcher(None, nome, janela).ratio()
                if score > melhor_score:
                    melhor_score, melhor_nome = score, nome

        if melhor_nome and melhor_score >= corte:
            return self.por_curso[curso_id][melhor_nome]
        return None

    def listar_por_periodo(self, curso_id: str, periodo_alvo: str) -> list:
        todas = self.todas_por_curso.get(curso_id, [])
        encontradas = [m for m in todas if str(m.get("periodo", "")) == periodo_alvo]
        return sorted(encontradas, key=lambda m: m.get("disciplina", ""))


def detectar_intencao(pergunta_normalizada: str):
    for campo in ORDEM_INTENCAO:
        palavras_chave = CAMPO_POR_INTENCAO[campo]
        if any(pc in pergunta_normalizada for pc in palavras_chave):
            return campo
    return None


def detectar_periodo_alvo(pergunta_normalizada: str):
    for palavra, numero in ORDINAIS_PERIODO.items():
        if palavra in pergunta_normalizada:
            return numero
    m = re.search(r"(\d+)\s*o?\s*period", pergunta_normalizada)
    if m:
        return m.group(1)
    m = re.search(r"period\w*\s*(\d+)", pergunta_normalizada)
    if m:
        return m.group(1)
    return None


def eh_pergunta_de_listagem(pergunta_normalizada: str) -> bool:
    return any(p in pergunta_normalizada for p in PALAVRAS_LISTAGEM)


def formatar_tabela(headers: list, linhas: list) -> str:
    larguras = [
        max(len(str(headers[i])), *(len(str(l[i])) for l in linhas)) if linhas
        else len(str(headers[i]))
        for i in range(len(headers))
    ]

    def fmt_linha(valores: list) -> str:
        return " | ".join(str(v).ljust(larguras[i]) for i, v in enumerate(valores))

    separador = "-+-".join("-" * w for w in larguras)
    corpo = "\n".join(fmt_linha(l) for l in linhas)
    return f"{fmt_linha(headers)}\n{separador}\n{corpo}"


def responder_listagem(pergunta: str, base: BaseDisciplinas, curso_id: str):
    q_norm = norm(pergunta)
    if not eh_pergunta_de_listagem(q_norm):
        return None

    periodo_alvo = detectar_periodo_alvo(q_norm)
    if periodo_alvo is None:
        return None

    disciplinas = base.listar_por_periodo(curso_id, periodo_alvo)
    if not disciplinas:
        return f"Não encontrei disciplinas cadastradas para o {periodo_alvo}º período nesse curso."

    linhas = [
        [m.get("disciplina", ""), m.get("cr", ""), m.get("total", ""), ", ".join(m.get("prereq", [])) if isinstance(m.get("prereq"), list) else (m.get("prereq") or "—")]
        for m in disciplinas
    ]
    tabela = formatar_tabela(["Disciplina", "Créditos", "Carga Horária Total", "Pré-requisitos"], linhas)
    return f"Disciplinas — {periodo_alvo}º Período ({len(disciplinas)}):\n\n{tabela}"


def responder_direto(pergunta: str, base: BaseDisciplinas, curso_id: str):
    q_norm = norm(pergunta)

    intencao = detectar_intencao(q_norm)
    if not intencao:
        return None

    disciplina_meta = base.buscar_disciplina(curso_id, q_norm)
    if not disciplina_meta:
        return None

    valor = disciplina_meta.get(intencao)

    # prereq vazio é uma resposta válida (disciplina sem pré-requisito);
    # os demais campos vazios/ausentes indicam metadado não encontrado,
    # melhor cair no fallback semântico do que arriscar responder errado
    if intencao == "prereq":
        valor = valor or "Nenhum"
    elif not valor and valor != 0:
        return None

    nome_disciplina = disciplina_meta.get("disciplina", "")
    sufixo = "h" if intencao in ("ch", "apcc", "total") else ""
    return f"{LABEL_CAMPO[intencao]} de {nome_disciplina}: {valor}{sufixo}"


def responder_estruturado(pergunta: str, base: BaseDisciplinas, curso_id: str):
    """Tenta listagem e resposta direta por metadados (sem LLM). Retorna
    None se nenhuma camada souber responder — sinal para cair no RAG+LLM."""
    resposta = responder_listagem(pergunta, base, curso_id)
    if resposta is not None:
        return resposta
    return responder_direto(pergunta, base, curso_id)