import streamlit as st
import requests
import json
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from cursos_config import CURSOS
from historico import (
    carregar_todas_conversas,
    salvar_todas_conversas,
    conversas_do_curso,
    criar_nova_conversa,
    deletar_conversa,
    definir_titulo_automatico,
)
from resposta_estruturada import BaseDisciplinas, responder_estruturado


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"

st.set_page_config(page_title="Assistente de Cursos - UNIR", page_icon=":material/school:", layout="wide")

CHROMA_PATH = "./chroma_db"


@st.cache_resource(show_spinner="Carregando base de conhecimento dos cursos...")
def carregar_banco():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3", model_kwargs={"device": "cpu"}, encode_kwargs={"normalize_embeddings": True})
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    base = BaseDisciplinas.carregar(db)
    return db, base


db, base = carregar_banco()


# ─────────────────────────────────────────────────────────────────
# Seletor de curso
# ─────────────────────────────────────────────────────────────────
nomes_cursos = {info["nome"]: curso_id for curso_id, info in CURSOS.items()}
nome_selecionado = st.sidebar.selectbox(":material/menu_book: Curso", list(nomes_cursos.keys()))
curso_atual = nomes_cursos[nome_selecionado]

if st.session_state.get("curso_atual") != curso_atual:
    st.session_state.curso_atual = curso_atual
    st.session_state.pop("conversa_ativa_id", None)  # troca de curso = troca de espaço de conversas


# ─────────────────────────────────────────────────────────────────
# Histórico de conversas (multi-conversa persistida, por curso)
# ─────────────────────────────────────────────────────────────────
if "todas_conversas" not in st.session_state:
    st.session_state.todas_conversas = carregar_todas_conversas()

conversas_curso = conversas_do_curso(st.session_state.todas_conversas, curso_atual)

if "conversa_ativa_id" not in st.session_state or st.session_state.conversa_ativa_id not in conversas_curso:
    if conversas_curso:
        st.session_state.conversa_ativa_id = list(conversas_curso.keys())[0]
    else:
        st.session_state.conversa_ativa_id = criar_nova_conversa(st.session_state.todas_conversas, curso_atual)

st.sidebar.markdown("---")
st.sidebar.subheader(":material/chat: Conversas")

if st.sidebar.button(":material/add: Nova conversa", use_container_width=True):
    st.session_state.conversa_ativa_id = criar_nova_conversa(st.session_state.todas_conversas, curso_atual)
    st.rerun()

conversas_curso = conversas_do_curso(st.session_state.todas_conversas, curso_atual)
lista_ids = list(conversas_curso.keys())
if lista_ids:
    def formatar_titulo(cid):
        return conversas_curso[cid].get("titulo", f"Conversa {cid}")

    index_atual = lista_ids.index(st.session_state.conversa_ativa_id) if st.session_state.conversa_ativa_id in lista_ids else 0
    conversa_selecionada = st.sidebar.radio(":material/history: Histórico:", options=lista_ids, format_func=formatar_titulo, index=index_atual, label_visibility="collapsed")
    st.session_state.conversa_ativa_id = conversa_selecionada

if st.sidebar.button(":material/delete: Excluir conversa atual", use_container_width=True):
    novo_ativo = deletar_conversa(st.session_state.todas_conversas, curso_atual, st.session_state.conversa_ativa_id)
    if novo_ativo is None:
        novo_ativo = criar_nova_conversa(st.session_state.todas_conversas, curso_atual)
    st.session_state.conversa_ativa_id = novo_ativo
    st.rerun()

conversa_atual = conversas_do_curso(st.session_state.todas_conversas, curso_atual)[st.session_state.conversa_ativa_id]
mensagens = conversa_atual["mensagens"]


# ─────────────────────────────────────────────────────────────────
# RAG: retriever filtrado por curso + geração de resposta
# ─────────────────────────────────────────────────────────────────
def retriever_do_curso(curso_id: str):
    return db.as_retriever(search_kwargs={"k": 5, "filter": {"curso": curso_id}})


def get_memoria(limit=6):
    return mensagens[-limit:]


def montar_historico():
    historico = ""
    for m in get_memoria():
        role = "Usuário" if m["role"] == "user" else "Assistente"
        historico += f"{role}: {m['content']}\n"
    return historico


def gerar_stream(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": True
        },
        stream=True,
    )

    response.raise_for_status()

    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))

                if "response" in data:
                    yield data["response"]

            except json.JSONDecodeError:
                continue


def montar_prompt_llm(pergunta, curso_id, curso_nome):
    retriever = retriever_do_curso(curso_id)
    docs = retriever.invoke(pergunta)

    contexto = "\n\n".join([d.page_content for d in docs])
    historico = montar_historico()

    return f"""
Você é um mentor acadêmico da UNIR, especializado no PPC do curso de {curso_nome} — atencioso, direto e humano, como um professor experiente conversando com o aluno.

Use o histórico da conversa para entender o contexto.

Responda apenas com base no contexto do PPC de {curso_nome} fornecido abaixo. Evite frases robóticas como "de acordo com o documento" ou "segundo o contexto fornecido" — fale de forma natural.
Se a informação não estiver no contexto, diga de forma simples que não encontrou esse detalhe no PPC de {curso_nome} — nunca invente números de carga horária, créditos ou pré-requisitos.

=== HISTÓRICO ===
{historico}

=== CONTEXTO PPC — {curso_nome} ===
{contexto}

Pergunta atual:
{pergunta}

Resposta clara e natural:
"""


# ─────────────────────────────────────────────────────────────────
# Interface principal
# ─────────────────────────────────────────────────────────────────
st.title(":material/school: Assistente de Cursos — UNIR")
st.caption(f"Curso ativo: **{nome_selecionado}**")

for msg in mensagens:
    if msg["role"] == "user":
        avatar = ":material/person:"
    else:
        avatar = ":material/school:"

    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input(f"Pergunte sobre o PPC de {nome_selecionado}..."):
    definir_titulo_automatico(conversa_atual, prompt)

    mensagens.append({"role": "user", "content": prompt})
    salvar_todas_conversas(st.session_state.todas_conversas)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=":material/school:"):
        # 1) tenta resposta determinística por metadados (rápida, exata,
        #    sem custo de LLM e sem risco de alucinação de números)
        resposta_direta = responder_estruturado(prompt, base, curso_atual)

        if resposta_direta is not None:
            st.markdown(resposta_direta)
            full_response = resposta_direta
        else:
            # 2) fallback: RAG semântico + LLM local via Ollama, com streaming
            placeholder = st.empty()
            full_response = ""
            prompt_final = montar_prompt_llm(prompt, curso_atual, nome_selecionado)
            for chunk in gerar_stream(prompt_final):
                full_response += chunk
                placeholder.markdown(full_response)

    mensagens.append({"role": "assistant", "content": full_response})
    salvar_todas_conversas(st.session_state.todas_conversas)