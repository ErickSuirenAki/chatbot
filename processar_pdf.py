import os
import shutil
import importlib
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorDevice
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from cursos_config import CURSOS
from tabela_utils import tabelas_para_documents, gerar_docs_descritivos

CHROMA_PATH = "./chroma_db"  #um banco só, compartilhado por todos os cursos


def processar_pdf_do_curso(curso_id: str, pasta: str):
    caminho_pdf = os.path.join(pasta, "ppc.pdf")
    print(f"  Convertendo PDF ({caminho_pdf})...")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options.device = AcceleratorDevice.CPU

    converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})
    result = converter.convert(caminho_pdf)
    md_content = result.document.export_to_markdown()

    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    sections = md_splitter.split_text(md_content)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs_pdf = text_splitter.split_documents(sections)

    # Adiciona o metadado de curso em cada chunk vindo do PDF
    # Sem isso, o retriever não conseguiria filtrar por curso depois
    for doc in docs_pdf:
        doc.metadata["curso"] = curso_id
        doc.metadata["source"] = caminho_pdf

    print(f"    → {len(docs_pdf)} fragmentos extraídos do PDF")
    return docs_pdf


def processar_e_salvar():
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3",model_kwargs={"device": "cpu"},encode_kwargs={"normalize_embeddings": True})

    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)  # apaga o banco antigo, se existir

    todos_os_docs = []

    # Percorre todos os cursos cadastrados em cursos_config.py
    # Cada curso tem seu próprio tabela.py
    for curso_id, info in CURSOS.items():
        print(f"\n=== Processando curso: {info['nome']} ({curso_id}) ===")

        pasta = info["pasta"]
        modulo_tabela = importlib.import_module(pasta.replace("/", ".") + ".tabela")

        docs_pdf = processar_pdf_do_curso(curso_id, pasta)

        docs_descritivos = gerar_docs_descritivos(curso_id, info["nome"], modulo_tabela.MATRIZ_CURRICULAR, modulo_tabela.ELETIVAS)
        print(f"    → {len(docs_descritivos)} textos descritivos gerados")

        docs_tabulares = tabelas_para_documents(curso_id, info["nome"], modulo_tabela.MATRIZ_CURRICULAR, modulo_tabela.ELETIVAS)
        print(f"    → {len(docs_tabulares)} documentos tabulares gerados")
        todos_os_docs += docs_pdf + docs_descritivos + docs_tabulares

    print(f"\nTotal de fragmentos a indexar (todos os cursos): {len(todos_os_docs)}")
    print("\nCriando banco de vetores único (chroma_db)...")
    Chroma.from_documents(todos_os_docs, embeddings, persist_directory=CHROMA_PATH)
    print("Banco de dados criado com sucesso!")


if __name__ == "__main__":
    processar_e_salvar()