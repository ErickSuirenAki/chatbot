import json
from pathlib import Path
import tempfile
import unittest
from cursos_config import carregar_cursos, carregar_tabela
from resposta_estruturada import BaseDisciplinas


class CadastroCursosTest(unittest.TestCase):
    def cadastrar(self, raiz, identificador, **campos):
        pasta = Path(raiz) / identificador
        pasta.mkdir()
        (pasta / 'ppc.pdf').write_bytes(b'%PDF-1.7\n')
        dados = {'nome': 'Curso de exemplo', 'campus': 'Campus A', 'versao': 'Matriz 2025', **campos}
        (pasta / 'curso.json').write_text(json.dumps(dados), encoding='utf-8')
        return pasta

    def test_mesmo_curso_em_campi_e_versoes_distintos(self):
        with tempfile.TemporaryDirectory() as raiz:
            self.cadastrar(raiz, 'curso_a_2025')
            self.cadastrar(raiz, 'curso_b_2025', campus='Campus B')
            self.cadastrar(raiz, 'curso_a_2020', versao='Matriz 2020')
            cursos = carregar_cursos(raiz, existentes={})
            self.assertEqual(len(cursos), 3)
            self.assertEqual(len({info['nome'] for info in cursos.values()}), 3)
            self.assertEqual(BaseDisciplinas.dos_cursos(cursos).todas_por_curso, {})

    def test_pdf_nao_exige_tabela_manual(self):
        with tempfile.TemporaryDirectory() as raiz:
            pasta = self.cadastrar(raiz, 'exemplo')
            self.assertIsNone(carregar_tabela(pasta))
            self.assertIn('exemplo', carregar_cursos(raiz, existentes={}))

    def test_exige_campus_versao_e_pdf(self):
        for campo in ['campus', 'versao', 'nome']:
            with self.subTest(campo=campo), tempfile.TemporaryDirectory() as raiz:
                self.cadastrar(raiz, 'exemplo', **{campo: ''})
                with self.assertRaises(ValueError):
                    carregar_cursos(raiz, existentes={})
        with tempfile.TemporaryDirectory() as raiz:
            pasta = self.cadastrar(raiz, 'exemplo')
            (pasta / 'ppc.pdf').unlink()
            with self.assertRaises(ValueError):
                carregar_cursos(raiz, existentes={})

    def test_cadastro_duplicado_nao_sobrescreve_existente(self):
        with tempfile.TemporaryDirectory() as raiz:
            self.cadastrar(raiz, 'existente')
            with self.assertRaises(ValueError):
                carregar_cursos(raiz, existentes={'existente': {'nome': 'Já cadastrado'}})


    def test_referencia_pdf_original_sem_duplicar_arquivo(self):
        with tempfile.TemporaryDirectory() as raiz:
            original = Path(raiz) / 'original.pdf'
            original.write_bytes(b'%PDF-1.7\n')
            pasta = Path(raiz) / 'cadastro'
            pasta.mkdir()
            (pasta / 'curso.json').write_text(json.dumps({
                'nome': 'Curso', 'campus': 'Campus A', 'versao': 'PPC 2025',
                'arquivo_pdf': str(original),
            }))
            cursos = carregar_cursos(raiz, existentes={})
            self.assertEqual(cursos['cadastro']['arquivo_pdf'], str(original))
            self.assertFalse((pasta / 'ppc.pdf').exists())

    def test_pdf_modificado_exige_revisao(self):
        from processar_pdf import validar_documentos
        with tempfile.TemporaryDirectory() as raiz:
            arquivo = Path(raiz) / 'ppc.pdf'
            arquivo.write_bytes(b'%PDF-1.7\n')
            cursos = {'teste': {'pasta': raiz, 'arquivo_pdf': str(arquivo), 'pdf_sha256': 'invalido'}}
            with self.assertRaisesRegex(ValueError, 'mudou desde a identificação'):
                validar_documentos(cursos)

    def test_arquivo_com_extensao_pdf_sem_cabecalho_e_rejeitado(self):
        from processar_pdf import validar_documentos
        with tempfile.TemporaryDirectory() as raiz:
            arquivo = Path(raiz) / 'ppc.pdf'
            arquivo.write_text('nao e PDF')
            with self.assertRaisesRegex(ValueError, 'não parece ser um PDF'):
                validar_documentos({'teste': {'pasta': raiz}})
