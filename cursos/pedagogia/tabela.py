"""
tabela.py — Matriz curricular do curso de Pedagogia — Licenciatura (UNIR, Ji-Paraná)
======================================================================================
Extraído do PPC (páginas 36-42): "MATRIZ CURRICULAR OBRIGATÓRIA" e
"MATRIZ CURRICULAR DOS COMPONENTES OPTATIVOS OBRIGATÓRIOS".

IMPORTANTE — diferenças em relação ao PPC de Ciência da Computação:
  • O PPC de Pedagogia NÃO lista pré-requisitos entre disciplinas (o curso é
    organizado por eixos/núcleos, não por dependência direta entre matérias).
    Por isso, "prereq" fica sempre como lista vazia [].
  • O PPC usa "H.T." (horas teóricas) e "H.P." (horas práticas) em vez de
    "CH" (carga horária teórica) e "APCC" (atividades práticas como
    componente curricular). Na prática os dois pares de campos representam
    a mesma ideia (teoria x prática), então reaproveitamos os mesmos nomes
    de campo do curso de Computação (ch = teoria, apcc = prática) para que
    o restante do código (tabela_utils.py) funcione sem precisar saber
    qual curso está processando.
  • O curso tem 9 períodos (semestres), não 8.
"""

from typing import Dict, List

# ══════════════════════════════════════════════════════════════════
#  TABELA 1 — MATRIZ CURRICULAR OBRIGATÓRIA POR SEMESTRE
# ══════════════════════════════════════════════════════════════════
#
#  Campos de cada disciplina:
#    disciplina  → nome completo
#    prereq      → sempre [] neste curso (PPC não define pré-requisitos)
#    cr          → créditos
#    ch          → carga horária teórica (H.T.)
#    apcc        → carga horária prática (H.P.)
#    total       → carga horária total (ch + apcc)
#
# ══════════════════════════════════════════════════════════════════

MATRIZ_CURRICULAR: Dict[int, List[dict]] = {

    1: [  # PRIMEIRO SEMESTRE
        {"disciplina": "Metodologia da Pesquisa Científica", "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Psicologia da Educação I",           "prereq": [], "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
        {"disciplina": "Sociologia da Educação I",           "prereq": [], "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
        {"disciplina": "LIBRAS",                              "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "História da Educação",               "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
    ],
    # Subtotal do semestre: 400h

    2: [  # SEGUNDO SEMESTRE
        {"disciplina": "Filosofia da Educação I",   "prereq": [], "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
        {"disciplina": "Brincar e Educação",         "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Sociologia da Educação II",  "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Língua Portuguesa",          "prereq": [], "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
        {"disciplina": "Relações Interpessoais",     "prereq": [], "cr": 2, "ch": 20, "apcc": 20, "total": 40},
        {"disciplina": "Arte Educação",              "prereq": [], "cr": 2, "ch": 20, "apcc": 20, "total": 40},
    ],
    # Subtotal do semestre: 400h

    3: [  # TERCEIRO SEMESTRE
        {"disciplina": "Filosofia da Educação II",           "prereq": [], "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
        {"disciplina": "Didática",                            "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Educação com Jovens e Adultos",       "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Psicologia da Educação II",           "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Educação, Gênero e Sexualidade",      "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
        {"disciplina": "Educação e Relações Raciais",         "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
    ],
    # Subtotal do semestre: 400h

    4: [  # QUARTO SEMESTRE
        {"disciplina": "Metodologia do Ensino da Educação Infantil I", "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Metodologia do Ensino da Alfabetização I",     "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Metodologia do Ensino da Língua Portuguesa",   "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Educação Inclusiva",                            "prereq": [], "cr": 4, "ch": 80, "apcc": 0,  "total": 80},
        {"disciplina": "Pedagogia não escolar",                         "prereq": [], "cr": 2, "ch": 30, "apcc": 10, "total": 40},
        {"disciplina": "Optativa",                                      "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
    ],
    # Subtotal do semestre: 400h

    5: [  # QUINTO SEMESTRE
        {"disciplina": "Estágio Supervisionado em Educação Inclusiva",  "prereq": ["Didática", "Educação Inclusiva", "Libras", "Educação e Relações Raciais"], "cr": 4, "ch": 20, "apcc": 60, "total": 80},
        {"disciplina": "Metodologia do Ensino da Educação Infantil II", "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Metodologia do Ensino de Matemática",           "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Metodologia do Ensino de Geografia",            "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Metodologia do Ensino da Alfabetização II",     "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Optativa",                                      "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
    ],
    # Subtotal do semestre: 440h

    6: [  # SEXTO SEMESTRE
        {"disciplina": "Estágio Supervisionado em Espaço não Escolar",     "prereq": ["Didática", "Pedagogia não escolar", "Relações raciais"], "cr": 4, "ch": 20, "apcc": 60, "total": 80},
        {"disciplina": "Metodologia do Ensino de Ciências",                 "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Pesquisa em Educação I – Projeto de Pesquisa",     "prereq": [], "cr": 4, "ch": 40, "apcc": 40, "total": 80},
        {"disciplina": "Metodologia do Ensino de História",                 "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Gestão do Trabalho Escolar e não escolar",         "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Optativa",                                          "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
    ],
    # Subtotal do semestre: 440h

    7: [  # SÉTIMO SEMESTRE
        {"disciplina": "Estágio Supervisionado em Educação Infantil e Gestão", "prereq": [], "cr": 6, "ch": 20, "apcc": 100, "total": 120},
        {"disciplina": "Educação e Tecnologias",  "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Pedagogia e Extensão",     "prereq": [], "cr": 5, "ch": 80, "apcc": 20, "total": 100},
        {"disciplina": "Optativa",                 "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
        {"disciplina": "Educação do Campo",        "prereq": [], "cr": 2, "ch": 25, "apcc": 15, "total": 40},
        {"disciplina": "Optativa",                 "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
    ],
    # Subtotal do semestre: 420h

    8: [  # OITAVO SEMESTRE
        {"disciplina": "Estágio Supervisionado nos Anos Iniciais, EJA e Gestão", "prereq": [], "cr": 6, "ch": 20, "apcc": 100, "total": 120},
        {"disciplina": "Educação com Povos da Floresta", "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Legislação Educacional",          "prereq": [], "cr": 4, "ch": 60, "apcc": 20, "total": 80},
        {"disciplina": "Educação Ambiental",              "prereq": [], "cr": 2, "ch": 25, "apcc": 15, "total": 40},
        {"disciplina": "Teorias do Currículo",            "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
        {"disciplina": "Optativa",                        "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
    ],
    # Subtotal do semestre: 400h

    9: [  # NONO SEMESTRE
        {"disciplina": "Pesquisa em Educação II – TCC",       "prereq": [], "cr": 4, "ch": 20, "apcc": 60, "total": 80},
        {"disciplina": "Políticas Públicas para Educação",     "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
        {"disciplina": "Políticas em Avaliação Educacional",   "prereq": [], "cr": 2, "ch": 20, "apcc": 20, "total": 40},
        {"disciplina": "Optativa",                              "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
        {"disciplina": "Optativa",                              "prereq": [], "cr": 2, "ch": 40, "apcc": 0,  "total": 40},
    ],
    # Subtotal do semestre: 240h
    # + Atividades Complementares: 200h (fora da grade por semestre)
    # TOTAL GERAL DO CURSO: 3.740h
}


# ══════════════════════════════════════════════════════════════════
#  TABELA 2 — DISCIPLINAS OPTATIVAS OBRIGATÓRIAS
#  (o aluno escolhe algumas dentre a lista; não têm semestre fixo)
# ══════════════════════════════════════════════════════════════════
#  Observação: o PPC não informa "CR" (créditos) para as optativas,
#  apenas T (teoria) / P (prática) / Total. Como todas têm 40h totais
#  e, no restante do PPC, 1 crédito = 20h, aplicamos cr = total / 20.

ELETIVAS: List[dict] = [
    {"disciplina": "Cultura, identidade e diferença",                              "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Psicopedagogia e educação",                                    "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Teatro didático: linguagens cênicas",                          "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Escola do campo e agroecologia para crianças",                 "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Retórica, ciência e educação",                                 "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Existencialismo e educação",                                   "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Lógica e teoria da ciência",                                   "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Ensino de língua portuguesa como segunda língua para surdos",  "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Libras (optativa)",                                            "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Pedagogia social",                                             "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Metodologias de pesquisa com crianças",                        "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Educação com bebês",                                           "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Projetos educacionais interdisciplinares",                     "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Etnoconhecimento e educação",                                  "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "História oral e documentos",                                   "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Literatura infantil africana",                                 "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Pedagogia de Projetos no Ensino de Ciências",                  "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Matemática Básica",                                            "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Pedagogia sistêmica",                                          "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Estudos das Infâncias",                                        "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Formação e Profissionalização Docente",                        "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Desenvolvimento moral e ética profissional",                   "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Contação de histórias",                                        "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Literatura infanto-juvenil",                                   "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
    {"disciplina": "Produção de material didático",                                "prereq": [], "cr": 2, "ch": 40, "apcc": 0, "total": 40},
]
