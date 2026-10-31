import json
from pathlib import Path
import tempfile
import unittest

from banco_utils import caminho_banco, publicar_banco
from cursos_config import CURSOS
from historico import carregar_todas_conversas, salvar_todas_conversas
from resposta_estruturada import (
    BaseDisciplinas, detectar_intencao, detectar_periodo_alvo, norm,
    responder_estruturado,
)


class RespostasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = BaseDisciplinas.dos_cursos(CURSOS)

    def test_horas_teoricas_nao_sao_total(self):
        resposta = responder_estruturado(
            'Quantas horas teóricas tem Metodologia da Pesquisa Científica?', self.base, 'pedagogia')
        self.assertIn('60h', resposta)
        self.assertIn('teórica', resposta)

    def test_optativas_repetidas_sao_preservadas(self):
        from cursos.pedagogia.tabela import MATRIZ_CURRICULAR
        for periodo, disciplinas in MATRIZ_CURRICULAR.items():
            with self.subTest(periodo=periodo):
                self.assertEqual(len(self.base.listar_por_periodo('pedagogia', str(periodo))), len(disciplinas))

    def test_nono_semestre(self):
        for texto in ['nono período', '9º semestre', 'semestre 9', '9º período']:
            self.assertEqual(detectar_periodo_alvo(norm(texto)), '9')
        self.assertIsNone(detectar_periodo_alvo(norm('segundo o PPC')))

    def test_ignora_metadados_descritivos_em_qualquer_ordem(self):
        ficha = {'tipo': 'disciplina', 'curso': 'teste', 'disciplina': 'Exemplo', 'periodo': 1, 'total': 80, 'cr': 4}
        descritivo = {'tipo': 'descritivo_disciplina', 'curso': 'teste', 'disciplina': 'Exemplo', 'periodo': 1}
        for ordem in [[ficha, descritivo], [descritivo, ficha]]:
            class DB:
                def get(self, **kwargs):
                    return {'metadatas': ordem}
            base = BaseDisciplinas.carregar(DB())
            self.assertEqual(base.listar_por_periodo('teste', '1')[0]['total'], 80)

    def test_nao_escolhe_uma_disciplina_em_comparacao(self):
        self.assertIsNone(self.base.buscar_disciplina('pedagogia', norm('créditos de Didática e LIBRAS')))

    def test_optativa_sem_periodo_e_ambigua(self):
        self.assertIsNone(self.base.buscar_disciplina('pedagogia', norm('quantos créditos tem Optativa?')))

    def test_nao_confunde_numerais(self):
        base = BaseDisciplinas()
        base._adicionar({'curso': 'teste', 'disciplina': 'Cálculo I'})
        self.assertIsNone(base.buscar_disciplina('teste', norm('créditos de Cálculo IV')))

    def test_multiplos_campos_nao_retornam_resposta_parcial(self):
        self.assertIsNone(detectar_intencao(norm('créditos e carga horária de Didática')))

    def test_credito_estimado_e_identificado(self):
        resposta = responder_estruturado('Quantos créditos tem Psicopedagogia e educação?', self.base, 'pedagogia')
        self.assertIn('estimado', resposta)

    def test_prerequisito_ausente_nao_significa_nenhum(self):
        base = BaseDisciplinas()
        base._adicionar({'curso': 'teste', 'disciplina': 'Exemplo'})
        resposta = responder_estruturado('Qual pré-requisito de Exemplo?', base, 'teste')
        self.assertIn('não estão informados', resposta)


class PersistenciaTest(unittest.TestCase):
    def test_sessoes_nao_carregam_historico_global(self):
        self.assertEqual(carregar_todas_conversas(), {})
        salvar_todas_conversas({'privado': 'não gravar implicitamente'})

    def test_exportacao_e_leitura_explicitas(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = str(Path(pasta) / 'historico.json')
            dados = {'pedagogia': {'abc': {'mensagens': []}}}
            salvar_todas_conversas(dados, arquivo)
            self.assertEqual(carregar_todas_conversas(arquivo), dados)

    def test_json_corrompido_nao_e_ocultado(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'historico.json'
            arquivo.write_text('{quebrado')
            with self.assertRaises(json.JSONDecodeError):
                carregar_todas_conversas(str(arquivo))

    def test_falha_na_indexacao_preserva_base_ativa(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta) / 'chroma_db'
            anterior = publicar_banco(lambda destino: (destino / 'dados').write_text('anterior'), raiz)
            def falhar(destino):
                (destino / 'dados').write_text('incompleto')
                raise RuntimeError('falha simulada')
            with self.assertRaises(RuntimeError):
                publicar_banco(falhar, raiz)
            self.assertEqual(caminho_banco(raiz), anterior)
            self.assertEqual((anterior / 'dados').read_text(), 'anterior')
            self.assertEqual(len(list((raiz / 'versoes').iterdir())), 1)

    def test_base_legada_funciona_sem_manifesto(self):
        self.assertEqual(caminho_banco('/tmp/base-legada'), Path('/tmp/base-legada'))


if __name__ == '__main__':
    unittest.main()
