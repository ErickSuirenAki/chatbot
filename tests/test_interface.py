"""Teste da interface com dependências pesadas simuladas; exige Streamlit."""
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

try:
    from streamlit.testing.v1 import AppTest
    import requests
except ImportError:
    AppTest = None


class BancoSimulado:
    def __init__(self, **kwargs):
        pass

    def get(self, **kwargs):
        return {'ids': ['teste']}

    def as_retriever(self, **kwargs):
        return self

    def invoke(self, pergunta):
        return [types.SimpleNamespace(page_content='O curso forma professores.', metadata={'source': 'ppc.pdf'})]


@unittest.skipIf(AppTest is None, 'Streamlit não instalado neste interpretador')
class InterfaceTest(unittest.TestCase):
    def test_consulta_e_falha_ollama(self):
        chroma = types.ModuleType('langchain_chroma')
        chroma.Chroma = BancoSimulado
        embeddings = types.ModuleType('langchain_huggingface')
        embeddings.HuggingFaceEmbeddings = lambda **kwargs: object()
        with tempfile.TemporaryDirectory() as pasta:
            (Path(pasta) / 'chroma.sqlite3').touch()
            with patch.dict(sys.modules, {'langchain_chroma': chroma, 'langchain_huggingface': embeddings}), patch('banco_utils.caminho_banco', return_value=Path(pasta)):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'appOllamaLocal.py'), default_timeout=15).run()
                self.assertFalse(app.exception)
                with patch('requests.post') as ollama:
                    app.chat_input[0].set_value('Qual pré-requisito de programação pra dispositivos móveis?').run()
                    self.assertFalse(app.exception)
                    app.chat_input[0].set_value('e pra cursar essa dai?').run()
                    self.assertFalse(app.exception)
                    historico = app.session_state['todas_conversas']['ciencia_computacao']
                    resposta = next(iter(historico.values()))['mensagens'][-1]['content']
                    self.assertIn('Para cursar **Programação Orientada a Objetos**', resposta)
                    self.assertIn('**Programação I**', resposta)
                    self.assertNotIn('Tecnologias de Ensino', resposta)
                    for pergunta in [
                        'e qual a carga horária dessa?',
                        'ela é importante pra fazer quais disciplinas?',
                        'ela tranca quais disciplinas?',
                        'quais disciplinas nao posso fazer se reprovei nela',
                    ]:
                        app.chat_input[0].set_value(pergunta).run()
                        self.assertFalse(app.exception)
                    resposta = next(iter(app.session_state['todas_conversas']['ciencia_computacao'].values()))['mensagens'][-1]['content']
                    for disciplina in ['Programação II', 'Estrutura de Dados I', 'Programação Orientada a Objetos', 'Cálculo Numérico']:
                        self.assertIn(f'**{disciplina}**', resposta)
                    self.assertNotIn('100h', resposta)
                    ollama.assert_not_called()
                app.sidebar.selectbox(key='curso').select('Pedagogia — Licenciatura — Ji-Paraná — PPC 2018').run()
                app.chat_input[0].set_value('Quantas horas teóricas tem Metodologia da Pesquisa Científica?').run()
                self.assertFalse(app.exception)
                self.assertTrue(any('60h' in item.value for item in app.markdown))
                with patch('requests.post', side_effect=requests.ConnectionError('offline')):
                    app.chat_input[0].set_value('Qual o objetivo do curso?').run()
                self.assertFalse(app.exception)
                self.assertTrue(app.error)
                self.assertIn('Ollama', app.error[0].value)
                app.sidebar.selectbox(key='campus').select('Ariquemes').run()
                self.assertFalse(app.exception)
                self.assertTrue(all('Ariquemes' in nome for nome in app.sidebar.selectbox(key='curso').options))
                # Outra sessão não recebe as conversas da primeira.
                outra = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'appOllamaLocal.py'), default_timeout=15).run()
                self.assertFalse(outra.exception)
                for conversas in outra.session_state['todas_conversas'].values():
                    self.assertTrue(all(not c['mensagens'] for c in conversas.values()))
