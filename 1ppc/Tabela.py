"""
dados.py — Tabelas do PPC de Ciência da Computação (UNIR)
==========================================================
Contém as duas tabelas principais do PPC exatamente como estão no documento:

  TABELA 1 — Matriz Curricular (8 períodos obrigatórios)
             Colunas: disciplina | prereq | cr | ch | apcc | total

  TABELA 2 — Disciplinas Eletivas (Quadro 4)
             Colunas: disciplina | prereq | cr | ch | apcc | total

Uso como módulo (importado pelo ingest.py):
    from dados import tabelas_para_documents

Uso standalone (consulta interativa):
    python dados.py
"""

from langchain_core.documents import Document

# ══════════════════════════════════════════════════════════════════
#  TABELA 1 — MATRIZ CURRICULAR POR PERÍODO
# ══════════════════════════════════════════════════════════════════
#
#  Campos de cada disciplina:
#    disciplina  → nome completo
#    prereq      → lista de pré-requisitos (strings); [] se não tiver
#    cr          → créditos
#    ch          → carga horária teórica/prática (horas)
#    apcc        → atividades práticas como componente curricular (horas)
#    total       → carga horária total (ch + apcc)
#
# ══════════════════════════════════════════════════════════════════

MATRIZ_CURRICULAR: dict[int, list[dict]] = {

    # ──────────────────────────────────────────────────────────────
    1: [  # PRIMEIRO PERÍODO
    # ──────────────────────────────────────────────────────────────
        {"disciplina": "Matemática Geral",                                   "prereq": [],                                                                                     "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Língua Portuguesa",                                  "prereq": [],                                                                                     "cr": 2,  "ch": 40,  "apcc": 0,  "total": 40},
        {"disciplina": "Sociologia Geral e do Desenvolvimento Tecnológico",  "prereq": [],                                                                                     "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Fundamentos da Computação",                          "prereq": [],                                                                                     "cr": 2,  "ch": 40,  "apcc": 0,  "total": 40},
        {"disciplina": "Eletrônica para Computação",                         "prereq": [],                                                                                     "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Programação I",                                      "prereq": [],                                                                                     "cr": 6,  "ch": 100, "apcc": 20, "total": 120},
        {"disciplina": "Lógica Matemática",                                  "prereq": [],                                                                                     "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Filosofia",                                          "prereq": [],                                                                                     "cr": 2,  "ch": 40,  "apcc": 0,  "total": 40},
        {"disciplina": "Noções de Direito",                                  "prereq": [],                                                                                     "cr": 2,  "ch": 40,  "apcc": 0,  "total": 40},
    ],
    # Subtotal: 27 cr | 520 ch | 20 apcc | 540 total

    # ──────────────────────────────────────────────────────────────
    2: [  # SEGUNDO PERÍODO
    # ──────────────────────────────────────────────────────────────
        {"disciplina": "Cálculo I",                                          "prereq": ["Matemática Geral"],                                                                   "cr": 5,  "ch": 100, "apcc": 0,  "total": 100},
        {"disciplina": "Organização de Computadores",                        "prereq": ["Eletrônica para Computação"],                                                         "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Programação II",                                     "prereq": ["Programação I"],                                                                      "cr": 5,  "ch": 80,  "apcc": 20, "total": 100},
        {"disciplina": "Estrutura de Dados I",                               "prereq": ["Programação I"],                                                                      "cr": 5,  "ch": 80,  "apcc": 20, "total": 100},
        {"disciplina": "Matemática Discreta",                                "prereq": ["Lógica Matemática"],                                                                  "cr": 5,  "ch": 100, "apcc": 0,  "total": 100},
        {"disciplina": "Geometria Analítica",                                "prereq": ["Matemática Geral"],                                                                   "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
    ],
    # Subtotal: 28 cr | 520 ch | 40 apcc | 560 total

    # ──────────────────────────────────────────────────────────────
    3: [  # TERCEIRO PERÍODO
    # ──────────────────────────────────────────────────────────────
        {"disciplina": "Cálculo II",                                         "prereq": ["Cálculo I"],                                                                          "cr": 5,  "ch": 100, "apcc": 0,  "total": 100},
        {"disciplina": "Álgebra Linear",                                     "prereq": ["Matemática Geral"],                                                                   "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Estrutura de Dados II",                              "prereq": ["Estrutura de Dados I"],                                                               "cr": 5,  "ch": 80,  "apcc": 20, "total": 100},
        {"disciplina": "Programação Orientada a Objetos",                    "prereq": ["Programação I"],                                                                      "cr": 5,  "ch": 80,  "apcc": 20, "total": 100},
        {"disciplina": "Organização, Sistemas e Métodos (OSM)",              "prereq": [],                                                                                     "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Sistemas Operacionais",                              "prereq": ["Organização de Computadores"],                                                        "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
    ],
    # Subtotal: 26 cr | 480 ch | 40 apcc | 520 total

    # ──────────────────────────────────────────────────────────────
    4: [  # QUARTO PERÍODO
    # ──────────────────────────────────────────────────────────────
        {"disciplina": "Cálculo III",                                        "prereq": ["Cálculo II"],                                                                         "cr": 5,  "ch": 100, "apcc": 0,  "total": 100},
        {"disciplina": "Teoria da Computação e Linguagens Formais",          "prereq": ["Estrutura de Dados II", "Matemática Discreta"],                                       "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Banco de Dados I",                                   "prereq": ["Sistemas Operacionais", "Estrutura de Dados II"],                                     "cr": 4,  "ch": 60,  "apcc": 20, "total": 80},
        {"disciplina": "Redes de Computadores",                              "prereq": ["Sistemas Operacionais"],                                                              "cr": 5,  "ch": 80,  "apcc": 20, "total": 100},
        {"disciplina": "Física Geral e Experimental I",                      "prereq": ["Cálculo I"],                                                                          "cr": 6,  "ch": 80,  "apcc": 40, "total": 120},
    ],
    # Subtotal: 24 cr | 400 ch | 80 apcc | 480 total

    # ──────────────────────────────────────────────────────────────
    5: [  # QUINTO PERÍODO
    # ──────────────────────────────────────────────────────────────
        {"disciplina": "Gerência de Projeto",                                "prereq": ["Organização, Sistemas e Métodos (OSM)"],                                              "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Laboratório de Banco de Dados",                      "prereq": ["Banco de Dados I"],                                                                   "cr": 5,  "ch": 40,  "apcc": 60, "total": 100},
        {"disciplina": "Introdução ao Desenvolvimento Web",                  "prereq": ["Programação Orientada a Objetos"],                                                    "cr": 4,  "ch": 60,  "apcc": 20, "total": 80},
        {"disciplina": "Sistemas Distribuídos",                              "prereq": ["Sistemas Operacionais", "Programação Orientada a Objetos"],                           "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Estatística e Probabilidade",                        "prereq": ["Cálculo II"],                                                                         "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Cálculo Numérico",                                   "prereq": ["Álgebra Linear", "Programação I"],                                                    "cr": 4,  "ch": 60,  "apcc": 20, "total": 80},
        {"disciplina": "Eletiva I",                                          "prereq": [],                                                                                     "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
    ],
    # Subtotal: 27 cr | 440 ch | 100 apcc | 540 total

    # ──────────────────────────────────────────────────────────────
    6: [  # SEXTO PERÍODO
    # ──────────────────────────────────────────────────────────────
        {"disciplina": "Análise de Sistemas",                                "prereq": ["Banco de Dados I"],                                                                   "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Arquitetura de Computadores",                        "prereq": ["Organização de Computadores"],                                                        "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Inteligência Artificial",                            "prereq": ["Estrutura de Dados II", "Cálculo II"],                                                "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Interface Homem/Computador",                         "prereq": ["Introdução ao Desenvolvimento Web"],                                                  "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Processos Estocásticos",                             "prereq": ["Estatística e Probabilidade", "Teoria da Computação e Linguagens Formais"],           "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Gerência de Recursos Humanos",                       "prereq": ["Organização, Sistemas e Métodos (OSM)"],                                              "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Empreendimentos em Informática",                     "prereq": ["Gerência de Projeto"],                                                                "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Eletiva II",                                         "prereq": [],                                                                                     "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
    ],
    # Subtotal: 27 cr | 540 ch | 0 apcc | 540 total

    # ──────────────────────────────────────────────────────────────
    7: [  # SÉTIMO PERÍODO
    # ──────────────────────────────────────────────────────────────
        {"disciplina": "Engenharia de Software",                             "prereq": ["Análise de Sistemas", "Gerência de Projeto", "Introdução ao Desenvolvimento Web"],    "cr": 5,  "ch": 80,  "apcc": 20, "total": 100},
        {"disciplina": "TCC 1",                                              "prereq": ["Análise de Sistemas", "Interface Homem/Computador", "Sistemas Distribuídos", "Estatística e Probabilidade", "Redes de Computadores"], "cr": 4, "ch": 80, "apcc": 0, "total": 80},
        {"disciplina": "Análise Orientada a Objetos",                        "prereq": ["Análise de Sistemas", "Programação Orientada a Objetos"],                             "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Compiladores e Linguagens de Programação",           "prereq": ["Teoria da Computação e Linguagens Formais"],                                          "cr": 4,  "ch": 60,  "apcc": 20, "total": 80},
        {"disciplina": "Computação Gráfica",                                 "prereq": ["Estrutura de Dados I"],                                                               "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Eletiva III",                                        "prereq": [],                                                                                     "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
    ],
    # Subtotal: 25 cr | 440 ch | 60 apcc | 500 total

    # ──────────────────────────────────────────────────────────────
    8: [  # OITAVO PERÍODO
    # ──────────────────────────────────────────────────────────────
        {"disciplina": "Transmissão de Dados",                               "prereq": ["Redes de Computadores"],                                                              "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "Segurança da Informação",                            "prereq": ["Gerência de Projeto"],                                                                "cr": 3,  "ch": 60,  "apcc": 0,  "total": 60},
        {"disciplina": "TCC 2",                                              "prereq": ["TCC 1", "Engenharia de Software"],                                                    "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Eletiva IV",                                         "prereq": [],                                                                                     "cr": 4,  "ch": 80,  "apcc": 0,  "total": 80},
        {"disciplina": "Atividades Científico-Culturais",                    "prereq": [],                                                                                     "cr": 0,  "ch": 200, "apcc": 0,  "total": 200},
        {"disciplina": "Estágio Supervisionado",                             "prereq": [],                                                                                     "cr": 10, "ch": 200, "apcc": 0,  "total": 200},
    ],
    # Subtotal: 24 cr | 680 ch | 0 apcc | 680 total
    # TOTAL GERAL: 4.020 ch | 340 apcc | 4.360 total
}


# ══════════════════════════════════════════════════════════════════
#  TABELA 2 — DISCIPLINAS ELETIVAS  (Quadro 4 do PPC)
# ══════════════════════════════════════════════════════════════════

ELETIVAS: list[dict] = [
    {"disciplina": "Teoria da Informação",                  "prereq": ["Estatística e Probabilidade"],                        "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Programação para Dispositivos Móveis",  "prereq": ["Programação Orientada a Objetos"],                    "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Semântica Formal",                      "prereq": ["Teoria da Computação e Linguagens Formais"],          "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Especificação Formal de Software",      "prereq": ["Semântica Formal"],                                   "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Algoritmos Avançados",                  "prereq": ["Estrutura de Dados II", "Programação II"],            "cr": 5, "ch": 80, "apcc": 20, "total": 100},
    {"disciplina": "Banco de Dados II",                     "prereq": ["Banco de Dados I"],                                   "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Sistemas Multimídia",                   "prereq": [],                                                     "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Processamento de Imagens",              "prereq": ["Estrutura de Dados II"],                              "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Pesquisa Operacional",                  "prereq": ["Cálculo Numérico"],                                   "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Tópicos Avançados em Computação I",     "prereq": [],                                                     "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Tópicos Avançados em Computação II",    "prereq": [],                                                     "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Governança de TI",                      "prereq": [],                                                     "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
    {"disciplina": "Informática na Educação",               "prereq": [],                                                     "cr": 4, "ch": 60, "apcc": 20, "total": 80},
    {"disciplina": "Libras",                                "prereq": [],                                                     "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
    {"disciplina": "Tecnologias de Ensino à Distância",     "prereq": ["Informática na Educação"],                            "cr": 5, "ch": 60, "apcc": 40, "total": 100},
    {"disciplina": "Sociedade e Cultura Brasileira",        "prereq": [],                                                     "cr": 3, "ch": 40, "apcc": 20, "total": 60},
]


# ══════════════════════════════════════════════════════════════════
#  FUNÇÃO EXPORTADA PARA O INGEST.PY
# ══════════════════════════════════════════════════════════════════

def tabelas_para_documents() -> list[Document]:
    """
    Converte MATRIZ_CURRICULAR e ELETIVAS em objetos Document do LangChain
    para serem indexados no ChromaDB pelo ingest.py.

    Estratégia:
      - 1 Document por período  → contém todas as disciplinas do período
        em formato de tabela Markdown, com pré-requisitos e carga horária
      - 1 Document para eletivas → tabela Markdown do Quadro 4
      - 1 Document por disciplina individualmente → permite busca granular

    Assim o retriever consegue encontrar tanto perguntas gerais
    ("quais disciplinas tem no 3º período?") quanto específicas
    ("quem são os pré-requisitos de Banco de Dados I?").
    """
    nomes_periodos = {
        1: "PRIMEIRO",  2: "SEGUNDO",  3: "TERCEIRO", 4: "QUARTO",
        5: "QUINTO",    6: "SEXTO",    7: "SÉTIMO",   8: "OITAVO",
    }
    docs = []

    # ── Document por período (visão geral do período) ──────────────
    for periodo, disciplinas in MATRIZ_CURRICULAR.items():
        nome_periodo = nomes_periodos[periodo]
        linhas = [
            f"[TABELA — MATRIZ CURRICULAR — {nome_periodo} PERÍODO ({periodo}º)]",
            "",
            f"| Disciplina | Pré-Requisitos | CR | CH | APCC | Total |",
            f"|---|---|---|---|---|---|",
        ]
        for d in disciplinas:
            prereqs = ", ".join(d["prereq"]) if d["prereq"] else "—"
            linhas.append(
                f"| {d['disciplina']} | {prereqs} | {d['cr']} | {d['ch']} | {d['apcc']} | {d['total']} |"
            )
        docs.append(Document(
            page_content="\n".join(linhas),
            metadata={
                "tipo":    "tabela_periodo",
                "periodo": periodo,
                "source":  "dados.py",
            }
        ))

    # ── Document por disciplina individualmente ────────────────────
    for periodo, disciplinas in MATRIZ_CURRICULAR.items():
        nome_periodo = nomes_periodos[periodo]
        for d in disciplinas:
            prereqs = ", ".join(d["prereq"]) if d["prereq"] else "Nenhum"
            conteudo = (
                f"[DISCIPLINA — {nome_periodo} PERÍODO ({periodo}º)]\n\n"
                f"Nome: {d['disciplina']}\n"
                f"Período: {periodo}º ({nome_periodo})\n"
                f"Pré-Requisitos: {prereqs}\n"
                f"Créditos: {d['cr']}\n"
                f"Carga Horária: {d['ch']}h\n"
                f"APCC: {d['apcc']}h\n"
                f"Total: {d['total']}h"
            )
            docs.append(Document(
                page_content=conteudo,
                metadata={
                    "tipo":       "disciplina",
                    "periodo":    periodo,
                    "disciplina": d["disciplina"],
                    "source":     "dados.py",
                }
            ))

    # ── Document da tabela de eletivas (visão geral) ───────────────
    linhas_el = [
        "[TABELA — DISCIPLINAS ELETIVAS — Quadro 4]",
        "",
        "| Disciplina | Pré-Requisitos | CR | CH | APCC | Total |",
        "|---|---|---|---|---|---|",
    ]
    for d in ELETIVAS:
        prereqs = ", ".join(d["prereq"]) if d["prereq"] else "—"
        linhas_el.append(
            f"| {d['disciplina']} | {prereqs} | {d['cr']} | {d['ch']} | {d['apcc']} | {d['total']} |"
        )
    docs.append(Document(
        page_content="\n".join(linhas_el),
        metadata={
            "tipo":   "tabela_eletivas",
            "source": "dados.py",
        }
    ))

    # ── Document por eletiva individualmente ──────────────────────
    for d in ELETIVAS:
        prereqs = ", ".join(d["prereq"]) if d["prereq"] else "Nenhum"
        conteudo = (
            f"[DISCIPLINA ELETIVA]\n\n"
            f"Nome: {d['disciplina']}\n"
            f"Período: Eletiva (cursada no 5º, 6º, 7º ou 8º período)\n"
            f"Pré-Requisitos: {prereqs}\n"
            f"Créditos: {d['cr']}\n"
            f"Carga Horária: {d['ch']}h\n"
            f"APCC: {d['apcc']}h\n"
            f"Total: {d['total']}h"
        )
        docs.append(Document(
            page_content=conteudo,
            metadata={
                "tipo":       "disciplina_eletiva",
                "disciplina": d["disciplina"],
                "source":     "dados.py",
            }
        ))

    return docs


# ══════════════════════════════════════════════════════════════════
#  FUNÇÕES DE CONSULTA (uso standalone, não afetam o ingest)
# ══════════════════════════════════════════════════════════════════

def _tabela_periodo_str(periodo: int) -> str:
    nomes = {1:"PRIMEIRO",2:"SEGUNDO",3:"TERCEIRO",4:"QUARTO",5:"QUINTO",6:"SEXTO",7:"SÉTIMO",8:"OITAVO"}
    if periodo not in MATRIZ_CURRICULAR:
        return f"Período {periodo} não existe. Use 1 a 8."
    sep = "─" * 72
    linhas = [sep, f"{nomes[periodo]} PERÍODO", sep,
              f"{'DISCIPLINA':<46} {'PRÉ-REQUISITOS':<28} {'CR':>3} {'CH':>5} {'APCC':>5} {'TOTAL':>6}", sep]
    tcr = tch = tapcc = ttotal = 0
    for d in MATRIZ_CURRICULAR[periodo]:
        pr = ", ".join(d["prereq"]) if d["prereq"] else "—"
        pr = pr[:26] + ".." if len(pr) > 28 else pr
        linhas.append(f"{d['disciplina']:<46} {pr:<28} {d['cr']:>3} {d['ch']:>5} {d['apcc']:>5} {d['total']:>6}")
        tcr += d["cr"]; tch += d["ch"]; tapcc += d["apcc"]; ttotal += d["total"]
    linhas += [sep, f"{'SUBTOTAL':<46} {'':28} {tcr:>3} {tch:>5} {tapcc:>5} {ttotal:>6}", sep]
    return "\n".join(linhas)


def _tabela_eletivas_str() -> str:
    sep = "─" * 72
    linhas = [sep, "DISCIPLINAS ELETIVAS  (Quadro 4)", sep,
              f"{'DISCIPLINA':<46} {'PRÉ-REQUISITOS':<28} {'CR':>3} {'CH':>5} {'APCC':>5} {'TOTAL':>6}", sep]
    for d in ELETIVAS:
        pr = ", ".join(d["prereq"]) if d["prereq"] else "—"
        pr = pr[:26] + ".." if len(pr) > 28 else pr
        linhas.append(f"{d['disciplina']:<46} {pr:<28} {d['cr']:>3} {d['ch']:>5} {d['apcc']:>5} {d['total']:>6}")
    linhas.append(sep)
    return "\n".join(linhas)


def _normalizar(texto: str) -> str:
    """Remove acentos e converte para minúsculas para busca tolerante."""
    import unicodedata
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("ascii").lower()


def _buscar(nome: str) -> list[tuple]:
    """Busca por nome parcial, ignorando acentos e maiúsculas."""
    nome_n = _normalizar(nome)
    res = []
    for periodo, discs in MATRIZ_CURRICULAR.items():
        for d in discs:
            if nome_n in _normalizar(d["disciplina"]):
                res.append((periodo, d))
    for d in ELETIVAS:
        if nome_n in _normalizar(d["disciplina"]):
            res.append(("eletiva", d))
    return res


def _prereqs(nome: str) -> str:
    res = _buscar(nome)
    if not res:
        return f"Disciplina '{nome}' não encontrada."
    linhas = []
    for periodo, d in res:
        label = f"{periodo}º período" if isinstance(periodo, int) else "Eletiva"
        pr = ", ".join(d["prereq"]) if d["prereq"] else "Nenhum"
        linhas.append(f"[{label}]  {d['disciplina']}\n  Pré-requisitos: {pr}")
    return "\n".join(linhas)


def _depende(nome: str) -> str:
    nome_n = _normalizar(nome)
    deps = []
    for periodo, discs in MATRIZ_CURRICULAR.items():
        for d in discs:
            if any(nome_n in _normalizar(pr) for pr in d["prereq"]):
                deps.append(f"[{periodo}º período]  {d['disciplina']}")
    for d in ELETIVAS:
        if any(nome_n in _normalizar(pr) for pr in d["prereq"]):
            deps.append(f"[Eletiva]  {d['disciplina']}")
    if not deps:
        return f"Nenhuma disciplina depende de '{nome}'."
    return f"Disciplinas que dependem de '{nome}':\n" + "\n".join(f"  • {x}" for x in deps)


# ══════════════════════════════════════════════════════════════════
#  CLI INTERATIVO
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    AJUDA = """
Comandos disponíveis:
  periodo <N>          → tabela do período N        (ex: periodo 3)
  eletivas             → tabela de disciplinas eletivas
  todas                → imprime todas as tabelas
  prereq <disciplina>  → pré-requisitos de uma disciplina
  depende <disciplina> → quais disciplinas dependem dela
  buscar <nome>        → busca disciplina por nome parcial
  ajuda                → mostra este menu
  sair                 → encerra
"""
    print("=" * 72)
    print("  TABELAS DO PPC — Ciência da Computação (UNIR)")
    print("=" * 72)
    print(AJUDA)

    while True:
        try:
            cmd = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd:
            continue

        partes = cmd.split(" ", 1)
        op  = partes[0].lower()
        arg = partes[1].strip() if len(partes) > 1 else ""

        if op == "sair":
            break
        elif op == "ajuda":
            print(AJUDA)
        elif op == "periodo":
            try:
                print(_tabela_periodo_str(int(arg)))
            except (ValueError, TypeError):
                print("Use: periodo <número de 1 a 8>")
        elif op == "eletivas":
            print(_tabela_eletivas_str())
        elif op == "todas":
            for i in range(1, 9):
                print(_tabela_periodo_str(i))
                print()
            print(_tabela_eletivas_str())
        elif op == "prereq":
            print(_prereqs(arg) if arg else "Informe o nome da disciplina.")
        elif op == "depende":
            print(_depende(arg) if arg else "Informe o nome da disciplina.")
        elif op == "buscar":
            if not arg:
                print("Informe o nome da disciplina.")
            else:
                res = _buscar(arg)
                if not res:
                    print(f"Nenhuma disciplina encontrada com '{arg}'.")
                else:
                    for periodo, d in res:
                        label = f"{periodo}º período" if isinstance(periodo, int) else "Eletiva"
                        pr = ", ".join(d["prereq"]) if d["prereq"] else "Nenhum"
                        print(f"[{label}]  {d['disciplina']}")
                        print(f"  CR: {d['cr']} | CH: {d['ch']}h | APCC: {d['apcc']}h | Total: {d['total']}h")
                        print(f"  Pré-requisitos: {pr}")
        else:
            # tenta buscar diretamente pelo que foi digitado
            res = _buscar(cmd)
            if res:
                for periodo, d in res:
                    label = f"{periodo}º período" if isinstance(periodo, int) else "Eletiva"
                    pr = ", ".join(d["prereq"]) if d["prereq"] else "Nenhum"
                    print(f"[{label}]  {d['disciplina']}")
                    print(f"  CR: {d['cr']} | CH: {d['ch']}h | APCC: {d['apcc']}h | Total: {d['total']}h")
                    print(f"  Pré-requisitos: {pr}")
            else:
                print(f"Comando '{op}' não reconhecido. Digite 'ajuda' para ver os comandos.")
        print()