"""Documentos de busca derivados das matrizes, preservando campos não informados."""
import unicodedata
from langchain_core.documents import Document


def normalizar(texto: str) -> str:
    return unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('ascii').lower()


def _valor(valor):
    return 'Não informado' if valor is None else str(valor)


def _requisitos(d):
    requisitos = d.get('prereq')
    if requisitos is None:
        return 'Pré-requisitos não informados na matriz'
    if not requisitos:
        return 'Nenhum pré-requisito indicado na matriz'
    return ', '.join(requisitos)


def _ficha(d):
    linhas = [f"Nome: {d['disciplina']}"]
    for campo, titulo in [('cr', 'Créditos'), ('ch', 'Carga horária teórica'),
                          ('apcc', 'Carga horária prática'), ('total', 'Carga horária total')]:
        valor = _valor(d.get(campo))
        if campo == 'cr' and d.get('cr_estimado'):
            valor += ' (estimados por equivalência de horas)'
        linhas.append(f'{titulo}: {valor}')
    linhas.append(_requisitos(d))
    if d.get('prereq_condicao'):
        linhas.append('Outras condições: ' + d['prereq_condicao'])
    return '\n'.join(linhas)


def _metadados(curso_id, d, tipo, periodo=None):
    meta = {'tipo': tipo, 'curso': curso_id, 'disciplina': d['disciplina'],
            'source': f'cursos/{curso_id}/tabela.py'}
    if periodo:
        meta['periodo'] = periodo
    for campo in ['cr', 'ch', 'apcc', 'total', 'cr_estimado', 'pagina_pdf', 'codigo', 'prereq_condicao']:
        if d.get(campo) is not None:
            meta[campo] = d[campo]
    if d.get('prereq') is not None:
        meta['prereq'] = ', '.join(d['prereq'])
    return meta


def tabelas_para_documents(curso_id: str, curso_nome: str, matriz_curricular: dict, eletivas: list) -> list[Document]:
    docs = []
    for periodo, disciplinas in matriz_curricular.items():
        titulo = f'{periodo}º período' if periodo else 'Período não informado'
        linhas = [f'Matriz curricular — {curso_nome} — {titulo}', '',
                  '| Disciplina | Créditos | Teoria | Prática | Total | Pré-requisitos |',
                  '| --- | --- | --- | --- | --- | --- |']
        for d in disciplinas:
            linhas.append('| ' + ' | '.join([d['disciplina'], *[_valor(d.get(c)) for c in ['cr', 'ch', 'apcc', 'total']], _requisitos(d)]) + ' |')
            docs.append(Document(page_content=f'Curso: {curso_nome}\nPeríodo: {titulo}\n' + _ficha(d),
                                 metadata=_metadados(curso_id, d, 'disciplina', periodo)))
        meta = {'tipo': 'tabela_periodo', 'curso': curso_id, 'source': f'cursos/{curso_id}/tabela.py'}
        if periodo:
            meta['periodo'] = periodo
        docs.append(Document(page_content='\n'.join(linhas), metadata=meta))
    for d in eletivas:
        docs.append(Document(page_content=f'Curso: {curso_nome}\nDisciplina eletiva/optativa; período conforme oferta.\n' + _ficha(d),
                             metadata=_metadados(curso_id, d, 'disciplina_eletiva')))
    return docs


def gerar_docs_descritivos(curso_id: str, curso_nome: str, matriz_curricular: dict, eletivas: list) -> list[Document]:
    docs = []
    for periodo, disciplinas in matriz_curricular.items():
        for d in disciplinas:
            partes = [f"A disciplina {d['disciplina']} faz parte do curso de {curso_nome}."]
            if periodo:
                partes.append(f'É oferecida no {periodo}º período.')
            if d.get('cr') is not None:
                estimado = ' estimados por equivalência de horas' if d.get('cr_estimado') else ''
                partes.append(f"Tem {d['cr']} créditos{estimado}.")
            for campo, descricao in [('ch', 'carga horária teórica'), ('apcc', 'carga horária prática'), ('total', 'carga horária total')]:
                if d.get(campo) is not None:
                    partes.append(f"A {descricao} é de {d[campo]} horas.")
            partes.append(_requisitos(d) + '.')
            if d.get('prereq_condicao'):
                partes.append(d['prereq_condicao'])
            docs.append(Document(page_content=' '.join(partes), metadata=_metadados(curso_id, d, 'descritivo_disciplina', periodo)))
    for d in eletivas:
        docs.append(Document(page_content=f"{d['disciplina']} é uma opção eletiva/optativa do curso de {curso_nome}.\n" + _ficha(d),
                             metadata=_metadados(curso_id, d, 'descritivo_eletiva')))
    return docs
