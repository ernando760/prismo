"""Contrato documental e distribuição; não simulam julgamento visual de um agente."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'skills/prismo'


class CreateGuidanceTests(unittest.TestCase):
    def test_creation_phases_preserve_approval_before_mutation(self):
        text = (ROOT / 'references/create.md').read_text()
        phases = re.findall(r'^## (.+)$', text, re.M)
        self.assertEqual(phases[:6], [
            'Investigar', 'Projetar', 'Aprovar', 'Implementar', 'Inspecionar', 'Validar'])
        approval = text.split('## Aprovar\n')[1].split('## Implementar\n')[0]
        self.assertIn('Aguarde aprovação', approval)
        self.assertIn('tokens/dependências não apresentados', approval)

    def test_visual_reference_is_conditional_and_not_globally_loaded(self):
        entry = (ROOT / 'SKILL.md').read_text()
        self.assertNotIn('visual-design.md', entry)
        creation = (ROOT / 'references/create.md').read_text()
        design = creation.split('## Projetar\n')[1].split('## Aprovar\n')[0]
        self.assertIn('[visual-design.md](visual-design.md)', design)
        self.assertIn('tarefas exclusivamente técnicas', design)
        callers = {p.name for p in (ROOT / 'references').glob('*.md')
                   if p.name != 'visual-design.md' and 'visual-design.md' in p.read_text()}
        self.assertEqual(callers, {'create.md'})

    def test_visual_evidence_is_not_inferred_from_technical_checks(self):
        text = (ROOT / 'references/create.md').read_text()
        inspection = text.split('## Inspecionar\n')[1].split('## Validar\n')[0]
        self.assertIn('não declare o componente visualmente', inspection)
        self.assertIn('verificações\nmanuais pendentes', inspection)
        validation = text.split('## Validar\n')[1].split('## Helper')[0]
        for evidence in ('problemas comprovados', 'riscos potenciais',
                         'verificações manuais pendentes', 'colors.py contrast'):
            self.assertIn(evidence, validation)

    def test_state_comparison_and_icon_proportion_are_explicit(self):
        text = (ROOT / 'references/visual-design.md').read_text()
        interactions = text.split('## Interações e acessibilidade')[1].split('## Responsividade')[0]
        for state in ('default', 'hover', 'focus', 'error', 'disabled'):
            self.assertIn(state, interactions)
        self.assertIn('error com focus', interactions)
        self.assertIn('diferença perceptível', interactions)
        composition = text.split('## Hierarquia e composição')[1].split('## Tipografia')[0]
        for criterion in ('opticamente', 'proporção da área desenhada', 'em relação ao texto'):
            self.assertIn(criterion, composition)

    def test_token_generation_stays_in_proposal_before_approval(self):
        text = (ROOT / 'references/create.md').read_text()
        approval = text.split('## Aprovar\n')[1].split('## Implementar\n')[0]
        for constraint in ('gerador\ndeterminístico existente', 'preview calculado',
                           'sem persistir tokens antes da aprovação',
                           'tokens/dependências não apresentados'):
            self.assertIn(constraint, approval)

    def test_local_document_links_resolve(self):
        for path in [ROOT / 'SKILL.md', *ROOT.joinpath('references').glob('create*.md'),
                     ROOT / 'references/visual-design.md']:
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent / target.split('#')[0]).is_file(),
                                    f'{path}: {target}')


if __name__ == '__main__':
    unittest.main()
