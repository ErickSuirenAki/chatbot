"""Totais conferidos nos PPCs, mantendo divergências do documento."""
import re

from resposta_estruturada import norm


CARGAS_CONFERIDAS = {
    "ciencia_computacao": (
        "A carga horária total é de **4.360 horas**, conforme a seção de identificação do curso."
    ),
    "estatistica_bacharelado_ji_parana_resolucao_726_2024": (
        "A carga horária total é de **3.290 horas-relógio**, conforme a Resolução 726/2024."
    ),
    "historia_licenciatura_porto_velho_ppc_2013": (
        "O PPC apresenta dois valores. A identificação do curso informa **3.360** e "
        "a tabela de integralização registra **3.560** na coluna de carga horária."
    ),
    "engenharia_eletrica_bacharelado_porto_velho_proposta_2004_processo_2005": (
        "O processo apresenta dois valores. Na seção 7.2, a matriz tem **5.240 horas-aula** "
        "(262 créditos). Na seção 9, a proposta prevê **5.420 horas-aula** (271 créditos)."
    ),
}


def responder_carga_curso(pergunta, curso_id):
    pergunta = norm(pergunta).rstrip("?.!")
    if re.fullmatch(
        r"(?:(?:qual (?:e )?a|me diga a) )?carga horaria(?: total)? do curso"
        r"|quantas horas (?:tem o curso|o curso tem)"
        r"|qual (?:e )?a carga horaria total",
        pergunta,
    ):
        return CARGAS_CONFERIDAS.get(curso_id)
    return None
