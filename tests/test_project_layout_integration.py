"""Integração dos caminhos compartilhados entre operações, sem escrever no consumidor após init."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / 'skills/prismo/scripts'

class LayoutIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data) if isinstance(data, dict) else data)

    def run_script(self, name, *args):
        result = subprocess.run([sys.executable, str(SCRIPTS / (name + '.py')), *map(str, args)], capture_output=True, text=True)
        self.assertIn(result.returncode, (0, 2), result.stderr)
        return json.loads(result.stdout)

    def test_custom_nested_paths_flow_between_operations(self):
        self.write('packages/web/package.json', {'dependencies': {'react': '19'}})
        self.write('docs/storybook/package.json', {'devDependencies': {'storybook': '10'}})
        self.write('docs/storybook/.storybook/main.ts', 'export default {}')
        plan = {'name':'Acme', 'platforms':['web'], 'identity':'Pendente', 'accessibility':'WCAG',
                'documentation':{'central':'adiada', 'web':'Storybook'}, 'evidence':[], 'reuse':[], 'pending':[],
                'paths':{'decisions':'acme/decisions.json', 'tokens':'acme/tokens.json', 'components':{},
                         'packages':{'web':['packages/web']}, 'documentation':{'storybook':'docs/storybook', 'docusaurus':'guides/site', 'widgetbook':'examples/widgets'}}}
        self.write('plan.json', plan)
        self.run_script('init', self.root, '--plan', self.root/'plan.json', '--apply')
        self.assertEqual(self.run_script('tokens', 'validate', self.root, '--decisions', 'acme/decisions.json')['validation'], 'passed_supported_subset')
        audit = self.run_script('audit', self.root, '--decisions', 'acme/decisions.json')
        self.assertEqual(audit['checks']['tokens']['sources'], ['acme/tokens.json'])
        document = self.run_script('document', self.root, '--decisions', 'acme/decisions.json')
        self.assertEqual(document['declared_token_source'], 'acme/tokens.json')
        self.assertEqual(document['declared_documentation']['docusaurus'], {'path':'guides/site', 'exists':False})
        self.assertTrue(document['declared_documentation']['storybook']['exists'])
        story = self.run_script('storybook', self.root, '--decisions', 'acme/decisions.json', )
        self.assertTrue(story['configured']); self.assertIn('storybook', story['storybook_packages'])
        fixture = json.loads((REPO/'tests/fixtures/create/web-plan.json').read_text())
        self.write('create.json', fixture)
        create = self.run_script('create', self.root, '--decisions', 'acme/decisions.json', '--plan', self.root/'create.json')
        self.assertEqual(create['catalog_directory'], 'docs/storybook')
        self.assertTrue(any('fora do diretório' in issue for issue in create['issues']))
        self.assertEqual(create['package_dir'], 'packages/web'); self.assertIn('react', create['architecture_evidence']['web'])
        self.assertTrue(any('fora do pacote' in issue for issue in create['issues']))
        self.assertFalse((self.root/'packages/web/src').exists())

    def test_flutter_package_manifest_is_selected_from_project_root(self):
        self.write('mobile/pubspec.yaml', 'name: acme_ds_flutter\ndependencies:\n  flutter:\n    sdk: flutter\n')
        self.write('design-system/decisions.json', {'decisions': {'platforms':['flutter'], 'paths': {'tokens':'design-system/tokens.json', 'packages':{'flutter':['mobile']}}}})
        self.write('design-system/tokens.json', {})
        fixture = json.loads((REPO/'tests/fixtures/create/flutter-plan.json').read_text())
        self.write('create.json', fixture)
        result = self.run_script('create', self.root, '--plan', self.root/'create.json')
        self.assertTrue(result['architecture_evidence']['flutter'])
        self.assertEqual(result['package_dir'], 'mobile')

    def test_catalog_consumes_real_package_public_export(self):
        # Fixture isolada: a resolução de Node é real, sem instalar dependências.
        library = {'name':'@acme/ds', 'version':'1.0.0', 'type':'module',
                   'exports':{'.':'./src/index.js'}}
        catalog = {'name':'catalog', 'private':True, 'type':'module',
                   'dependencies':{'@acme/ds':'file:../../packages/web'}}
        self.write('packages/web/package.json', library)
        self.write('packages/web/src/index.js', "export { button } from './button.js';\n")
        self.write('packages/web/src/button.js', "export const button = () => 'library';\n")
        self.write('docs/catalog/package.json', catalog)
        self.write('docs/catalog/story.mjs', "import {button} from '@acme/ds'; console.log(button());\n")
        node_modules = self.root/'docs/catalog/node_modules/@acme'
        node_modules.mkdir(parents=True)
        (node_modules/'ds').symlink_to(self.root/'packages/web', target_is_directory=True)
        self.assertIn(library['name'], catalog['dependencies'])
        result = subprocess.run(['node', 'story.mjs'], cwd=self.root/'docs/catalog', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'library')
        self.write('packages/web/src/index.js', 'export const other = 1;\n')
        failed = subprocess.run(['node', 'story.mjs'], cwd=self.root/'docs/catalog', capture_output=True, text=True)
        self.assertNotEqual(failed.returncode, 0)

    def test_configured_documentation_rejects_escape(self):
        self.write('design-system/decisions.json', {'decisions': {'paths': {'documentation': {'storybook': '../outside'}}}})
        for name in ('document', 'storybook'):
            result = subprocess.run([sys.executable, str(SCRIPTS/(name+'.py')), str(self.root)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)

    def test_documentation_at_project_root_remains_supported(self):
        self.write('design-system/decisions.json', {'decisions': {'paths': {'documentation': {'storybook': '.', 'docusaurus': '.'}}}})
        self.write('.storybook/main.js', 'export default {}')
        self.assertEqual(self.run_script('document', self.root)['declared_documentation']['storybook']['path'], '.')
        self.assertTrue(self.run_script('storybook', self.root)['configured'])

    def test_multiple_packages_need_selection_and_legacy_root_still_works(self):
        self.write('package.json', {'dependencies': {'react':'19'}})
        self.write('one/package.json', {'dependencies': {'react':'19'}})
        self.write('two/package.json', {'dependencies': {'vue':'3'}})
        self.write('design-system/decisions.json', {'decisions': {'platforms':['web'], 'paths': {'tokens':'design-system/tokens.json', 'packages':{'web':['one','two']}}}})
        self.write('design-system/tokens.json', {})
        fixture = json.loads((REPO/'tests/fixtures/create/web-plan.json').read_text()); self.write('create.json', fixture)
        args = (self.root, '--plan', self.root/'create.json')
        result = self.run_script('create', *args)
        self.assertTrue(any('múltiplos' in issue for issue in result['issues']))
        result = self.run_script('create', *args, '--package-dir', 'two')
        self.assertIn('vue', result['architecture_evidence']['web'])
        self.write('design-system/decisions.json', {'decisions': {'platforms':['web'], 'paths': {'tokens':'design-system/tokens.json'}}})
        self.assertIn('react', self.run_script('create', *args)['architecture_evidence']['web'])

if __name__ == '__main__': unittest.main()
