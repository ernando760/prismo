"""Inspeção segura e somente leitura da integração Storybook."""
import importlib.util
import json
import sys
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/prismo/scripts/storybook.py'
spec = importlib.util.spec_from_file_location('storybook_inspect', SCRIPT)
s = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(SCRIPT.parent))
spec.loader.exec_module(s)


class StorybookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def record(self, platforms):
        (self.root / 'design-system').mkdir(exist_ok=True)
        (self.root / 'design-system/decisions.json').write_text(json.dumps({'decisions': {'platforms': platforms, 'paths': {'tokens': 'design-system/tokens.json'}}}))

    def test_web_declared_but_not_implemented_requires_approval(self):
        self.record(['web', 'flutter'])
        result = s.inspect(self.root)
        self.assertTrue(result['web_declared']); self.assertFalse(result['configured'])
        self.assertEqual(result['next'], 'approval_required_before_install_or_configuration')

    def test_framework_and_existing_configuration_are_detected(self):
        (self.root / 'package.json').write_text(json.dumps({'dependencies': {'react':'19'},'devDependencies': {'storybook':'10','@storybook/react-vite':'10'}}))
        (self.root / '.storybook').mkdir(); (self.root / '.storybook/main.ts').write_text('export default {}')
        result=s.inspect(self.root)
        self.assertIn('react',result['web_evidence']); self.assertTrue(result['configured'])
        self.assertEqual(result['next'],'review_existing_config_and_renderer')

    def test_packages_without_configuration_are_not_reported_as_working(self):
        self.record(['web'])
        (self.root / 'package.json').write_text(json.dumps({'devDependencies': {'storybook':'10'}}))
        self.assertFalse(s.inspect(self.root)['configured'])

    def test_flutter_only_is_not_web(self):
        self.record(['flutter'])
        self.assertFalse(s.inspect(self.root)['web_declared'])
        self.assertEqual(s.inspect(self.root)['next'],'not_applicable_to_declared_platforms')

    def test_empty_project_requires_scope_clarification(self):
        self.assertEqual(s.inspect(self.root)['next'],'clarify_web_scope_before_integration')

    def test_custom_configuration_directory(self):
        (self.root / 'catalog').mkdir(); (self.root / 'catalog/main.mjs').write_text('throw Error("must not execute")')
        self.assertTrue(s.inspect(self.root,'catalog')['configured'])

    def test_registered_location_and_explicit_override(self):
        self.record(['web'])
        path = self.root / 'design-system/decisions.json'
        record = json.loads(path.read_text())
        record['decisions']['paths']['documentation'] = {'storybook': 'docs/catalog'}
        path.write_text(json.dumps(record))
        (self.root / 'docs/catalog/.storybook').mkdir(parents=True)
        (self.root / 'docs/catalog/.storybook/main.ts').write_text('export default {}')
        (self.root / 'docs/catalog/package.json').write_text(json.dumps({'devDependencies': {'storybook': '10'}}))
        result = s.inspect(self.root)
        self.assertTrue(result['configured'])
        self.assertEqual(result['package_dir'], 'docs/catalog')
        self.assertIn('storybook', result['storybook_packages'])
        self.assertEqual(s.inspect(self.root, package_dir='.')['package_dir'], '.')
        with self.assertRaises(ValueError): s.inspect(self.root, config_dir='../outside')

    def test_inspection_does_not_change_files(self):
        self.record(['web']); (self.root / 'design-system/tokens.json').write_text('{}')
        before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        s.inspect(self.root)
        self.assertEqual(before,{str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_invalid_json_is_not_silently_ignored(self):
        (self.root / 'package.json').write_text('{')
        with self.assertRaises(ValueError): s.inspect(self.root)


if __name__ == '__main__':
    unittest.main()
