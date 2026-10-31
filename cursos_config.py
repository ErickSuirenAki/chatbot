"""Cursos existentes e descoberta de novos PPCs em cursos/*/curso.json.

Cada pasta nova contém ppc.pdf e curso.json com nome, campus e versao.
A matriz tabela.py é opcional: sem ela, as consultas usam o texto do PPC.
Use uma pasta distinta para cada campus e versão da matriz.
"""

import importlib
import json
from pathlib import Path

CURSOS_EXISTENTES = {
    "ciencia_computacao": {
        "nome": "Ciência da Computação — Bacharelado — Porto Velho — PPC 2014",
        "campus": "Porto Velho",
        "versao": "PPC 2014",
        "pasta": "cursos/ciencia_computacao",
    },
    "pedagogia": {
        "nome": "Pedagogia — Licenciatura — Ji-Paraná — PPC 2018",
        "campus": "Ji-Paraná",
        "versao": "PPC 2018",
        "pasta": "cursos/pedagogia",
    },
}


def carregar_tabela(pasta):
    """Ausência de tabela é válida; erros em uma tabela existente não são ocultados."""
    if not (Path(pasta) / "tabela.py").is_file():
        return None
    return importlib.import_module(str(pasta).replace("/", ".") + ".tabela")


def carregar_cursos(raiz="cursos", existentes=None):
    cursos = dict(CURSOS_EXISTENTES if existentes is None else existentes)
    for arquivo in sorted(Path(raiz).glob("*/curso.json")):
        with arquivo.open(encoding="utf-8") as f:
            dados = json.load(f)
        if not isinstance(dados, dict) or any(
            not isinstance(dados.get(campo), str) or not dados[campo].strip()
            for campo in ("nome", "campus", "versao")
        ):
            raise ValueError(f"Preencha nome, campus e versao em {arquivo}.")
        curso_id = arquivo.parent.name
        if curso_id in cursos:
            raise ValueError(f"Identificador de curso duplicado: {curso_id}.")
        pdf = Path(dados.get("arquivo_pdf", arquivo.parent / "ppc.pdf"))
        if not pdf.is_file():
            raise ValueError(f"PDF não encontrado para {arquivo}: {pdf}.")
        nome = f"{dados['nome'].strip()} — {dados['campus'].strip()} — {dados['versao'].strip()}"
        if any(info['nome'] == nome for info in cursos.values()):
            raise ValueError(f"Curso, campus e versão já cadastrados: {nome}.")
        cursos[curso_id] = {
            "nome": nome, "pasta": str(arquivo.parent),
            "campus": dados['campus'].strip(), "versao": dados['versao'].strip(),
            "arquivo_pdf": str(pdf),
            "pdf_sha256": dados.get("pdf_sha256"),
            "observacoes": dados.get("observacoes", ""),
            "requer_ocr": dados.get("requer_ocr", False),
        }
    return cursos


CURSOS = carregar_cursos()
