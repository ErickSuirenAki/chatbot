import re
import unicodedata
import streamlit as st
import requests

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings



OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"


st.set_page_config(page_title="Assistente PPC - UNIR", page_icon="🎓")
st.title("🎓 Assistente de Cursos — UNIR ")

CHROMA_PATH = "./chroma_db"


@st.cache_resource
def carregar_banco():
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 5})
    return db, retriever

db, retriever = carregar_banco()


def get_memoria(limit=6):
    msgs = st.session_state.get("messages", [])
    return msgs[-limit:]

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
        stream=True
    )

    full_text = ""

    for line in response.iter_lines():
        if line:
            try:
                token = line.decode("utf-8")
                if '"response":"' in token:
                    part = token.split('"response":"')[1].split('"')[0]
                    full_text += part
                    yield part
            except:
                pass

    return full_text



def responder(pergunta):
    docs = retriever.invoke(pergunta)

    contexto = "\n\n".join([d.page_content for d in docs])

    historico = montar_historico()

    prompt = f"""
Você é um assistente da UNIR especializado no PPC de Ciência da Computação.

Use o histórico da conversa para entender o contexto.

Se a informação não estiver no contexto, diga: "Não encontrei essa informação no PPC."

=== HISTÓRICO ===
{historico}

=== CONTEXTO PPC ===
{contexto}

Pergunta atual:
{pergunta}

Resposta clara e natural:
"""

    return prompt



if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("Pergunte sobre o PPC..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        prompt_final = responder(prompt)

        for chunk in gerar_stream(prompt_final):
            full_response += chunk
            placeholder.markdown(full_response)

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )