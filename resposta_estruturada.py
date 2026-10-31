"""
resposta_estruturada.py — Camada de resposta direta por metadados
=====================================================================
Ideia trazida do rag_core.py da colega (fuzzy matching de disciplina +
detecção de intenção) e reescrita para usar o schema de metadados que já
existe neste projeto (tabela_utils.py): "disciplina", "periodo", "cr",
"ch", "apcc", "total", "curso".

Por que existe: perguntas do tipo "qual a carga horária de Cálculo I?"
não deveriam depender do LLM — ele pode arredondar, inventar ou misturar
disciplinas parecidas. Aqui a resposta vem direto dos metadados extraídos
da grade curricular (tabela.py de cada curso), sem gerar valores com um modelo de linguagem; a correção depende dos dados cadastrados.

Se a camada não conseguir identificar com confiança a disciplina + a
intenção da pergunta, devolve None — quem chamar cai no fallback semântico
(RAG + LLM) normalmente.
"""

from __future__ import annotations

import re
import unicodedata
import difflib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_chroma import Chroma

# palavra-chave da pergunta -> campo de metadado correspondente
CAMPO_POR_INTENCAO = {
    "cr": ["credito", "créditos", "quantos creditos", "quantos créditos"],
    "ch": ["carga horaria", "carga horária", "quantas horas teoricas", "horas teoricas"],
    "apcc": ["apcc", "horas praticas", "horas práticas", "atividade pratica"],
    "total": ["carga horaria total", "total de horas", "quantas horas"],
    "periodo": ["periodo", "período", "qual periodo", "que periodo", "semestre"],
    "prereq": ["pre-requisito", "pre requisito", "prerequisito", "requisito"],
}

# a ordem importa: intenções mais específicas (ex: "carga horaria total")
# precisam ser checadas antes das mais genéricas (ex: "carga horaria")
ORDEM_INTENCAO = ["prereq", "apcc", "total", "cr", "ch", "periodo"]

PALAVRAS_LISTAGEM = [
    "liste", "listar", "lista de", "quais materias", "quais matérias",
    "quais disciplinas", "quais sao as", "quais são as", "todas as materias",
    "todas as matérias", "todas as disciplinas", "mostre as materias",
    "mostre as disciplinas", "me liste", "me mostre",
]

ORDINAIS_PERIODO = {
    "primeiro": "1", "segundo": "2", "terceiro": "3", "quarto": "4",
    "quinto": "5", "sexto": "6", "setimo": "7", "oitavo": "8",
    "nono": "9", "decimo": "10",
}

LABEL_CAMPO = {
    "cr": "Créditos",
    "ch": "Carga horária teórica",
    "apcc": "Carga horária de APCC (prática)",
    "total": "Carga horária total",
    "periodo": "Período",
    "prereq": "Pré-requisito(s)",
}


def norm(txt: str) -> str:
    if not txt:
        return ""
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("utf-8")
    txt = txt.lower()
    return re.sub(r"\s+", " ", txt).strip()


class BaseDisciplinas:
    """Índice em memória, por curso, de disciplina normalizada -> metadados.
    Construído a partir dos metadados já gravados no Chroma (não precisa
    reprocessar o PDF nem o tabela.py)."""

    def __init__(self):
        self.por_curso: dict[str, dict[str, dict]] = {}
        self.todas_por_curso: dict[str, list[dict]] = {}

    @classmethod
    def carregar(cls, db: "Chroma") -> "BaseDisciplinas":
        base = cls()
        registros = db.get(include=["metadatas"])
        metadatas = registros.get("metadatas", []) or []

        # Textos descritivos não são fichas: não possuem todos os campos.
        for meta in metadatas:
            if meta.get("tipo") not in {"disciplina", "disciplina_eletiva"}:
                continue
            base._adicionar(dict(meta))
        return base

    def _adicionar(self, meta):
        curso_id, nome = meta["curso"], meta["disciplina"]
        self.por_curso.setdefault(curso_id, {})[norm(nome)] = meta
        self.todas_por_curso.setdefault(curso_id, []).append(meta)

    @classmethod
    def dos_cursos(cls, cursos):
        """Dados canônicos, independentes da ordem e da versão do Chroma."""
        from cursos_config import carregar_tabela
        base = cls()
        for curso_id, info in cursos.items():
            modulo = carregar_tabela(info["pasta"])
            if modulo is None:
                continue
            for periodo, disciplinas in modulo.MATRIZ_CURRICULAR.items():
                for disciplina in disciplinas:
                    base._adicionar({**disciplina, "curso": curso_id, "periodo": periodo if periodo else None,
                                     "source": f"{info['pasta']}/tabela.py"})
            for disciplina in modulo.ELETIVAS:
                base._adicionar({**disciplina, "curso": curso_id,
                                 "source": f"{info['pasta']}/tabela.py"})
        return base

    def buscar_disciplina(self, curso_id: str, pergunta_normalizada: str, corte: float = 0.86):
        registros = self.todas_por_curso.get(curso_id, [])
        nomes = {norm(m["disciplina"]) for m in registros}
        exatos = [n for n in nomes if re.search(r"(?<!\w)" + re.escape(n) + r"(?!\w)", pergunta_normalizada)]
        # Um nome curto pode estar contido em outro (ex.: Educação Inclusiva).
        exatos = [n for n in exatos if not any(n != outro and n in outro for outro in exatos)]
        if len(exatos) > 1:
            return None  # Comparações exigem uma resposta com mais de uma ficha.
        if exatos:
            melhor = exatos[0]
        else:
            palavras = pergunta_normalizada.split()
            scores = []
            for nome in nomes:
                tam = len(nome.split())
                janelas = [" ".join(palavras[i:i + tam]) for i in range(len(palavras) - tam + 1)]
                # Não confundir sequências de disciplinas, como Cálculo I e IV.
                sufixo = nome.split()[-1]
                if re.fullmatch(r"[ivx]+|\d+", sufixo):
                    janelas = [j for j in janelas if j.split()[-1] == sufixo]
                score = max((difflib.SequenceMatcher(None, nome, j).ratio() for j in janelas), default=0)
                scores.append((score, nome))
            scores.sort(reverse=True)
            if not scores or scores[0][0] < corte:
                return None
            if len(scores) > 1 and scores[0][0] - scores[1][0] < 0.08:
                return None
            melhor = scores[0][1]
        candidatos = [m for m in registros if norm(m["disciplina"]) == melhor]
        periodo = detectar_periodo_alvo(pergunta_normalizada)
        if periodo:
            candidatos = [m for m in candidatos if str(m.get("periodo")) == periodo]
        return candidatos[0] if len(candidatos) == 1 else None

    def listar_por_periodo(self, curso_id: str, periodo_alvo: str) -> list:
        todas = self.todas_por_curso.get(curso_id, [])
        encontradas = [m for m in todas if str(m.get("periodo", "")) == periodo_alvo]
        return sorted(encontradas, key=lambda m: m.get("disciplina", ""))


def detectar_intencao(pergunta_normalizada: str):
    q = norm(pergunta_normalizada)
    if re.search(
        r"\b(?:tranca|trancam|bloqueia|bloqueiam|desbloqueia|libera|liberam)\b"
        r"|(?:nao posso|nao consigo|fico sem|impede de).*(?:fazer|cursar|disciplina|materia)"
        r"|(?:importante|necessaria|necessario).*(?:fazer|cursar|disciplina|materia)"
        r"|(?:quais|que)\s+(?:disciplinas|materias).*(?:dependem|exigem|reprov)"
        r"|(?:pre-requisito|pre requisito|prerequisito)\s+(?:de|para)\s+quais"
        r"|dependem diretamente de", q
    ):
        return "dependentes"
    encontrados = set()
    for campo, palavras in CAMPO_POR_INTENCAO.items():
        if any(norm(pc) in q for pc in palavras):
            encontrados.add(campo)
    if "horas teoricas" in q or "carga horaria teorica" in q:
        encontrados.discard("total")
        encontrados.add("ch")
    elif "total" in encontrados:
        encontrados.discard("ch")
    if "apcc" in encontrados:
        encontrados.discard("total")
    if encontrados - {"periodo"}:
        encontrados.discard("periodo")
    return next(iter(encontrados)) if len(encontrados) == 1 else None


def detectar_periodo_alvo(pergunta_normalizada: str):
    q = norm(pergunta_normalizada)
    ordinais = "|".join(ORDINAIS_PERIODO)
    m = re.search(r"\b(" + ordinais + r")\s+(?:periodo|semestre)\b", q)
    if m:
        return ORDINAIS_PERIODO[m.group(1)]
    m = re.search(r"\b(\d+)\s*o?\s*(?:periodo|semestre)\b", q)
    if m:
        return m.group(1)
    m = re.search(r"\b(?:periodo|semestre)\s*(\d+)\b", q)
    return m.group(1) if m else None


def eh_pergunta_de_listagem(pergunta_normalizada: str) -> bool:
    return any(p in pergunta_normalizada for p in PALAVRAS_LISTAGEM)


def formatar_tabela(headers: list, linhas: list) -> str:
    def linha(valores):
        return "| " + " | ".join(str(v).replace("|", "\\|").replace("\n", " ") for v in valores) + " |"
    return "\n".join([linha(headers), linha(["---"] * len(headers)), *(linha(l) for l in linhas)])


def responder_listagem(pergunta: str, base: BaseDisciplinas, curso_id: str):
    q_norm = norm(pergunta)
    if not eh_pergunta_de_listagem(q_norm):
        return None

    periodo_alvo = detectar_periodo_alvo(q_norm)
    if periodo_alvo is None:
        return None

    disciplinas = base.listar_por_periodo(curso_id, periodo_alvo)
    if not disciplinas:
        return f"Não encontrei disciplinas cadastradas para o {periodo_alvo}º período nesse curso."

    linhas = [
        [m.get("disciplina", ""), m.get("cr") if m.get("cr") is not None else "Não informado", m.get("total") if m.get("total") is not None else "Não informado", ", ".join(m.get("prereq", [])) if isinstance(m.get("prereq"), list) else (m.get("prereq") or "Não informado")]
        for m in disciplinas
    ]
    tabela = formatar_tabela(["Disciplina", "Créditos", "Carga Horária Total", "Pré-requisitos"], linhas)
    return f"No {periodo_alvo}º período, você encontra estas {len(disciplinas)} disciplinas:\n\n{tabela}\n\nO traço indica que não há pré-requisito cadastrado para a disciplina."


def responder_direto(pergunta: str, base: BaseDisciplinas, curso_id: str):
    q_norm = norm(pergunta)

    intencao = detectar_intencao(q_norm)
    if not intencao:
        return None

    disciplina_meta = base.buscar_disciplina(curso_id, q_norm)
    if not disciplina_meta:
        return None

    if intencao == "dependentes":
        nome = disciplina_meta["disciplina"]
        dependentes = []
        for ficha in base.todas_por_curso.get(curso_id, []):
            requisitos = ficha.get("prereq") or []
            if isinstance(requisitos, str):
                requisitos = [r.strip() for r in requisitos.split(",")]
            if any(norm(r) == norm(nome) for r in requisitos):
                dependentes.append(ficha["disciplina"])
        if not dependentes:
            return f"Não encontrei disciplinas que dependam diretamente de **{nome}** nos dados que tenho disponíveis."
        lista = "\n".join(f"- **{d}**" for d in sorted(set(dependentes)))
        return (
            f"Você precisa ter sido aprovado em **{nome}** para cursar estas disciplinas, "
            f"que dependem diretamente dela:\n\n{lista}\n\n"
            "Se você reprovar, precisará cumprir esse pré-requisito antes de cursá-las. "
            "Isso também pode atrasar disciplinas posteriores que dependam delas."
        )

    valor = disciplina_meta.get(intencao)

    nome = disciplina_meta.get("disciplina", "essa disciplina")
    if intencao == "prereq":
        if "prereq" not in disciplina_meta or valor is None:
            return f"Os pré-requisitos de **{nome}** não estão informados nos dados que tenho disponíveis."
        requisitos = valor if isinstance(valor, list) else [item.strip() for item in str(valor).split(",") if item.strip()]
        if not requisitos:
            return f"Não encontrei pré-requisitos cadastrados para **{nome}**."
        nomes = [f"**{requisito}**" for requisito in requisitos]
        lista = nomes[0] if len(nomes) == 1 else ", ".join(nomes[:-1]) + " e " + nomes[-1]
        return f"Para cursar **{nome}**, você precisa ter cursado {lista}, que {'é o pré-requisito dessa disciplina' if len(nomes) == 1 else 'são os pré-requisitos dessa disciplina'}."

    if valor is None or valor == "":
        return None
    if intencao == "cr":
        unidade = "crédito" if valor == 1 else "créditos"
        resposta = f"A disciplina **{nome}** tem **{valor} {unidade}**."
        if disciplina_meta.get("cr_estimado"):
            resposta += " Esse valor é estimado por equivalência de horas, pois os créditos não estão explícitos na tabela do PPC."
        return resposta
    if intencao == "periodo":
        return f"A disciplina **{nome}** faz parte do **{valor}º período** do curso."
    if intencao == "ch":
        return f"A disciplina **{nome}** tem **{valor}h de carga horária teórica**."
    if intencao == "apcc":
        return f"A disciplina **{nome}** tem **{valor}h de atividades práticas**."
    if intencao == "total":
        return f"A carga horária total de **{nome}** é de **{valor}h**."
    return None


def responder_estruturado(pergunta: str, base: BaseDisciplinas, curso_id: str):
    """Tenta listagem e resposta direta por metadados (sem LLM). Retorna
    None se nenhuma camada souber responder — sinal para cair no RAG+LLM."""
    resposta = responder_listagem(pergunta, base, curso_id)
    if resposta is not None:
        return resposta
    return responder_direto(pergunta, base, curso_id)

def resolver_continuacao(pergunta: str, historico: list, base: BaseDisciplinas, curso_id: str):
    """Resolve referências curtas antes da consulta estruturada e da busca RAG.

    Retorna (pergunta explícita, esclarecimento). Referências ambíguas nunca
    são enviadas ao modelo para escolher uma disciplina por conta própria.
    """
    q = norm(pergunta)
    referencia = re.search(
        r"\b(?:ess[ae](?:\s+(?:dai|ai|disciplina|materia))?|dess[ae]|ness[ae]|ela|dela|nela|a anterior)\b", q
    )
    cursar = bool(re.search(r"\b(?:cursar|ter cursado)\b", q))
    continuacao = referencia or (q.startswith('e ') and cursar)
    if not continuacao:
        return pergunta, None

    # Uma disciplina escrita pelo usuário tem prioridade sobre os pronomes.
    explicita = base.buscar_disciplina(curso_id, q)
    if explicita:
        if cursar and detectar_intencao(q) is None:
            return f"Quais são os pré-requisitos de {explicita['disciplina']}?", None
        return pergunta, None

    if not historico or historico[-1].get('role') != 'assistant':
        return pergunta, 'De qual disciplina você quer saber? Pode me dizer o nome dela?'

    if not base.todas_por_curso.get(curso_id):
        # Cursos novos ainda não têm uma matriz estruturada. Levar o contexto
        # da conversa atual à busca evita pesquisar somente um pronome.
        anterior = next((m.get('content', '') for m in reversed(historico) if m.get('role') == 'user'), '')
        if not anterior:
            return pergunta, 'De qual disciplina você quer saber? Pode me dizer o nome dela?'
        resposta_anterior = historico[-1].get('content', '')
        return (
            f"{pergunta}\nContexto da conversa: {anterior[:1500]}\n"
            f"Resposta anterior, apenas para identificar o assunto: {resposta_anterior[:1500]}", None
        )

    texto = norm(historico[-1].get('content', '').replace('**', ''))
    # Após listar dependentes, o assunto continua sendo a matéria de origem.
    if texto.startswith('voce precisa ter sido aprovado em '):
        texto = texto.split(' para cursar estas disciplinas', 1)[0]
    # Na resposta sobre pré-requisitos, "essa daí" aponta para o requisito
    # apresentado, não para a disciplina da pergunta anterior.
    marcador = re.search(r'precisa ter cursado\s+', texto)
    if marcador:
        texto = texto[marcador.end():].split(', que ', 1)[0]
    nomes = {m['disciplina'] for m in base.todas_por_curso.get(curso_id, [])}
    encontrados = [nome for nome in nomes if re.search(r'(?<!\w)' + re.escape(norm(nome)) + r'(?!\w)', texto)]
    encontrados = [nome for nome in encontrados if not any(
        nome != outro and norm(nome) in norm(outro) for outro in encontrados
    )]
    if len(encontrados) != 1:
        if encontrados:
            opcoes = ', '.join(f'**{nome}**' for nome in sorted(encontrados))
            return pergunta, f'Você quer saber de qual destas disciplinas: {opcoes}?'
        return pergunta, 'De qual disciplina você quer saber? Pode me dizer o nome dela?'

    nome = encontrados[0]
    intencao = detectar_intencao(q)
    if intencao is None and cursar:
        intencao = 'prereq'
    # Herdar a intenção só em elipses curtas; uma pergunta nova não deve
    # virar novamente "carga horária" apenas porque esse era o assunto anterior.
    if intencao is None and re.fullmatch(
        r"(?:e\s+)?(?:ela|essa|esse|essa dai|essa ai|dela|nela|e essa)[?!.\s]*", q
    ):
        ultima_pergunta = next((m.get('content', '') for m in reversed(historico) if m.get('role') == 'user'), '')
        intencao = detectar_intencao(norm(ultima_pergunta))
    consultas = {
        'dependentes': 'Quais disciplinas dependem diretamente',
        'prereq': 'Quais são os pré-requisitos', 'cr': 'Quantos créditos tem',
        'ch': 'Qual a carga horária teórica', 'apcc': 'Quantas horas práticas tem',
        'total': 'Qual a carga horária total', 'periodo': 'Qual o período',
    }
    if intencao not in consultas:
        return f'{pergunta.rstrip('? .')} (sobre a disciplina {nome})?', None
    return f'{consultas[intencao]} de {nome}?', None
