import os
from cursos_config import CURSOS, carregar_tabela
from pathlib import Path
import hashlib
import argparse
import gc
import tempfile
from importlib.metadata import version
from banco_utils import publicar_banco

CHROMA_PATH = "./chroma_db"  #um banco só, compartilhado por todos os cursos


def processar_pdf_do_curso(curso_id: str, pasta: str, arquivo_pdf: str | None = None):
    caminho_pdf = arquivo_pdf or os.path.join(pasta, "ppc.pdf")
    print(f"  Convertendo PDF ({caminho_pdf})...")

    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorDevice
    from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

    cache_dir = Path("cache_ppcs")
    cache_dir.mkdir(exist_ok=True)
    chave = hashlib.sha256(Path(caminho_pdf).read_bytes()).hexdigest()
    chave += "-" + version("docling")
    cache = cache_dir / (chave + ".md")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options.device = AcceleratorDevice.CPU

    if cache.exists():
        md_content = cache.read_text(encoding="utf-8")
        print("    → Reutilizando conversão já concluída.")
    else:
        converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)})
        result = converter.convert(caminho_pdf)
        if getattr(result.status, "value", str(result.status)) != "success":
            raise ValueError(f"Conversão incompleta de {caminho_pdf}; confira as páginas antes de publicar.")
        md_content = result.document.export_to_markdown()
        if not md_content.strip():
            raise ValueError(f"Nenhum texto extraído de {caminho_pdf}.")
        fd, temporario = tempfile.mkstemp(dir=cache_dir, prefix=".conversao-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
                arquivo.write(md_content)
            os.replace(temporario, cache)
        finally:
            if os.path.exists(temporario):
                os.unlink(temporario)
        del converter, result
        gc.collect()

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

    if not docs_pdf:
        raise ValueError(f"Nenhum texto extraído de {caminho_pdf}; verifique o PDF.")
    print(f"    → {len(docs_pdf)} fragmentos extraídos do PDF")
    return docs_pdf


def validar_documentos(cursos):
    """Confere todos os arquivos antes de carregar modelos ou iniciar a indexação."""
    for curso_id, info in cursos.items():
        caminho = Path(info.get("arquivo_pdf") or Path(info["pasta"]) / "ppc.pdf")
        if not caminho.is_file():
            raise ValueError(f"PDF não encontrado para {curso_id}: {caminho}")
        with caminho.open("rb") as arquivo:
            if b"%PDF-" not in arquivo.read(1024):
                raise ValueError(f"O arquivo não parece ser um PDF: {caminho}")
            arquivo.seek(0)
            digest = hashlib.sha256()
            for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
                digest.update(bloco)
            sha = digest.hexdigest()
        if info.get("pdf_sha256") and info["pdf_sha256"] != sha:
            raise ValueError(f"O PDF de {curso_id} mudou desde a identificação; revise o cadastro.")
    return len(cursos)


def processar_e_salvar():
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    from tabela_utils import tabelas_para_documents, gerar_docs_descritivos

    validar_documentos(CURSOS)
    todos_os_docs = []

    # Percorre todos os cursos cadastrados em cursos_config.py
    # Cada curso tem seu próprio tabela.py
    for curso_id, info in CURSOS.items():
        print(f"\n=== Processando curso: {info['nome']} ({curso_id}) ===")

        pasta = info["pasta"]
        modulo_tabela = carregar_tabela(pasta)
        docs_pdf = processar_pdf_do_curso(curso_id, pasta, info.get("arquivo_pdf"))
        todos_os_docs += docs_pdf
        if modulo_tabela is None:
            print("    → Curso sem matriz revisada; consultas pelo texto do PPC.")
            continue

        docs_descritivos = gerar_docs_descritivos(curso_id, info["nome"], modulo_tabela.MATRIZ_CURRICULAR, modulo_tabela.ELETIVAS)
        docs_tabulares = tabelas_para_documents(curso_id, info["nome"], modulo_tabela.MATRIZ_CURRICULAR, modulo_tabela.ELETIVAS)
        print(f"    → {len(docs_descritivos)} textos descritivos e {len(docs_tabulares)} documentos tabulares")
        todos_os_docs += docs_descritivos + docs_tabulares

    print(f"\nTotal de fragmentos a indexar (todos os cursos): {len(todos_os_docs)}")
    print("\nCriando banco de vetores único (chroma_db)...")
    if not todos_os_docs:
        raise ValueError("Nenhum documento extraído; a base anterior foi preservada.")

    def construir(destino):
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3", model_kwargs={"device": "cpu"}, encode_kwargs={"normalize_embeddings": True})
        banco = Chroma.from_documents(todos_os_docs, embeddings, persist_directory=str(destino))
        if len(banco.get(include=[])["ids"]) != len(todos_os_docs):
            raise ValueError("A nova base não contém todos os documentos esperados.")

    destino = publicar_banco(construir, CHROMA_PATH)
    print(f"Banco publicado com sucesso em {destino}. A versão anterior foi preservada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Valida ou indexa os PPCs cadastrados.")
    parser.add_argument("--validar", action="store_true", help="Confere arquivos e hashes, sem carregar modelos nem alterar o banco.")
    args = parser.parse_args()
    if args.validar:
        print(f"Validação concluída: {validar_documentos(CURSOS)} PPCs cadastrados.")
    else:
        processar_e_salvar()
