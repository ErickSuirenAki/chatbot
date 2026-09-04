"""
historico.py — Persistência de múltiplas conversas em JSON, por curso
=======================================================================
Ideia trazida do chatbot_ppc (protótipo da colega) e adaptada para a base
multi-curso deste projeto: cada curso tem seu próprio conjunto de
conversas, já que trocar de curso muda completamente o contexto do PPC.

Formato do arquivo (historico_conversas.json):
{
  "ciencia_computacao": {
      "<id>": {"titulo": "...", "mensagens": [{"role": ..., "content": ...}]},
      ...
  },
  "pedagogia": {...}
}
"""

from __future__ import annotations

import json
import os
import uuid

HISTORICO_FILE = "historico_conversas.json"


def carregar_todas_conversas() -> dict:
    """Carrega o dicionário completo {curso_id: {conv_id: conversa}}."""
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def salvar_todas_conversas(todas_conversas: dict) -> None:
    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(todas_conversas, f, ensure_ascii=False, indent=2)


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