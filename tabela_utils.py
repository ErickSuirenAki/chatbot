import unicodedata
from langchain_core.documents import Document


def tabelas_para_documents(curso_id: str, curso_nome: str, matriz_curricular: dict, eletivas: list) -> list[Document]:
    """
    Converte a matriz curricular e as eletivas de UM curso em objetos Document.

    Parâmetros:
      curso_id         → identificador curto do curso, usado como filtro
                          (ex: "ciencia_computacao", "pedagogia")
      curso_nome        → nome legível do curso, usado nos textos
                          (ex: "Ciência da Computação", "Pedagogia")
      matriz_curricular → dict {periodo: [disciplinas]}, formato do tabela.py do curso
      eletivas          → list [disciplinas], formato do tabela.py do curso

    Retorna uma lista de Documents:
      - 1 por período  (tabela markdown com todas as disciplinas do período)
      - 1 por disciplina obrigatória (ficha individual)
      - 1 para a tabela geral de eletivas
      - 1 por eletiva individual
    Todos com metadata["curso"] = curso_id, para permitir filtro depois.
    """
    docs = []
    ultimo_periodo = max(matriz_curricular.keys())

    # ── Document por período (visão geral do período) ──────────────
    for periodo, disciplinas in matriz_curricular.items():
        linhas = [
            f"[TABELA — MATRIZ CURRICULAR — {curso_nome.upper()} — {periodo}º PERÍODO]",
            "",
            "| Disciplina | Pré-Requisitos | CR | CH | APCC | Total |",
            "|---|---|---|---|---|---|",
        ]
        for d in disciplinas:
            prereqs = ", ".join(d["prereq"]) if d["prereq"] else "—"
            linhas.append(
                f"| {d['disciplina']} | {prereqs} | {d['cr']} | {d['ch']} | {d['apcc']} | {d['total']} |"
            )
        docs.append(Document(
            page_content="\n".join(linhas),
            metadata={
                "tipo": "tabela_periodo",
                "periodo": periodo,
                "curso": curso_id,
                "source": f"cursos/{curso_id}/tabela.py",
            }
        ))

    # ── Document por disciplina individualmente ─────────────────────
    for periodo, disciplinas in matriz_curricular.items():
        for d in disciplinas:
            prereqs = ", ".join(d["prereq"]) if d["prereq"] else "Nenhum"
            conteudo = (
                f"[DISCIPLINA — {curso_nome} — {periodo}º PERÍODO]\n\n"
                f"Curso: {curso_nome}\n"
                f"Nome: {d['disciplina']}\n"
                f"Período: {periodo}º\n"
                f"Pré-Requisitos: {prereqs}\n"
                f"Créditos: {d['cr']}\n"
                f"Carga Horária: {d['ch']}h\n"
                f"APCC: {d['apcc']}h\n"
                f"Total: {d['total']}h"
            )
            docs.append(Document(
                page_content=conteudo,
                metadata={
                    "tipo": "disciplina",
                    "periodo": periodo,
                    "disciplina": d["disciplina"],
                    "curso": curso_id,
                    "source": f"cursos/{curso_id}/tabela.py",
                }
            ))

    # ── Document da tabela de eletivas (visão geral) ────────────────
    if eletivas:
        linhas_el = [
            f"[TABELA — DISCIPLINAS ELETIVAS/OPTATIVAS — {curso_nome.upper()}]",
            "",
            "| Disciplina | Pré-Requisitos | CR | CH | APCC | Total |",
            "|---|---|---|---|---|---|",
        ]
        for d in eletivas:
            prereqs = ", ".join(d["prereq"]) if d["prereq"] else "—"
            linhas_el.append(
                f"| {d['disciplina']} | {prereqs} | {d['cr']} | {d['ch']} | {d['apcc']} | {d['total']} |"
            )
        docs.append(Document(
            page_content="\n".join(linhas_el),
            metadata={"tipo": "tabela_eletivas", "curso": curso_id, "source": f"cursos/{curso_id}/tabela.py"}
        ))

        # ── Document por eletiva individualmente ────────────────────
        for d in eletivas:
            prereqs = ", ".join(d["prereq"]) if d["prereq"] else "Nenhum"
            conteudo = (
                f"[DISCIPLINA ELETIVA/OPTATIVA — {curso_nome}]\n\n"
                f"Curso: {curso_nome}\n"
                f"Nome: {d['disciplina']}\n"
                f"Período: Eletiva (pode variar conforme oferta do semestre)\n"
                f"Pré-Requisitos: {prereqs}\n"
                f"Créditos: {d['cr']}\n"
                f"Carga Horária: {d['ch']}h\n"
                f"APCC: {d['apcc']}h\n"
                f"Total: {d['total']}h"
            )
            docs.append(Document(
                page_content=conteudo,
                metadata={
                    "tipo": "disciplina_eletiva",
                    "disciplina": d["disciplina"],
                    "curso": curso_id,
                    "source": f"cursos/{curso_id}/tabela.py",
                }
            ))

    return docs


def gerar_docs_descritivos(curso_id: str, curso_nome: str, matriz_curricular: dict, eletivas: list) -> list[Document]:
    """
    Gera frases em linguagem natural para cada disciplina (obrigatória e
    eletiva). Embeddings entendem melhor texto corrido do que tabelas, então
    essas frases ajudam a busca semântica a encontrar a disciplina certa
    mesmo quando a pergunta não usa o vocabulário exato da tabela.
    """
    docs = []

    def _frase_prereq(prereqs):
        if not prereqs:
            return "Não tem pré-requisitos"
        if len(prereqs) == 1:
            return f"O pré-requisito é {prereqs[0]}"
        return f"Os pré-requisitos são {', '.join(prereqs[:-1])} e {prereqs[-1]}"

    def _frase_ch(d):
        if d["apcc"] > 0:
            return (
                f"Tem {d['cr']} créditos e carga horária total de {d['total']} horas "
                f"({d['ch']}h teóricas + {d['apcc']}h práticas)"
            )
        return f"Tem {d['cr']} créditos e carga horária de {d['total']} horas"

    for periodo, disciplinas in matriz_curricular.items():
        for d in disciplinas:
            texto = (
                f"A disciplina {d['disciplina']} é obrigatória no {periodo}º período "
                f"do curso de {curso_nome}. {_frase_ch(d)}. {_frase_prereq(d['prereq'])}."
            )
            docs.append(Document(
                page_content=texto,
                metadata={
                    "tipo": "descritivo_disciplina",
                    "periodo": periodo,
                    "disciplina": d["disciplina"],
                    "curso": curso_id,
                    "source": f"cursos/{curso_id}/tabela.py",
                }
            ))

    for d in eletivas:
        texto = (
            f"A disciplina {d['disciplina']} é eletiva/optativa do curso de {curso_nome}. "
            f"{_frase_ch(d)}. {_frase_prereq(d['prereq'])}."
        )
        docs.append(Document(
            page_content=texto,
            metadata={
                "tipo": "descritivo_eletiva",
                "disciplina": d["disciplina"],
                "curso": curso_id,
                "source": f"cursos/{curso_id}/tabela.py",
            }
        ))

    return docs


def normalizar(texto: str) -> str:
    """Remove acentos e converte para minúsculas para busca tolerante."""
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("ascii").lower()
