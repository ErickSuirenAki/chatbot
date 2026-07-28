import os #arquivos e pastas
import shutil #apagar o banco antigo
from docling.document_converter import DocumentConverter, PdfFormatOption #lê o pdf
from docling.datamodel.base_models import InputFormat #saber que tipo de arquivo
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorDevice #escolhe como docling processa o pdf se é cpu ou gpu
from langchain_huggingface import HuggingFaceEmbeddings #texto em vetores
from langchain_chroma import Chroma #banco vetorial (texto e as embeeddings)
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter # divide texto grande

# Importa os documentos estruturados da matriz curricular
from Tabela import tabelas_para_documents, MATRIZ_CURRICULAR, ELETIVAS #importa do arquivo tabela.py

FILE_PATH = "ppc_computacao.pdf" #o ppc que vai ser processado 
CHROMA_PATH = "./chroma_db" #onde vai ser salvo

def gerar_docs_descritivos(): #embeddings entedem melhro linguagemnatural do que tabelas
    from langchain_core.documents import Document

    nomes_periodos = {
        1: "primeiro",  2: "segundo",  3: "terceiro", 4: "quarto",
        5: "quinto",    6: "sexto",    7: "sétimo",   8: "oitavo",
    }

    docs = []

    #disciplinas obrigatórias
    for periodo, disciplinas in MATRIZ_CURRICULAR.items():
        nome_periodo = nomes_periodos[periodo]
        for d in disciplinas:
            prereqs = d["prereq"]

            #monta a frase de pré-requisitos de forma natural
            if not prereqs:
                frase_pre = "Não tem pré-requisitos"
            elif len(prereqs) == 1:
                frase_pre = f"O pré-requisito é {prereqs[0]}"
            else:
                frase_pre = f"Os pré-requisitos são {', '.join(prereqs[:-1])} e {prereqs[-1]}"

            #monta a frase de carga horária
            if d["apcc"] > 0:
                frase_ch = (
                    f"Tem {d['cr']} créditos e carga horária total de {d['total']} horas "
                    f"({d['ch']}h teóricas + {d['apcc']}h de APCC)"
                )
            else:
                frase_ch = (
                    f"Tem {d['cr']} créditos e carga horária de {d['total']} horas"
                )

            texto = (
                f"A disciplina {d['disciplina']} é obrigatória no {nome_periodo} período "
                f"do curso de Ciência da Computação. "
                f"{frase_ch}. "
                f"{frase_pre}."
            )

            docs.append(Document(
                page_content=texto,
                metadata={
                    "tipo":       "descritivo_disciplina",
                    "periodo":    periodo,
                    "disciplina": d["disciplina"],
                    "source":     "Tabela.py",
                }
            ))

    #Disciplinas eletivas
    for d in ELETIVAS:
        prereqs = d["prereq"]

        if not prereqs:
            frase_pre = "Não tem pré-requisitos"
        elif len(prereqs) == 1:
            frase_pre = f"O pré-requisito é {prereqs[0]}"
        else:
            frase_pre = f"Os pré-requisitos são {', '.join(prereqs[:-1])} e {prereqs[-1]}"

        if d["apcc"] > 0:
            frase_ch = (
                f"Tem {d['cr']} créditos e carga horária total de {d['total']} horas "
                f"({d['ch']}h teóricas + {d['apcc']}h de APCC)"
            )
        else:
            frase_ch = (
                f"Tem {d['cr']} créditos e carga horária de {d['total']} horas"
            )

        texto = (
            f"A disciplina {d['disciplina']} é uma disciplina eletiva do curso de "
            f"Ciência da Computação, podendo ser cursada a partir do quinto período. "
            f"{frase_ch}. "
            f"{frase_pre}."
        )

        docs.append(Document(
            page_content=texto,
            metadata={
                "tipo":       "descritivo_eletiva",
                "disciplina": d["disciplina"],
                "source":     "Tabela.py",
            }
        ))

    return docs


def processar_e_salvar(): #converte o pdf
    print("Iniciando conversão do PDF para Markdown...")
    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options.device = AcceleratorDevice.CPU

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )
    result = converter.convert(FILE_PATH) #pega o arquivo pdf           
    md_content = result.document.export_to_markdown()

    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    sections = md_splitter.split_text(md_content)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs_pdf = text_splitter.split_documents(sections)


    docs_descritivos = gerar_docs_descritivos()
    print(f"  → {len(docs_descritivos)} textos descritivos de disciplinas gerados")

    docs_tabulares = tabelas_para_documents()
    print(f"  → {len(docs_tabulares)} documentos tabulares do Tabela.py gerados")

    todos_os_docs = docs_pdf + docs_descritivos + docs_tabulares
    print(f"\nTotal de fragmentos a indexar: {len(todos_os_docs)}")
    print(f"  • Do PDF (Docling):       {len(docs_pdf)}")
    print(f"  • Descritivos (Abord. 2): {len(docs_descritivos)}")
    print(f"  • Tabulares (Tabela.py):  {len(docs_tabulares)}")

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH) # apaga o banco antigo se tiver

    print("\nCriando banco de vetores...")
    Chroma.from_documents(todos_os_docs, embeddings, persist_directory=CHROMA_PATH) #salva tudo no banco
    print("Banco de dados criado com sucesso!")


if __name__ == "__main__":
    processar_e_salvar()
