"""Contrato de materialização; o diálogo do agente é avaliado em init-scenarios.md."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/prismo/scripts/init.py'
spec = importlib.util.spec_from_file_location('prismo_init', SCRIPT)
init = importlib.util.module_from_spec(spec)
with patch.object(sys, 'path', [str(SCRIPT.parent), *sys.path]):
    spec.loader.exec_module(init)


class InitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='prismo init ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()
        self.plan_file = Path(self.temp.name) / 'plan.json'
        self.plan = dict(name='POC', platforms=['web'], identity='Pendente',
                         accessibility='WCAG 2.2 AA', documentation={'central': 'adiada', 'web': 'adiada'},
                         evidence=[], reuse=[], pending=['Definir identidade'],
                         paths=dict(decisions='design-system/decisions.json',
                                    tokens='design-system/tokens.json', components={'web': 'src/components'}))

    def run_init(self, apply=False, ok=True):
        self.plan_file.write_text(json.dumps(self.plan))
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root),
                                 '--plan', str(self.plan_file), *(['--apply'] if apply else [])],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return json.loads(result.stdout) if ok else result

    def test_preview_does_not_write(self):
        self.assertEqual(self.run_init()['status'], 'preview')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_empty_project_creates_only_scaffold(self):
        self.run_init(apply=True)
        self.assertEqual(json.loads((self.root / 'design-system/tokens.json').read_text()), {})
        record = json.loads((self.root / 'design-system/decisions.json').read_text())
        self.assertEqual(record['decisions'], self.plan)
        self.assertFalse((self.root / 'src').exists())
        files = {str(p.relative_to(self.root)) for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(files, {'design-system/decisions.json', 'design-system/tokens.json'})

    def test_existing_project_reuses_resources(self):
        (self.root / 'theme.css').write_text(':root { --brand: red; }')
        (self.root / 'widgets').mkdir()
        self.plan['paths'].update(tokens=None, components={})
        self.plan['reuse'] = ['theme.css: tokens legados', 'widgets: atoms e molecules existentes']
        self.run_init(apply=True)
        self.assertEqual((self.root / 'theme.css').read_text(), ':root { --brand: red; }')
        self.assertEqual(list((self.root / 'widgets').iterdir()), [])
        self.assertFalse((self.root / 'src').exists())

    def test_existing_component_directory_is_registered_without_changes(self):
        (self.root / 'src/components').mkdir(parents=True)
        (self.root / 'src/components/keep.txt').write_text('existing')
        self.run_init(apply=True)
        self.assertEqual((self.root / 'src/components/keep.txt').read_text(), 'existing')
        self.assertEqual(len(list((self.root / 'src/components').iterdir())), 1)

    def test_existing_dtcg_is_registered_and_consumed_by_other_operations(self):
        token_file = self.root / 'existing.json'
        token_file.write_text(json.dumps({'semantic': {'light': {'text': {'$type': 'color', '$value': {'colorSpace': 'srgb', 'components': [0, 0, 0]}}}}}))
        self.plan['paths'].update(tokens=None, tokens_existing='existing.json', components={})
        before = token_file.read_bytes()
        self.run_init(apply=True)
        record = json.loads((self.root / 'design-system/decisions.json').read_text())
        self.assertEqual(record['decisions']['paths']['tokens'], 'existing.json')
        self.assertEqual(token_file.read_bytes(), before)
        scripts = SCRIPT.parent
        result = subprocess.run([sys.executable, str(scripts / 'tokens.py'), 'validate', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(scripts / 'audit.py'), str(self.root)], capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)['checks']['tokens']['sources'], ['existing.json'])
        (self.root / 'package.json').write_text(json.dumps({'dependencies': {'react': '18'}}))
        (self.root / '.storybook').mkdir(); (self.root / '.storybook/main.ts').write_text('export default {}')
        fixture = SCRIPT.parents[3] / 'tests/fixtures/create/web-plan.json'
        result = subprocess.run([sys.executable, str(scripts / 'create.py'), str(self.root), '--plan', str(fixture)], capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)['token_source'], 'existing.json')

    def test_legacy_reuse_path_is_detected_when_unambiguous(self):
        (self.root / 'existing.json').write_text('{}')
        self.plan['paths'].update(tokens=None, components={})
        self.plan['reuse'] = ['existing.json — fonte DTCG existente']
        self.run_init(apply=True)
        result = subprocess.run([sys.executable, str(SCRIPT.parent / 'tokens.py'), 'validate', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_multiplatform_and_marketing_reuse_web(self):
        self.plan['platforms'] = ['web', 'flutter', 'marketing']
        self.plan['documentation'].update(flutter='Widgetbook adiado', marketing='reutiliza Web')
        self.plan['paths']['components']['flutter'] = 'mobile/lib/widgets'
        self.plan['reuse'] = ['Marketing reutiliza src/components da Web']
        self.run_init(apply=True)
        self.assertFalse((self.root / 'mobile').exists())
        self.assertFalse((self.root / 'marketing').exists())

    def test_existing_file_aborts_without_partial_output(self):
        (self.root / 'design-system').mkdir()
        path = self.root / 'design-system/tokens.json'
        path.write_text('preservar')
        self.run_init(apply=True, ok=False)
        self.assertEqual(path.read_text(), 'preservar')
        self.assertFalse((self.root / 'src').exists())
        self.assertFalse((self.root / 'design-system/decisions.json').exists())

    def test_second_init_preserves_decisions(self):
        self.run_init(apply=True)
        before = (self.root / 'design-system/decisions.json').read_bytes()
        self.run_init(apply=True, ok=False)
        self.assertEqual((self.root / 'design-system/decisions.json').read_bytes(), before)

    def test_missing_essential_decisions(self):
        for key, value in [('platforms', []), ('identity', ''), ('documentation', {})]:
            original = self.plan[key]
            self.plan[key] = value
            self.run_init(apply=True, ok=False)
            self.plan[key] = original
        self.assertEqual(list(self.root.iterdir()), [])

    def test_unsafe_or_overlapping_paths(self):
        for relative in ['../outside.json', '/tmp/outside.json', './tokens.json',
                         'src/components', 'src/components/tokens.json']:
            self.plan['paths']['tokens'] = relative
            self.run_init(apply=True, ok=False)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_parent_symlink_and_broken_link(self):
        (self.root / 'design-system').symlink_to(self.root.parent)
        self.run_init(apply=True, ok=False)
        (self.root / 'design-system').unlink()
        (self.root / 'design-system').symlink_to(self.root / 'missing')
        self.run_init(apply=True, ok=False)
        self.assertFalse((self.root / 'src').exists())

    def test_rolls_back_only_created_paths_on_failure(self):
        (self.root / 'keep.txt').write_text('keep')
        files, directories = init.prepare(self.root, self.plan)
        with patch.object(Path, 'open', side_effect=OSError('simulated failure')):
            with self.assertRaises(OSError):
                init.apply(self.root, files, directories)
        self.assertEqual(list(self.root.iterdir()), [self.root / 'keep.txt'])


if __name__ == '__main__':
    unittest.main()
