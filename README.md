# 🎓 Chatbot PPC — UNIR

Assistente virtual para consulta aos Projetos Pedagógicos de Curso (PPCs) da Universidade Federal de Rondônia.

🔗 **Acesse o chatbot:** [chatbot-ppc.streamlit.app](https://chatbot-ppc.streamlit.app/)

---

## O que ele faz

Permite que alunos e interessados consultem informações dos cursos da UNIR de forma natural, sem precisar procurar manualmente nos PDFs dos PPCs.

**Exemplos de perguntas:**
- *"Quais são os pré-requisitos de Banco de Dados I?"*
- *"Qual a carga horária de Programação I?"*
- *"Quais disciplinas tem no 5º período?"*
- *"Quais são as disciplinas eletivas?"*
- *"Qual o objetivo do curso?"*

---

## Tecnologias utilizadas

| Componente | Tecnologia | Função |
|---|---|---|
| Extração de PDF | Docling (IBM) | Converte PDF para Markdown preservando tabelas |
| Embedding | BAAI/bge-m3 | Converte texto em vetores semânticos |
| Banco de vetores | ChromaDB | Armazena e busca os vetores por similaridade |
| Interface web | Streamlit | Interface de chat no navegador |
| Orquestração | LangChain | Conecta os componentes do pipeline |

---

## Arquitetura

O sistema usa a arquitetura **RAG (Retrieval-Augmented Generation)** — em vez de treinar um modelo com os dados do PPC, o sistema busca em tempo real as informações relevantes e as devolve ao usuário.

```
Pergunta do usuário
       ↓
  BGE-M3 converte para vetor
       ↓
  ChromaDB busca chunks similares
       ↓
  Lógica de prioridade seleciona a melhor resposta
       ↓
  Resposta exibida no chat
```

### Lógica de prioridade

1. Se a pergunta menciona um período → retorna a tabela completa do período
2. Se a pergunta é sobre eletivas/optativas → retorna a tabela de eletivas
3. Se a pergunta é sobre uma disciplina específica → retorna o texto descritivo da disciplina
4. Caso geral → retorna o trecho mais relevante do PDF

---

## Estrutura do projeto

```
├── app.py              # Interface web (Streamlit)
├── pdf_processor.py    # Ingestão: PDF + Tabela.py → ChromaDB
├── Tabela.py           # Matriz curricular estruturada em Python
├── requirements.txt    # Dependências
└── chroma_db/          # Banco de vetores gerado
```

---

## Como rodar localmente

**Pré-requisitos:** Python 3.12, Linux recomendado

```bash
# 1. Clone o repositório
git clone https://github.com/ErickSuirenAki/chatbot.git
cd chatbot

# 2. Crie o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Gere o banco de vetores (necessário apenas uma vez)
python pdf_processor.py

# 5. Rode o chatbot
streamlit run app.py
```

---

## Limitações atuais

- Cobre apenas o curso de **Ciência da Computação** por enquanto
- Perguntas que exigem agregar múltiplas informações (ex: *"quais disciplinas não têm pré-requisito?"*) retornam resultado parcial
- Perguntas interpretativas dependem da qualidade da extração do PDF

