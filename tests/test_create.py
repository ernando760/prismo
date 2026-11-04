"""Fluxos determinísticos de revisão; não são avaliação de diálogo ou componentes gerados."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'skills/prismo/scripts/create.py'
spec = importlib.util.spec_from_file_location('prismo_create', SCRIPT)
c = importlib.util.module_from_spec(spec)
with patch.object(sys, 'path', [str(SCRIPT.parent), *sys.path]):
    spec.loader.exec_module(c)


def plan(platform='web'):
    return json.loads((REPO / 'tests/fixtures/create' / (platform + '-plan.json')).read_text())


class CreateTests(unittest.TestCase):
    def test_distribution_requires_each_applicable_check_without_execution(self):
        p = plan()
        p['distribution'] = {'typescript': True, 'css': True, 'resolutions': ['NodeNext', 'Bundler']}
        result = c.review(self.root, p)
        self.assertEqual(result['status'], 'needs_input')
        expected = {'build', 'pack', 'exports', 'types', 'css', 'nodenext', 'bundler'}
        self.assertEqual(set(result['distribution']['required_checks']), expected)
        for kind in expected:
            p['checks'].append({'kind': kind, 'command': 'touch SHOULD_NOT_EXIST'})
        result = c.review(self.root, p)
        self.assertEqual(result['status'], 'proposal_ready')
        self.assertEqual(result['distribution']['validation'], 'not_run')
        self.assertFalse((self.root / 'SHOULD_NOT_EXIST').exists())
        for kind in expected:
            incomplete = copy.deepcopy(p)
            incomplete['checks'] = [x for x in p['checks'] if x['kind'] != kind]
            self.assertEqual(c.review(self.root, incomplete)['status'], 'needs_input', kind)

    def test_js_distribution_and_legacy_manifest(self):
        p = plan()
        p['distribution'] = {'typescript': False, 'css': False, 'resolutions': []}
        p['checks'] += [{'kind': k, 'command': 'existing-check'} for k in ('build', 'pack', 'exports')]
        self.assertEqual(c.review(self.root, p)['status'], 'proposal_ready')
        package = self.root / 'package.json'
        package.write_text(json.dumps({'private': True, 'exports': './dist/index.js', 'dependencies': {'react': '19'}}))
        legacy = c.review(self.root, plan())
        self.assertEqual(legacy['status'], 'proposal_ready')
        self.assertTrue(any('tarball' in w for w in legacy['warnings']))

    def test_distribution_rejects_invalid_contracts(self):
        valid = {'typescript': True, 'css': False, 'resolutions': ['NodeNext']}
        for key, value in [('typescript', 1), ('css', None), ('resolutions', ['NodeNext', 'NodeNext']),
                           ('resolutions', ['unknown']), ('resolutions', 'Bundler')]:
            p = plan(); p['distribution'] = {**valid, key: value}
            with self.assertRaises(ValueError): c.review(self.root, p)
        p = plan(); p['distribution'] = {**valid, 'typescript': False}
        with self.assertRaises(ValueError): c.review(self.root, p)
        p = plan(); p['distribution'] = None
        with self.assertRaises(ValueError): c.review(self.root, p)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='prismo create ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'; self.root.mkdir()
        self.record(['web'])
        (self.root / 'package.json').write_text(json.dumps({'dependencies': {'react': '18.3.1'}}))
        (self.root / '.storybook').mkdir(); (self.root / '.storybook/main.ts').write_text('export default {}')
        self.tokens = {'semantic': {'light': {'text': {'$type': 'color', '$value': {'colorSpace': 'srgb', 'components': [0, 0, 0]}}}}}
        self.save_tokens()

    def record(self, platforms):
        (self.root / 'design-system').mkdir(exist_ok=True)
        (self.root / 'design-system/decisions.json').write_text(json.dumps({'decisions': {'platforms': platforms, 'paths': {'tokens': 'design-system/tokens.json'}}}))

    def save_tokens(self):
        (self.root / 'design-system/tokens.json').write_text(json.dumps(self.tokens))

    def flutter(self):
        (self.root / 'package.json').unlink()
        (self.root / 'pubspec.yaml').write_text('name: fixture\ndependencies:\n  flutter:\n    sdk: flutter\n')
        (self.root / 'widgetbook/lib').mkdir(parents=True)
        (self.root / 'widgetbook/lib/main.dart').write_text('// configuração existente, não executada neste teste')
        self.record(['flutter'])

    def test_web_proposal_ready_still_requires_approval(self):
        result = c.review(self.root, plan())
        self.assertEqual(result['status'], 'proposal_ready')
        self.assertEqual(result['phase'], 'proposal')
        self.assertIn('component_proposal', result['approval_required'])
        self.assertTrue(result['catalog_configuration_found'])

    def test_equal_values_do_not_merge_distinct_semantic_bindings(self):
        # Papéis da fixture; igualdade numérica não representa aprovação semântica.
        self.tokens['semantic']['light']['selection'] = copy.deepcopy(self.tokens['semantic']['light']['text'])
        self.tokens['semantic']['light']['selection']['$description'] = 'Sinal de seleção da fixture'
        self.save_tokens()
        p = plan()
        p['tokens']['selection'] = {'path': 'semantic.light.selection', 'binding': 'var(--fixture-selection)'}
        before = (self.root / 'design-system/tokens.json').read_bytes()
        result = c.review(self.root, p)
        self.assertIn('semantic.light.text', result['checked_token_paths'])
        self.assertIn('semantic.light.selection', result['checked_token_paths'])
        self.assertIn('component_proposal', result['approval_required'])
        self.assertEqual((self.root / 'design-system/tokens.json').read_bytes(), before)

    def test_coexisting_state_requires_case_and_unresolved_meaning_blocks_proposal(self):
        p = plan(); p['states'].append('focus+selected')
        self.assertEqual(c.review(self.root, p)['status'], 'needs_input')
        p['cases'].append({'name': 'Coexistência da fixture', 'states': ['focus+selected'],
                           'assertions': ['Conferir sinais e bindings do contrato aprovado']})
        self.assertEqual(c.review(self.root, p)['status'], 'proposal_ready')
        p['questions'] = ['Qual significado deve ser preservado em cada canal visual nesta combinação?']
        self.assertEqual(c.review(self.root, p)['status'], 'needs_input')

    def test_flutter_only_inference_and_widgetbook(self):
        self.flutter(); p = plan('flutter'); p['platform'] = None
        result = c.review(self.root, p)
        self.assertEqual(result['platform'], 'flutter')
        self.assertEqual(result['status'], 'proposal_ready')

    def test_multiplatform_requires_choice_when_ambiguous(self):
        (self.root / 'pubspec.yaml').write_text('dependencies:\n  flutter:\n    sdk: flutter\n')
        self.record(['web', 'flutter']); p = plan(); p['platform'] = None
        self.assertEqual(c.review(self.root, p)['status'], 'needs_input')
        p['platform'] = 'web'
        self.assertEqual(c.review(self.root, p)['status'], 'proposal_ready')

    def test_declared_web_without_technology_is_not_implemented_implicitly(self):
        (self.root / 'package.json').unlink()
        result = c.review(self.root, plan())
        self.assertEqual(result['status'], 'needs_input')
        self.assertTrue(any('Tecnologia' in issue for issue in result['issues']))

    def test_platform_decision_mismatch_and_wrong_catalog(self):
        self.record(['flutter'])
        self.assertEqual(c.review(self.root, plan())['status'], 'needs_input')
        self.record(['web']); p = plan(); p['catalog']['tool'] = 'widgetbook'
        self.assertTrue(any('Catálogo incompatível' in i for i in c.review(self.root, p)['issues']))

    def test_missing_catalog_requires_setup_approval_without_installing(self):
        p = plan(); p['catalog']['config'] = None
        result = c.review(self.root, p)
        self.assertEqual(result['status'], 'proposal_ready')
        self.assertIn('catalog_setup', result['approval_required'])
        self.assertTrue(result['warnings'])

    def test_missing_decisions_and_tokens_require_input(self):
        (self.root / 'design-system/decisions.json').unlink()
        self.assertEqual(c.review(self.root, plan())['status'], 'needs_input')
        self.record(['web']); (self.root / 'design-system/tokens.json').unlink()
        self.assertEqual(c.review(self.root, plan())['status'], 'needs_input')

    def test_existing_component_is_not_overwritten(self):
        path = self.root / 'src/atoms/Button.tsx'; path.parent.mkdir(parents=True)
        path.write_text('preservar')
        result = c.review(self.root, plan())
        self.assertEqual(result['status'], 'needs_input')
        self.assertEqual(path.read_text(), 'preservar')

    def test_existing_file_modification_requires_specific_approval(self):
        p = plan(); path = self.root / p['files'][0]['path']; path.parent.mkdir(parents=True); path.write_text('original')
        p['files'][0]['action'] = 'modify'
        result = c.review(self.root, p)
        self.assertEqual(result['status'], 'proposal_ready')
        self.assertIn('modify:src/atoms/Button.tsx', result['approval_required'])
        self.assertEqual(path.read_text(), 'original')

    def test_missing_alias_cycles_and_incompatible_alias_types(self):
        for token in [None, {'$type': 'color', '$value': '{semantic.light.text}'}, {'$type': 'color', '$value': '{size}'}]:
            self.tokens = {'semantic': {'light': {}}, 'size': {'$type': 'dimension', '$value': {'value': 4, 'unit': 'px'}}}
            if token: self.tokens['semantic']['light']['text'] = token
            self.save_tokens()
            self.assertEqual(c.review(self.root, plan())['status'], 'needs_input')

    def test_new_semantic_alias_requires_token_diff_and_approval(self):
        p = plan(); p['tokens']['foreground']['path'] = 'semantic.button.foreground'
        p['new_tokens'] = [{'path': 'semantic.button.foreground', 'token': {'$type': 'color', '$value': '{semantic.light.text}'}, 'reason': 'Papel específico aprovado na proposta'}]
        self.assertEqual(c.review(self.root, p)['status'], 'needs_input')
        p['files'].append({'path': 'design-system/tokens.json', 'action': 'modify', 'role': 'tokens'})
        result = c.review(self.root, p)
        self.assertEqual(result['status'], 'proposal_ready')
        self.assertIn('token_changes', result['approval_required'])
        self.assertNotIn('button', json.loads((self.root / 'design-system/tokens.json').read_text())['semantic'])

    def test_new_token_collision_does_not_change_foundation(self):
        p = plan(); before = (self.root / 'design-system/tokens.json').read_bytes()
        p['new_tokens'] = [{'path': 'semantic.light.text', 'token': {'$type': 'color', '$value': {}}, 'reason': 'alterar'}]
        self.assertEqual(c.review(self.root, p)['status'], 'needs_input')
        self.assertEqual((self.root / 'design-system/tokens.json').read_bytes(), before)

    def test_unanswered_questions_and_atomic_classification_block_ready(self):
        p = plan(); p['questions'] = ['Qual comportamento de loading?']
        self.assertIn('Qual comportamento de loading?', c.review(self.root, p)['issues'])
        p['questions'] = []; p['atomic'] = None
        self.assertEqual(c.review(self.root, p)['status'], 'needs_input')

    def test_state_coverage_is_required(self):
        p = plan(); p['states'].append('loading')
        result = c.review(self.root, p)
        self.assertEqual(result['status'], 'needs_input')
        self.assertTrue(any('loading' in i for i in result['issues']))

    def test_functional_accessibility_and_required_artifacts(self):
        p = plan(); p['checks'] = [p['checks'][0]]; p['files'] = p['files'][:1]
        result = c.review(self.root, p)
        self.assertEqual(result['status'], 'needs_input')
        self.assertTrue(any('acessibilidade' in i for i in result['issues']))
        self.assertTrue(any('documentation' in i for i in result['issues']))

    def test_traversal_and_symlinks_rejected(self):
        p = plan(); p['files'][0]['path'] = '../outside.dart'
        with self.assertRaises(ValueError): c.review(self.root, p)
        p['files'][0]['path'] = 'linked/Button.tsx'; (self.root / 'linked').symlink_to(self.root.parent)
        with self.assertRaises(ValueError): c.review(self.root, p)

    def test_duplicate_paths_and_unknown_states(self):
        p = plan(); p['files'].append(copy.deepcopy(p['files'][0]))
        p['cases'][0]['states'] = ['unknown']
        self.assertEqual(c.review(self.root, p)['status'], 'needs_input')

    def test_unused_new_tokens_and_overlapping_files_require_revision(self):
        p = plan()
        p['new_tokens'] = [{'path': 'semantic.unused', 'token': {'$type': 'color', '$value': '{semantic.light.text}'}, 'reason': 'Revisar necessidade'}]
        p['files'].append({'path': 'design-system/tokens.json', 'action': 'modify', 'role': 'tokens'})
        p['files'].append({'path': 'src/atoms/Button.tsx/child.js', 'action': 'create', 'role': 'exports'})
        issues = c.review(self.root, p)['issues']
        self.assertTrue(any('sem binding/uso' in i for i in issues))
        self.assertTrue(any('sobrepostos' in i for i in issues))

    def test_template_is_not_a_ready_proposal(self):
        template = json.loads((REPO / 'skills/prismo/assets/templates/create-plan.json').read_text())
        self.assertEqual(c.review(self.root, template)['status'], 'needs_input')

    def test_cli_preserves_all_generated_foundations_and_never_executes_commands(self):
        def run(script, args):
            return json.loads(subprocess.run([sys.executable, str(SCRIPT.parent / script), *args, '--full'], capture_output=True, text=True, check=True).stdout)
        self.tokens = run('colors.py', ['palette', '--plan', str(REPO / 'tests/fixtures/colors-plan.json')])['tokens']
        for foundation in ('typography', 'spacing', 'borders', 'elevation'):
            self.save_tokens()
            self.tokens = run(foundation + '.py', ['--plan', str(REPO / 'tests/fixtures' / (foundation + '-plan.json')), '--existing', str(self.root / 'design-system/tokens.json')])['tokens']
        self.save_tokens(); p = plan()
        p['checks'][0]['command'] = 'touch SHOULD_NOT_EXIST'
        plan_path = Path(self.tmp.name) / 'plan.json'; plan_path.write_text(json.dumps(p))
        before = {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root), '--plan', str(plan_path)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'proposal_ready')
        self.assertEqual(before, {str(path.relative_to(self.root)): path.read_bytes() for path in self.root.rglob('*') if path.is_file()})
        self.assertFalse((self.root / 'SHOULD_NOT_EXIST').exists())

    def test_cli_errors_and_pending_exit_codes(self):
        path = Path(self.tmp.name) / 'plan.json'; path.write_text('{}')
        command = [sys.executable, str(SCRIPT), str(self.root), '--plan', str(path)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
        p = plan(); p['questions'] = ['Escolher variante']; path.write_text(json.dumps(p))
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)


if __name__ == '__main__':
    unittest.main()
