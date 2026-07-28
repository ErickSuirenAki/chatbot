# 🎓 Chatbot de PPCs — UNIR (multi-curso, Ollama local)

Assistente virtual para consulta a Projetos Pedagógicos de Curso (PPCs) da Universidade Federal de Rondônia (UNIR), usando arquitetura **RAG** (*Retrieval-Augmented Generation*) com modelo de linguagem rodando **100% localmente** via [Ollama](https://ollama.com/).

Suporta **múltiplos cursos ao mesmo tempo** no mesmo chatbot — atualmente:
* Ciência da Computação
* Pedagogia — Licenciatura

---

## O que ele faz

Permite consultar informações do PPC de um curso (disciplinas, pré-requisitos, carga horária, matriz curricular, eletivas etc.) em linguagem natural, por meio de um chat web feito com Streamlit. O usuário escolhe o curso desejado num seletor, e o chatbot responde apenas com base no PPC daquele curso.

O fluxo é:

1. Cada PDF de PPC é convertido em texto estruturado (Docling) e combinado com a matriz curricular escrita manualmente em Python, específica de cada curso.
2. Todo esse conteúdo é transformado em vetores (embeddings) e salvo em **um único banco vetorial** (ChromaDB), com cada trecho marcado com o metadado `curso`.
3. Quando o usuário pergunta algo, o sistema busca os trechos mais relevantes **filtrando pelo curso selecionado** e monta um prompt com esse contexto.
4. O prompt é enviado a um modelo de linguagem (Llama 3.1) rodando localmente via Ollama, que gera a resposta em streaming.

---

## Tecnologias utilizadas

| Componente         | Tecnologia                | Função                                                        |
| -------------------- | --------------------------- | ---------------------------------------------------------------- |
| Extração de PDF       | Docling (IBM)                | Converte o PPC em texto estruturado, preservando tabelas         |
| Dados estruturados    | `cursos/<curso>/tabela.py`    | Matriz curricular e eletivas de cada curso, escritas manualmente |
| Embeddings            | BAAI/bge-m3 (HuggingFace)     | Representação vetorial semântica dos textos                      |
| Banco Vetorial        | ChromaDB                      | Armazenamento e busca dos trechos relevantes, filtrável por curso |
| LLM                   | Llama 3.1 via Ollama          | Geração de respostas em linguagem natural, 100% local             |
| Interface Web         | Streamlit                     | Interface de chat, com seletor de curso                          |
| Framework de IA       | LangChain                     | Integração entre recuperação (retriever) e o banco Chroma         |

---

## Estrutura do projeto

```text
├── cursos/
│   ├── ciencia_computacao/
│   │   ├── ppc.pdf         # PDF do PPC do curso
│   │   └── tabela.py       # matriz curricular e eletivas do curso
│   └── pedagogia/
│       ├── ppc.pdf
│       └── tabela.py
├── cursos_config.py        # registro central: quais cursos existem
├── tabela_utils.py         # lógica compartilhada entre todos os cursos
├── processar_pdf.py        # gera o banco vetorial (chroma_db) a partir de todos os cursos
├── appOllamaLocal.py       # interface de chat (Streamlit), com seletor de curso
├── chroma_db/               # banco vetorial gerado (não vai pro Git)
├── .gitignore
└── README.md
```

> Cada curso é independente em `cursos/<id>/`. Adicionar um curso novo não exige mexer em nenhum outro arquivo além de `cursos_config.py` (veja a seção "Como adicionar um novo curso").

---

## Como executar localmente

### Pré-requisitos

* Python 3.10 ou superior
* Git
* [Ollama](https://ollama.com/download) instalado na máquina

### 1. Clonar o repositório

```bash
git clone git@github.com:ErickSuirenAki/chatbot.git
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

Deixe o serviço do Ollama rodando (normalmente sobe automaticamente após a instalação, escutando em `http://localhost:11434`).

### 5. Gerar o banco vetorial a partir dos PPCs

Este passo lê **todos os cursos cadastrados em `cursos_config.py`**, processa os PDFs e as matrizes curriculares, gera os embeddings e cria a pasta `chroma_db/`. É necessário rodar **uma vez antes da primeira execução do chat**, e sempre que algum PDF ou `tabela.py` for atualizado:

```bash
python processar_pdf.py
```

⚠️ Esse processo é pesado (OCR + embeddings) e pode consumir bastante RAM. Se sua máquina tiver pouca memória (8 GB ou menos), feche outros programas pesados (incluindo o próprio Ollama) enquanto ele roda, para evitar que o sistema operacional finalize o processo por falta de memória (OOM killer).

### 6. Executar o chatbot

```bash
streamlit run appOllamaLocal.py
```

O Streamlit abre automaticamente uma aba no navegador (geralmente em `http://localhost:8501`). Escolha o curso desejado no seletor no topo da página.

---

## Como funciona por dentro

### `cursos_config.py`
Lista central de todos os cursos disponíveis no sistema, mapeando um `id` curto (ex: `pedagogia`) para o nome legível do curso e a pasta onde estão seus arquivos.

### `cursos/<curso>/tabela.py`
Contém a matriz curricular completa (por período/semestre) e a lista de disciplinas eletivas de **um** curso, escritas manualmente como dicionários Python. Cada disciplina tem nome, pré-requisitos, créditos e carga horária.

> Nem todo PPC segue o mesmo padrão: por exemplo, o curso de Pedagogia não define pré-requisitos formais entre disciplinas (organização por eixos, não por dependência), então nesse curso o campo `prereq` fica sempre vazio.

### `tabela_utils.py`
Módulo compartilhado por todos os cursos. Transforma os dicionários de `tabela.py` em `Document`s do LangChain — tanto em formato de tabela (visão geral por período) quanto em fichas individuais por disciplina, além de gerar textos descritivos em linguagem natural (que ajudam a busca semântica a encontrar a disciplina certa mesmo quando a pergunta não usa o vocabulário exato da tabela). **Todo documento gerado aqui recebe `metadata["curso"]`**, que é a peça-chave que permite filtrar a busca por curso depois.

### `processar_pdf.py`
1. Percorre todos os cursos cadastrados em `cursos_config.py`.
2. Para cada curso, usa o **Docling** para converter o `ppc.pdf` em Markdown, preservando tabelas, e divide esse conteúdo em pedaços menores (chunks).
3. Junta os chunks do PDF com os documentos gerados por `tabela_utils.py` (tabelas + fichas + descritivos), todos marcados com o metadado do curso correspondente.
4. Gera os embeddings de tudo com o modelo `BAAI/bge-m3` e salva num **único** banco vetorial ChromaDB, na pasta `chroma_db/`.

### `appOllamaLocal.py`
1. Carrega o banco vetorial (`chroma_db/`).
2. Mostra um seletor para o usuário escolher o curso. Ao trocar de curso, o histórico da conversa é reiniciado.
3. Configura um retriever que busca os trechos mais relevantes **filtrando pelo curso selecionado** (`filter={"curso": curso_id}`), evitando misturar informações de cursos diferentes.
4. Monta um prompt com instruções restritivas (responder somente com base no contexto recuperado, sem completar com conhecimento próprio), o histórico recente da conversa, o contexto e a pergunta atual.
5. Envia esse prompt para o Ollama (`http://localhost:11434/api/generate`, modelo `llama3.1`) em modo *streaming*, exibindo a resposta token a token.
6. Tem um modo de depuração opcional (checkbox "🔍 Mostrar contexto recuperado") que exibe os trechos que o retriever encontrou antes de gerar a resposta — útil para diagnosticar se um erro é de busca (trecho certo não foi encontrado) ou de geração (modelo ignorou o contexto correto).

---

## Como adicionar um novo curso

1. Criar a pasta `cursos/<id_do_curso>/`.
2. Colocar o PDF do PPC dentro, nomeado `ppc.pdf`.
3. Criar `cursos/<id_do_curso>/tabela.py` com `MATRIZ_CURRICULAR` e `ELETIVAS`, seguindo o mesmo formato dos cursos existentes (use `cursos/pedagogia/tabela.py` como modelo).
4. Adicionar uma entrada em `cursos_config.py`.
5. Rodar `python processar_pdf.py` novamente para reindexar tudo.

Nenhum outro arquivo precisa ser alterado.

---

## Exemplos de perguntas

* "Quais são os pré-requisitos de Banco de Dados I?"
* "Qual a carga horária de Programação Orientada a Objetos?"
* "Em que período é ofertada Didática?"
* "Quais disciplinas fazem parte do 5º período?"
* "Quais são as disciplinas eletivas do curso?"

---

## Solução de problemas

* **Erro de conexão com o Ollama** (`ConnectionError`): verifique se o Ollama está instalado e rodando (`ollama list` deve funcionar no terminal).
* **Modelo não encontrado**: rode `ollama pull llama3.1` novamente.
* **Pasta `chroma_db` não existe / respostas vazias**: rode `python processar_pdf.py` antes de iniciar o Streamlit.
* **`processar_pdf.py` trava ou o processo é encerrado sozinho**: provavelmente falta de memória RAM (o sistema operacional finaliza o processo). Rode fora do VS Code, direto no terminal, feche programas pesados durante o processamento e monitore com `free -h`.
* **O modelo responde algo que não está no PPC (alucinação)**: ative o modo debug no app para conferir se o trecho certo foi recuperado. Se sim, é o modelo ignorando o contexto — o prompt já inclui instruções restritivas contra isso, mas modelos locais menores erram mais que modelos maiores.
* **Erro ao instalar `docling` ou `sentence-transformers`**: essas bibliotecas podem exigir mais RAM/tempo na primeira instalação; confira se seu Python é 3.10+.

---

## Limitações atuais

* A qualidade das respostas depende da recuperação correta dos trechos relevantes e da capacidade do modelo local de seguir instruções sem alucinar.
* Não possui memória persistente entre sessões (o histórico se perde ao fechar o navegador, e também é resetado ao trocar de curso).
* Depende do Ollama estar rodando localmente; não funciona sem ele.
* O curso é escolhido manualmente pelo usuário num seletor — o chat não tenta detectar automaticamente de qual curso a pergunta se trata.
* Não substitui a consulta oficial ao PPC.

---

## Segurança

Nunca versionar chaves de API, senhas ou tokens diretamente no código. Use variáveis de ambiente (arquivo `.env`, ignorado pelo Git) para qualquer credencial, caso o projeto volte a usar uma API externa (como Groq) no futuro.

---

## Objetivo do projeto

Projeto desenvolvido com fins acadêmicos e de pesquisa, explorando técnicas de Recuperação de Informação, Embeddings, Bancos Vetoriais, Modelos de Linguagem (LLMs) e arquitetura RAG aplicadas ao contexto educacional, rodando de forma totalmente local com Ollama e suportando múltiplos cursos simultaneamente.