"""Conversas separadas por curso dentro de cada sessão.

A interface mantém este dicionário em session_state. Leitura e gravação em
JSON são opcionais e exigem um caminho explícito; não há arquivo global
carregado automaticamente. A persistência opcional usa substituição atômica.
"""

from __future__ import annotations

import json
import os
import uuid
import tempfile
from pathlib import Path


def carregar_todas_conversas(caminho: str | None = None) -> dict:
    """Importação explícita. A interface não carrega histórico compartilhado."""
    if caminho is None:
        return {}
    arquivo = Path(caminho)
    if not arquivo.exists():
        return {}
    with arquivo.open(encoding="utf-8") as f:
        dados = json.load(f)
    if not isinstance(dados, dict):
        raise ValueError("Histórico deve ser um objeto JSON.")
    return dados


def salvar_todas_conversas(todas_conversas: dict, caminho: str | None = None) -> None:
    """Por padrão o histórico fica na sessão. Exportação em disco é explícita e atômica."""
    if caminho is None:
        return
    arquivo = Path(caminho)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    fd, temporario = tempfile.mkstemp(prefix=".historico-", dir=arquivo.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(todas_conversas, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporario, arquivo)
    finally:
        if os.path.exists(temporario):
            os.unlink(temporario)


def conversas_do_curso(todas_conversas: dict, curso_id: str) -> dict:
    """Garante que o curso tenha uma entrada no dicionário e a retorna."""
    return todas_conversas.setdefault(curso_id, {})


def criar_nova_conversa(todas_conversas: dict, curso_id: str) -> str:
    """Cria uma conversa vazia para o curso informado e devolve o novo id."""
    conversas = conversas_do_curso(todas_conversas, curso_id)
    novo_id = str(uuid.uuid4())[:8]
    conversas[novo_id] = {
        "titulo": f"Conversa {len(conversas) + 1}",
        "mensagens": [],
    }
    salvar_todas_conversas(todas_conversas)
    return novo_id


def deletar_conversa(todas_conversas: dict, curso_id: str, conv_id: str) -> str | None:
    """Remove a conversa e devolve o id de outra conversa para assumir como
    ativa (ou None se não sobrou nenhuma — quem chamar deve criar uma nova)."""
    conversas = conversas_do_curso(todas_conversas, curso_id)
    if conv_id in conversas:
        del conversas[conv_id]
        salvar_todas_conversas(todas_conversas)

    if conversas:
        return list(conversas.keys())[0]
    return None


def definir_titulo_automatico(conversa: dict, primeira_mensagem: str) -> None:
    """Usa o começo da primeira pergunta do usuário como título da conversa,
    igual ao protótipo da colega — só roda se ainda não houver mensagens."""
    if not conversa["mensagens"]:
        conversa["titulo"] = (
            primeira_mensagem[:25] + ("..." if len(primeira_mensagem) > 25 else "")
        )