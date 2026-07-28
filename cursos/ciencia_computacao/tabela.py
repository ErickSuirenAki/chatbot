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
