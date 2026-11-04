"""Inventário real em fixtures temporárias; não simula aprovação ou sessão do agente."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'skills/prismo/scripts/document.py'
spec = importlib.util.spec_from_file_location('prismo_document', SCRIPT)
d = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(SCRIPT.parent))
spec.loader.exec_module(d)


class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='prismo document ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'consumer'
        self.root.mkdir()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(content) if isinstance(content, dict) else content)
        return target

    def portal(self, prefix=''):
        self.write(prefix + 'package.json', {'devDependencies': {'@docusaurus/core': '3.9.2'}})
        self.write(prefix + 'docusaurus.config.ts', 'export default {presets: []};')

    def decisions(self, path='design-system/decisions.json', tokens='design-system/tokens.json'):
        self.write(path, {'decisions': {'paths': {'tokens': tokens}, 'platforms': ['web', 'flutter']}})
        self.write(tokens, {'semantic': {'text': {'$type': 'color', '$value': '{primitive.ink}'}}})

    def test_existing_portal_is_evidence_not_approval(self):
        self.portal(); self.decisions()
        result = d.inventory(self.root)
        self.assertEqual(result['sources']['portal_packages'], [{'manifest': 'package.json', 'version': '3.9.2'}])
        self.assertEqual(result['sources']['portal_configs'], ['docusaurus.config.ts'])
        self.assertTrue(result['declared_token_source_exists'])
        self.assertEqual(result['phase'], 'investigation')
        self.assertIn('documentation_proposal', result['approval_required'])

    def test_absent_portal_proposes_setup_without_writes(self):
        result = d.inventory(self.root)
        self.assertEqual(result['sources']['portal_configs'], [])
        self.assertIn('portal_setup_if_needed', result['approval_required'])
        self.assertTrue(any('Portal não confirmado' in n for n in result['attention']))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_package_only_does_not_prove_configuration(self):
        self.write('package.json', {'dependencies': {'@docusaurus/core': '3.8.1'}})
        self.assertTrue(any('Portal não confirmado' in n for n in d.inventory(self.root)['attention']))

    def test_config_only_does_not_prove_dependencies(self):
        self.write('docusaurus.config.mjs', 'export default {};')
        self.assertTrue(any('Portal não confirmado' in n for n in d.inventory(self.root)['attention']))

    def test_monorepo_portals_require_selection(self):
        self.portal('apps/docs/'); self.portal('packages/site/')
        result = d.inventory(self.root)
        self.assertEqual(result['counts']['portal_configs'], 2)
        self.assertTrue(any('Múltiplos portais' in n for n in result['attention']))
        self.assertEqual(d.inventory(self.root / 'apps/docs')['counts']['portal_configs'], 1)

    def test_custom_sources_and_existing_documentation_for_reuse(self):
        self.decisions('ds/record.json', 'packages/theme/palette.json')
        self.write('portal/content/colors.mdx', '# Colors\nSource: palette.json')
        self.write('packages/button/README.md', '# API canônica')
        result = d.inventory(self.root, 'ds/record.json')
        self.assertIn('packages/theme/palette.json', result['sources']['token_candidates'])
        self.assertEqual(result['counts']['docs'], 2)
        self.assertIn('packages/button/README.md', result['sources']['docs'])

    def test_missing_decisions_and_tokens_report_gaps(self):
        self.write('theme/colors.tokens.json', {})
        result = d.inventory(self.root)
        self.assertIsNone(result['decisions'])
        self.assertFalse(result['declared_token_source_exists'])
        self.assertTrue(any('Registro não encontrado' in n for n in result['attention']))
        self.assertIn('theme/colors.tokens.json', result['sources']['token_candidates'])
        self.decisions(); (self.root / 'design-system/tokens.json').unlink()
        self.assertFalse(d.inventory(self.root)['declared_token_source_exists'])

    def test_web_flutter_catalogs_and_brand_assets_are_candidates_not_urls(self):
        for path in ('src/Button.tsx', 'lib/button.dart', 'src/Button.stories.tsx',
                     '.storybook/main.ts', 'widgetbook/lib/button_use_case.dart',
                     'src/Button.test.tsx', 'brand/logo.svg'):
            self.write(path, '// fixture')
        result = d.inventory(self.root)
        self.assertIn('src/Button.tsx', result['sources']['component_candidates'])
        self.assertIn('lib/button.dart', result['sources']['component_candidates'])
        self.assertNotIn('src/Button.test.tsx', result['sources']['component_candidates'])
        self.assertEqual(result['counts']['catalogs'], 3)
        self.assertEqual(result['sources']['identity_assets'], ['brand/logo.svg'])
        self.assertNotIn('url', result)

    def test_excludes_generated_dependencies_and_symlinks(self):
        self.write('node_modules/other/docusaurus.config.js', 'throw Error()')
        self.write('build/docs.md', 'gerado')
        outside = Path(self.tmp.name) / 'external'; outside.mkdir()
        (outside / 'secret.md').write_text('não ler')
        (self.root / 'linked').symlink_to(outside)
        (self.root / 'linked.md').symlink_to(outside / 'secret.md')
        result = d.inventory(self.root)
        self.assertEqual(result['counts']['docs'], 0)
        self.assertEqual(result['counts']['portal_configs'], 0)
        self.assertEqual(result['scan']['symlinks_skipped'], 2)
        self.assertTrue(any('Inventário parcial' in n for n in result['attention']))

    def test_scan_and_display_limits_are_explicit(self):
        for number in range(60): self.write('docs/page' + str(number) + '.md', '# Page')
        result = d.inventory(self.root, limit=3)
        self.assertTrue(result['scan']['truncated'])
        self.assertEqual(result['scan']['files'], 3)
        result = d.inventory(self.root)
        self.assertEqual(result['counts']['docs'], 60)
        self.assertEqual(len(result['sources']['docs']), 50)
        self.assertFalse(result['scan']['truncated'])

    def test_invalid_paths_and_external_declared_source_are_rejected(self):
        for path in ('../record.json', '/tmp/record.json', 'a\\b', 'a/./b'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                d.inventory(self.root, path)
        self.write('design-system/decisions.json', {'paths': {'tokens': '../outside.json'}})
        with self.assertRaises(ValueError): d.inventory(self.root)
        self.write('design-system/decisions.json', {'paths': {'tokens': 'external/tokens.json'}})
        (self.root / 'external').symlink_to(self.root.parent)
        with self.assertRaises(ValueError): d.inventory(self.root)

    def test_invalid_json_and_record_structure_are_not_silently_ignored(self):
        self.write('package.json', '{bad')
        with self.assertRaises(ValueError): d.inventory(self.root)
        (self.root / 'package.json').unlink()
        self.write('design-system/decisions.json', {'decisions': []})
        with self.assertRaises(ValueError): d.inventory(self.root)

    def test_cli_never_executes_config_or_package_scripts_and_preserves_files(self):
        self.decisions(); self.portal()
        self.write('docusaurus.config.ts', "require('node:fs').writeFileSync('SHOULD_NOT_EXIST', 'x')")
        self.write('package.json', {'dependencies': {'@docusaurus/core': '3.9.2'},
                                   'scripts': {'build': 'touch SHOULD_NOT_EXIST'}})
        for foundation in ('colors', 'typography', 'spacing', 'borders', 'elevation'):
            self.write('docs/' + foundation + '.md', '# Existente: ' + foundation)
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['phase'], 'investigation')
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_cli_bad_input_exit_one_and_no_approval_field(self):
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root / 'missing')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Erro:', result.stderr)
        self.assertNotIn('approved', d.inventory(self.root))


if __name__ == '__main__':
    unittest.main()
