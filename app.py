import re #regex
import unicodedata #acentos
import streamlit as st #interface web
from langchain_chroma import Chroma #abre o banco
from langchain_huggingface import HuggingFaceEmbeddings #modelo embeddings
from langchain_groq import ChatGroq

API_KEY = st.secrets["GROQ_API_KEY"]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=API_KEY,
    temperature=0
)

st.write("Tamanho da chave:", len(API_KEY))
st.write("Primeiros 10 caracteres:", API_KEY[:10])
st.write("Últimos 5 caracteres:", API_KEY[-5:])



#pagina
st.set_page_config(page_title="Assistente PPC - UNIR", page_icon="🎓", layout="centered")
st.title("🎓 Assistente de Cursos — UNIR")
st.markdown("Pergunte sobre disciplinas, cargas horárias, pré-requisitos e muito mais. (atualmente só responde perguntas sobre o Curso de Ciência da Computação)")

CHROMA_PATH = "./chroma_db" #banco

def norm(txt):
    if not txt:
        return ""
    return unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("utf-8").lower()

NUMEROS_PERIODO = {
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
    "primeiro": 1, "segundo": 2, "terceiro": 3, "quarto": 4,
    "quinto": 5, "sexto": 6, "setimo": 7, "oitavo": 8,
}

def detectar_periodo(pergunta):
    q = norm(pergunta)
    match = re.search(r"(\d)[ºo°]", q)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d)\s*per[ií]odo", q)
    if match:
        return int(match.group(1))
    for palavra, num in NUMEROS_PERIODO.items():
        if isinstance(palavra, str) and len(palavra) > 2 and palavra in q:
            return num
    return None

def pergunta_sobre_eletivas(pergunta):
    q = norm(pergunta)
    return "eletiva" in q or "optativa" in q

@st.cache_resource #so carrega o banco uma vez fica mais rapido
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


def buscar_tabela_periodo(periodo):
    resultado = db.get(
        where={"$and": [{"tipo": {"$eq": "tabela_periodo"}}, {"periodo": {"$eq": periodo}}]}
    )
    if resultado and resultado["documents"]:
        return resultado["documents"][0]
    return None

def buscar_tabela_eletivas():
    resultado = db.get(where={"tipo": {"$eq": "tabela_eletivas"}})
    if resultado and resultado["documents"]:
        return resultado["documents"][0]
    return None


def selecionar_melhor_chunk(docs, pergunta):
    pergunta_norm = norm(pergunta)

    for d in docs:
        tipo = d.metadata.get("tipo", "")
        if tipo in ("descritivo_disciplina", "descritivo_eletiva"):
            disciplina = norm(d.metadata.get("disciplina", ""))
            if disciplina and (disciplina in pergunta_norm or
                               any(p in pergunta_norm for p in disciplina.split() if len(p) > 4)):
                return d.page_content

    for d in docs:
        if d.metadata.get("tipo", "") in ("descritivo_disciplina", "descritivo_eletiva"):
            return d.page_content

    for d in docs:
        if d.metadata.get("tipo", "") in ("tabela_periodo", "tabela_eletivas"):
            return d.page_content

    if docs:
        return docs[0].page_content

    return None



def responder(pergunta):
    periodo = detectar_periodo(pergunta)
    if periodo:
        tabela = buscar_tabela_periodo(periodo)
        if tabela:
            return tabela

    if pergunta_sobre_eletivas(pergunta):
        tabela = buscar_tabela_eletivas()
        if tabela:
            return tabela

    docs = retriever.invoke(pergunta)

    if not docs:
        return "Não encontrei informações sobre isso no PPC."

    contexto = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Você é um assistente da UNIR especializado no PPC do curso de Ciência da Computação.

Responda APENAS usando as informações presentes no contexto.

Se a informação não estiver no contexto, responda exatamente:
"Não encontrei essa informação no PPC."

Contexto:
{contexto}

Pergunta:
{pergunta}
"""

    try:
        resposta = llm.invoke(prompt)
        return resposta.content
    except Exception as e:
        return f"Erro ao consultar a LLM: {e}"
    


# Histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caixa de entrada do usuário
if prompt_input := st.chat_input("Como posso ajudar?"):

    st.session_state.messages.append(
        {"role": "user", "content": prompt_input}
    )

    with st.chat_message("user"):
        st.markdown(prompt_input)

    with st.chat_message("assistant"):
        with st.spinner("Consultando PPC..."):
            response = responder(prompt_input)
            st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )