# 🎓 Chatbot PPC — UNIR

Assistente virtual para consulta aos Projetos Pedagógicos de Curso (PPCs) da Universidade Federal de Rondônia (UNIR), utilizando arquitetura RAG (*Retrieval-Augmented Generation*) e modelos de linguagem para responder perguntas em linguagem natural.

🔗 **Acesse o chatbot:** https://chatbot-ppc.streamlit.app/

---

## O que ele faz

Permite que alunos, professores e interessados consultem informações dos cursos da UNIR de forma rápida e intuitiva, sem precisar procurar manualmente nos documentos dos PPCs.

O chatbot busca as informações mais relevantes no PPC e gera respostas em linguagem natural, tornando a interação mais próxima de uma conversa humana.

### Exemplos de perguntas

* "Quais são os pré-requisitos de Banco de Dados I?"
* "Qual a carga horária de Programação I?"
* "Em que período é ofertada Inteligência Artificial?"
* "Quais disciplinas fazem parte do 5º período?"
* "Qual a ementa de Estrutura de Dados II?"
* "Quais são as disciplinas eletivas do curso?"

---

## Tecnologias utilizadas

| Componente      | Tecnologia           | Função                                                  |
| --------------- | -------------------- | ------------------------------------------------------- |
| Extração de PDF | Docling (IBM)        | Converte o PPC em texto estruturado preservando tabelas |
| Embeddings      | BAAI/bge-m3          | Representação vetorial semântica dos textos             |
| Banco Vetorial  | ChromaDB             | Armazenamento e recuperação dos trechos relevantes      |
| LLM             | Groq + Llama 3.3 70B | Geração das respostas em linguagem natural              |
| Interface Web   | Streamlit            | Interface de chat acessível pelo navegador              |
| Framework de IA | LangChain            | Integração entre recuperação e geração de respostas     |

---

## Arquitetura

O sistema utiliza a abordagem **RAG (Retrieval-Augmented Generation)**.

Em vez de treinar um modelo com os dados do PPC, o chatbot recupera os trechos mais relevantes do documento e utiliza uma LLM para gerar uma resposta baseada exclusivamente nessas informações.

```text
Pergunta do usuário
       ↓
 Embedding (BGE-M3)
       ↓
 Busca semântica (ChromaDB)
       ↓
 Recuperação dos trechos relevantes
       ↓
 Construção do contexto
       ↓
 LLM (Llama 3.3 via Groq)
       ↓
 Resposta em linguagem natural
       ↓
 Interface Streamlit
```

---

## Estratégia de recuperação

O sistema aplica algumas regras antes de consultar a LLM:

1. Perguntas sobre períodos retornam diretamente a matriz curricular do período solicitado.
2. Perguntas sobre disciplinas eletivas retornam a tabela de eletivas.
3. Perguntas sobre disciplinas específicas priorizam os trechos descritivos da disciplina.
4. Consultas gerais utilizam busca semântica no banco vetorial.
5. O contexto recuperado é enviado à LLM para geração da resposta final.

Essa abordagem reduz alucinações e mantém as respostas alinhadas ao conteúdo do PPC.

---

## Funcionalidades atuais

* Consulta de disciplinas por nome.
* Consulta de pré-requisitos.
* Consulta de carga horária.
* Consulta de ementas.
* Consulta da matriz curricular por período.
* Consulta de disciplinas eletivas.
* Busca semântica utilizando embeddings.
* Respostas em linguagem natural geradas por LLM.
* Histórico de conversa durante a sessão.

---

## Estrutura do projeto

```text
├── app.py                       # Interface Streamlit
├── processar_pdf.py             # Processamento do PPC e criação do banco vetorial
├── Tabela.py                    # Estrutura da matriz curricular
├── requirements.txt             # Dependências do projeto
├── chroma_db/                   # Banco vetorial persistido
├── README.md                    # Documentação
└── 3438_ppc_bcc_1179480801.pdf  # PPC utilizado atualmente
```

---

## Como executar localmente

### Pré-requisitos

* Python 3.12 ou superior
* Git

### 1. Clonar o repositório

```bash
git clone https://github.com/ErickSuirenAki/chatbot.git
cd chatbot
```

### 2. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar a chave da API

Crie o arquivo:

```text
.streamlit/secrets.toml
```

Conteúdo:

```toml
GROQ_API_KEY = "sua_chave_aqui"
```

### 5. Executar a aplicação

```bash
streamlit run app.py
```

---

## Curso atualmente suportado

Atualmente o chatbot está configurado para responder perguntas sobre o curso de:

* Ciência da Computação — UNIR

A arquitetura foi desenvolvida para permitir futura expansão para outros cursos da universidade.

---

## Limitações atuais

* Atualmente cobre apenas um curso.
* A qualidade das respostas depende da recuperação correta dos trechos relevantes.
* Perguntas muito ambíguas podem gerar respostas incompletas.
* Não possui memória persistente entre sessões.
* Não substitui a consulta oficial ao PPC.

---

## Objetivo do projeto

Este projeto foi desenvolvido com fins acadêmicos e de pesquisa, buscando explorar técnicas de Recuperação de Informação, Embeddings, Bancos Vetoriais, Modelos de Linguagem (LLMs) e arquitetura RAG aplicadas ao contexto educacional.

O objetivo é evoluir progressivamente o chatbot para proporcionar uma experiência de consulta cada vez mais próxima de uma conversa natural, mantendo as respostas fundamentadas nos documentos oficiais dos cursos.
