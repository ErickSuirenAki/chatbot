"""
cursos_config.py — Lista central dos cursos suportados pelo chatbot
=====================================================================
Para adicionar um curso novo no futuro, o processo é:
  1. Criar a pasta cursos/<id_do_curso>/
  2. Colocar o PDF do PPC lá dentro, como ppc.pdf
  3. Criar cursos/<id_do_curso>/tabela.py com MATRIZ_CURRICULAR e ELETIVAS
     (use cursos/pedagogia/tabela.py como modelo)
  4. Adicionar uma entrada aqui embaixo em CURSOS

Nenhum outro arquivo precisa ser tocado — processar_pdf.py e
appOllamaLocal.py leem essa lista automaticamente.
"""

CURSOS = {
    "ciencia_computacao": {
        "nome": "Ciência da Computação",
        "pasta": "cursos/ciencia_computacao",
    },
    "pedagogia": {
        "nome": "Pedagogia — Licenciatura",
        "pasta": "cursos/pedagogia",
    },
}
