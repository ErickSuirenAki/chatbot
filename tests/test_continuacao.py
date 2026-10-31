import unittest
from cursos_config import CURSOS
from resposta_estruturada import BaseDisciplinas, resolver_continuacao, responder_estruturado


class ContinuacaoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = BaseDisciplinas.dos_cursos(CURSOS)
        cls.curso = 'ciencia_computacao'

    def historico(self, nome):
        pergunta = f'Qual pré-requisito de {nome}?'
        resposta = responder_estruturado(pergunta, self.base, self.curso)
        self.assertIsNotNone(resposta)
        return [{'role': 'user', 'content': pergunta}, {'role': 'assistant', 'content': resposta}]

    def test_cadeia_de_prerequisitos(self):
        historico = self.historico('Programação para Dispositivos Móveis')
        for esperado in ['Programação Orientada a Objetos', 'Programação I']:
            pergunta, esclarecer = resolver_continuacao('e pra cursar essa dai?', historico, self.base, self.curso)
            self.assertIsNone(esclarecer)
            self.assertIn(esperado, pergunta)
            resposta = responder_estruturado(pergunta, self.base, self.curso)
            self.assertIn(esperado, resposta)
            self.assertNotIn('Tecnologias de Ensino', resposta)
            historico.extend([{'role': 'user', 'content': 'e pra cursar essa dai?'}, {'role': 'assistant', 'content': resposta}])
        self.assertIn('Não encontrei pré-requisitos', resposta)

    def test_varios_requisitos_pede_esclarecimento(self):
        pergunta, esclarecer = resolver_continuacao('e pra cursar essa dai?', self.historico('Sistemas Distribuídos'), self.base, self.curso)
        self.assertIsNotNone(esclarecer)
        self.assertIn('Sistemas Operacionais', esclarecer)
        self.assertIn('Programação Orientada a Objetos', esclarecer)

    def test_muda_intencao_sem_trocar_disciplina(self):
        pergunta, esclarecer = resolver_continuacao('e quantos créditos ela tem?', self.historico('Programação para Dispositivos Móveis'), self.base, self.curso)
        self.assertIsNone(esclarecer)
        self.assertIn('Programação Orientada a Objetos', pergunta)
        self.assertIn('5 créditos', responder_estruturado(pergunta, self.base, self.curso))

    def test_nao_utiliza_outra_conversa_ou_curso(self):
        for historico, curso in [([], self.curso), (self.historico('Programação para Dispositivos Móveis'), 'pedagogia')]:
            _, esclarecer = resolver_continuacao('e pra cursar essa dai?', historico, self.base, curso)
            self.assertIsNotNone(esclarecer)

    def test_disciplina_explicita_tem_prioridade(self):
        pergunta, esclarecer = resolver_continuacao('e pra cursar Banco de Dados II?', self.historico('Programação para Dispositivos Móveis'), self.base, self.curso)
        self.assertIsNone(esclarecer)
        resposta = responder_estruturado(pergunta, self.base, self.curso)
        self.assertIn('Banco de Dados I', resposta)
        self.assertNotIn('Programação Orientada', resposta)

    def test_nao_recupera_assunto_antigo_depois_de_mudanca(self):
        historico = self.historico('Programação para Dispositivos Móveis')
        historico += [{'role': 'user', 'content': 'Qual o objetivo do curso?'}, {'role': 'assistant', 'content': 'O curso forma profissionais da computação.'}]
        _, esclarecer = resolver_continuacao('e pra cursar essa dai?', historico, self.base, self.curso)
        self.assertIsNotNone(esclarecer)


    def test_sequencia_carga_horaria_e_bloqueios(self):
        historico = self.historico('Estrutura de Dados I')
        perguntas = [
            'e qual a carga horária dessa?',
            'ela é importante pra fazer quais disciplinas?',
            'ela tranca quais disciplinas?',
            'quais disciplinas nao posso fazer se reprovei nela',
        ]
        for indice, texto in enumerate(perguntas):
            with self.subTest(pergunta=texto):
                consulta, esclarecer = resolver_continuacao(texto, historico, self.base, self.curso)
                self.assertIsNone(esclarecer)
                self.assertIn('Programação I', consulta)
                resposta = responder_estruturado(consulta, self.base, self.curso)
                self.assertIsNotNone(resposta)
                if indice == 0:
                    self.assertIn('100h', resposta)
                else:
                    for disciplina in ['Programação II', 'Estrutura de Dados I', 'Programação Orientada a Objetos', 'Cálculo Numérico']:
                        self.assertIn(f'**{disciplina}**', resposta)
                    self.assertNotIn('100h', resposta)
                    self.assertIn('diretamente', resposta)
                    self.assertNotIn('**Estrutura de Dados II**', resposta)
                historico.extend([{'role': 'user', 'content': texto}, {'role': 'assistant', 'content': resposta}])

    def test_pergunta_nova_nao_herda_carga_horaria(self):
        historico = [
            {'role': 'user', 'content': 'Qual a carga horária de Programação I?'},
            {'role': 'assistant', 'content': 'A disciplina **Programação I** tem **100h de carga horária teórica**.'},
        ]
        consulta, esclarecer = resolver_continuacao('ela é difícil de aprender?', historico, self.base, self.curso)
        self.assertIsNone(esclarecer)
        self.assertIn('difícil de aprender', consulta)
        self.assertIn('Programação I', consulta)
        self.assertIsNone(responder_estruturado(consulta, self.base, self.curso))

    def test_dependencias_explicitas_e_isoladas_por_curso(self):
        resposta = responder_estruturado('Programação I tranca quais disciplinas?', self.base, self.curso)
        self.assertIn('**Cálculo Numérico**', resposta)
        self.assertIsNone(responder_estruturado('Programação I tranca quais disciplinas?', self.base, 'pedagogia'))

    def test_sem_dependentes_nao_inventa_bloqueios(self):
        resposta = responder_estruturado('Programação para Dispositivos Móveis tranca quais disciplinas?', self.base, self.curso)
        self.assertIn('Não encontrei disciplinas', resposta)


    def test_curso_sem_tabela_leva_contexto_para_busca(self):
        base = BaseDisciplinas()
        historico = [
            {'role': 'user', 'content': 'Qual o pré-requisito de Direito Civil II?'},
            {'role': 'assistant', 'content': 'Para cursá-la, você precisa ter cursado Direito Civil I.'},
        ]
        consulta, esclarecer = resolver_continuacao('e qual a carga horária dessa?', historico, base, 'direito_novo')
        self.assertIsNone(esclarecer)
        self.assertIn('Direito Civil I', consulta)
        self.assertIn('carga horária', consulta)
