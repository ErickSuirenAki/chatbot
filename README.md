# 🎓 Chatbot PPC — UNIR 

Assistente virtual para consulta ao Projeto Pedagógico de Curso (PPC) de Ciência da Computação da Universidade Federal de Rondônia (UNIR), usando arquitetura **RAG** (*Retrieval-Augmented Generation*) com modelo de linguagem rodando **100% localmente** via [Ollama](https://ollama.com/).

---

## O que ele faz

Permite consultar informações do PPC (disciplinas, pré-requisitos, carga horária, matriz curricular, eletivas etc.) em linguagem natural, por meio de um chat web feito com Streamlit.

O fluxo é:

1. O PDF do PPC é convertido em texto estruturado (Docling) e combinado com tabelas da matriz curricular escritas manualmente em Python.
2. Esse conteúdo é transformado em vetores (embeddings) e salvo em um banco vetorial (ChromaDB).
3. Quando o usuário faz uma pergunta, o sistema busca os trechos mais relevantes no banco vetorial e monta um prompt com esse contexto.
4. O prompt é enviado para um modelo de linguagem (Llama 3.1) rodando localmente via Ollama, que gera a resposta em streaming.

---

## Tecnologias utilizadas

| Componente        | Tecnologia                 | Função                                                       |
| ------------------ | --------------------------- | -------------------------------------------------------------- |
| Extração de PDF     | Docling (IBM)                | Converte o PPC em texto estruturado, preservando tabelas       |
| Dados estruturados  | `Tabela.py`                   | Matriz curricular e eletivas escritas manualmente em Python    |
| Embeddings          | BAAI/bge-m3 (HuggingFace)     | Representação vetorial semântica dos textos                    |
| Banco Vetorial      | ChromaDB                      | Armazenamento e busca dos trechos relevantes                   |
| LLM                 | Llama 3.1 via Ollama          | Geração de respostas em linguagem natural, 100% local          |
| Interface Web       | Streamlit                     | Interface de chat no navegador                                 |
| Framework de IA     | LangChain                     | Integração entre recuperação (retriever) e o banco Chroma      |

---

## Estrutura do projeto

```text
├── appOllamaLocal.py    # Interface de chat (Streamlit) que conversa com o Ollama
├── processar_pdf.py     # Lê o PDF, gera os embeddings e cria o banco vetorial (chroma_db)
├── Tabela.py             # Matriz curricular e disciplinas eletivas em formato de dados
├── ppc_computacao.pdf    # PDF do PPC usado como fonte de dados
├── chroma_db/             # Banco vetorial gerado (criado automaticamente, não vai pro Git)
├── .gitignore
└── README.md
```

> **Observação:** o projeto ainda não possui um arquivo `requirements.txt`. A seção de instalação abaixo lista as dependências a instalar manualmente. Veja "Próximos passos" ao final para uma sugestão de melhoria.

---

## Como executar localmente

### Pré-requisitos

* Python 3.10 ou superior
* Git
* [Ollama](https://ollama.com/download) instalado na máquina

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/chatbot.git
cd chatbot
```

### 2. Criar e ativar um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Instalar as dependências

```bash
pip install streamlit requests langchain langchain-chroma langchain-huggingface langchain-text-splitters langchain-core docling sentence-transformers
```

### 4. Instalar e preparar o Ollama

Baixe e instale o Ollama em https://ollama.com/download, depois baixe o modelo usado pelo projeto:

```bash
ollama pull llama3.1
```

Deixe o serviço do Ollama rodando (normalmente ele sobe automaticamente após a instalação, escutando em `http://localhost:11434`).

### 5. Gerar o banco vetorial a partir do PDF

Esse passo lê `ppc_computacao.pdf`, extrai o conteúdo, gera os embeddings e cria a pasta `chroma_db/`. Precisa ser executado **uma vez antes da primeira execução do chat**, e sempre que o PDF ou o `Tabela.py` forem atualizados:

```bash
python processar_pdf.py
```

### 6. Executar o chatbot

```bash
streamlit run appOllamaLocal.py
```

O Streamlit abre automaticamente uma aba no navegador (geralmente em `http://localhost:8501`).

---

## Como funciona por dentro

### `Tabela.py`
Contém a matriz curricular completa (8 períodos) e a lista de disciplinas eletivas, escritas manualmente como dicionários Python. A função `tabelas_para_documents()` transforma esses dados em objetos `Document` do LangChain, tanto em formato de tabela (visão geral por período/eletivas) quanto em formato individual (uma disciplina por documento), facilitando buscas gerais e específicas.

### `processar_pdf.py`
1. Usa o **Docling** para converter `ppc_computacao.pdf` em Markdown, preservando tabelas.
2. Divide esse Markdown em pedaços menores (chunks), primeiro por cabeçalhos e depois por tamanho de caractere.
3. Gera textos descritivos em linguagem natural para cada disciplina (ex: "A disciplina Programação I é obrigatória no primeiro período... Tem 6 créditos...").
4. Junta tudo (chunks do PDF + textos descritivos + tabelas do `Tabela.py`) e gera os embeddings com o modelo `BAAI/bge-m3`.
5. Salva tudo no banco vetorial ChromaDB, na pasta `chroma_db/`.

### `appOllamaLocal.py`
1. Carrega o banco vetorial (`chroma_db/`) e configura um retriever que busca os 5 trechos mais relevantes para cada pergunta.
2. Mantém o histórico da conversa na sessão do Streamlit (`st.session_state`).
3. A cada pergunta do usuário, monta um prompt contendo: instruções para o modelo, o histórico recente da conversa, o contexto recuperado do banco vetorial e a pergunta atual.
4. Envia esse prompt para o Ollama (`http://localhost:11434/api/generate`, modelo `llama3.1`) em modo *streaming*, exibindo a resposta token a token na tela.

---

## Exemplos de perguntas

* "Quais são os pré-requisitos de Banco de Dados I?"
* "Qual a carga horária de Programação I?"
* "Em que período é ofertada Inteligência Artificial?"
* "Quais disciplinas fazem parte do 5º período?"
* "Quais são as disciplinas eletivas do curso?"

---

## Solução de problemas

* **Erro de conexão com o Ollama** (`ConnectionError`): verifique se o Ollama está instalado e rodando (`ollama list` deve funcionar no terminal).
* **Modelo não encontrado**: rode `ollama pull llama3.1` novamente.
* **Pasta `chroma_db` não existe / respostas vazias**: rode `python processar_pdf.py` antes de iniciar o Streamlit.
* **Erro ao instalar `docling` ou `sentence-transformers`**: essas bibliotecas podem exigir mais RAM/tempo na primeira instalação; confira se seu Python é 3.10+.

---

## Limitações atuais

* Cobre apenas o curso de Ciência da Computação — UNIR.
* A qualidade das respostas depende da recuperação correta dos trechos relevantes.
* Não possui memória persistente entre sessões (o histórico se perde ao fechar o navegador).
* Depende do Ollama estar rodando localmente; não funciona sem ele.
* Não substitui a consulta oficial ao PPC.

---

## Próximos passos sugeridos

* Criar um `requirements.txt` com as versões exatas das dependências usadas.
* Adicionar um `.env` ou arquivo de configuração para trocar o modelo do Ollama sem editar o código.
* Adicionar testes automatizados para as funções de busca em `Tabela.py`.

---

## Objetivo do projeto

Projeto desenvolvido com fins acadêmicos e de pesquisa, explorando técnicas de Recuperação de Informação, Embeddings, Bancos Vetoriais, Modelos de Linguagem (LLMs) e arquitetura RAG aplicadas ao contexto educacional, rodando de forma totalmente local com Ollama.
