"""Evidências determinísticas e limites da auditoria; não simula revisão humana completa."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'skills/prismo/scripts/audit.py'
spec = importlib.util.spec_from_file_location('prismo_audit', SCRIPT)
a = importlib.util.module_from_spec(spec)
with patch.object(sys, 'path', [str(SCRIPT.parent), *sys.path]):
    spec.loader.exec_module(a)


def color(v, alpha=1):
    return {'$type': 'color', '$value': {'colorSpace': 'srgb', 'components': [v, v, v], 'alpha': alpha}}


def config():
    return {'contrast_pairs': [], 'bindings': {}, 'components': []}


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='prismo audit ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tokens = {'primitive': {'black': color(0), 'white': color(1), 'gray': color(.5)},
                       'semantic': {'text': {'$type': 'color', '$value': '{primitive.black}'}}}
        self.save()
        self.write('design-system/decisions.json', {'decisions': {'paths': {'tokens': 'ds/tokens.json'}, 'platforms': ['web', 'flutter']}})
        self.write('src/Button.css', '.button { color: var(--text); background: var(--surface); }')
        self.c = config()

    def write(self, filename, value):
        path = self.root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value, dict) else value)
        return path

    def save(self):
        self.write('ds/tokens.json', self.tokens)

    def pair(self, foreground='semantic.text', background='primitive.white', usage='normal_text'):
        return {'foreground': foreground, 'background': background, 'usage': usage,
                'evidence': {'file': 'src/Button.css', 'line': 1, 'text': 'color: var(--text); background: var(--surface)'}}

    def run_audit(self, **kwargs):
        return a.audit(self.root, self.c, **kwargs)

    def codes(self, result):
        return {f['code']: f for f in result['findings']}

    def test_healthy_tokens_and_identified_contrast_no_confirmed_findings(self):
        self.c['contrast_pairs'] = [self.pair()]
        result = self.run_audit()
        self.assertEqual(result['summary']['confirmed'], 0)
        self.assertEqual(result['checks']['tokens']['count'], 4)
        self.assertEqual(result['checks']['contrast'][0]['ratio'], 21)
        self.assertTrue(result['checks']['contrast'][0]['AA'])
        self.assertEqual(result['findings'], [])
        self.assertTrue(result['manual_checks'])

    def test_failed_pair_has_ratio_location_recommendation_and_limited_claim(self):
        self.c['contrast_pairs'] = [self.pair('primitive.white')]
        result = self.run_audit(); item = self.codes(result)['CONTRAST_AA']
        self.assertEqual(item['certainty'], 'confirmed')
        self.assertEqual(item['severity'], 'high')
        self.assertEqual(item['evidence']['ratio'], 1)
        self.assertEqual(item['evidence']['file'], 'src/Button.css')
        self.assertEqual(item['evidence']['line'], 1)
        self.assertIn('par declarado', item['title'].lower())
        self.assertIn('confirmar aplicação', item['recommendation'])

    def test_usage_thresholds_differ_and_comparison_is_not_rounded(self):
        self.c['contrast_pairs'] = [self.pair('primitive.gray', usage=u) for u in ('normal_text', 'large_text', 'non_text')]
        results = self.run_audit()['checks']['contrast']
        self.assertFalse(results[0]['AA']); self.assertTrue(results[1]['AA']); self.assertTrue(results[2]['AA'])
        self.c['contrast_pairs'] = [self.pair()]
        with patch.object(a, 'contrast', return_value=4.49999):
            result = self.run_audit()['checks']['contrast'][0]
        self.assertFalse(result['AA']); self.assertEqual(result['ratio'], 4.49999)

    def test_alpha_missing_color_and_unsupported_context_stay_pending(self):
        self.tokens['primitive']['white'] = color(1, .5); self.save()
        self.c['contrast_pairs'] = [self.pair()]
        result = self.run_audit()
        self.assertEqual(self.codes(result)['CONTRAST_BLOCKED']['certainty'], 'manual')
        self.assertEqual(result['summary']['confirmed'], 0)
        self.c['contrast_pairs'] = [self.pair(background='missing')]
        self.assertEqual(self.codes(self.run_audit())['CONTRAST_BLOCKED']['certainty'], 'manual')

    def test_stale_evidence_does_not_produce_a_contrast_result(self):
        p = self.pair('primitive.white'); p['evidence']['line'] = 2
        self.c['contrast_pairs'] = [p]
        result = self.run_audit()
        self.assertNotIn('ratio', result['checks']['contrast'][0])
        self.assertEqual(self.codes(result)['CONTRAST_EVIDENCE']['certainty'], 'manual')

    def test_names_are_not_used_to_invent_contrast_pairs(self):
        result = self.run_audit()
        self.assertEqual(result['checks']['contrast'], [])
        self.assertEqual(self.codes(result)['CONTRAST_UNKNOWN']['certainty'], 'manual')

    def test_missing_reference_cycle_and_type_mismatch_are_confirmed(self):
        for value, kind in (('{missing}', 'color'), ('{semantic.text}', 'color'), ('{primitive.white}', 'dimension')):
            with self.subTest(value=value, kind=kind):
                self.tokens['semantic']['text'] = {'$type': kind, '$value': value}; self.save()
                result = self.run_audit(); item = self.codes(result)['TOKEN_INVALID']
                self.assertEqual(item['certainty'], 'confirmed')
                self.assertIn('ds/tokens.json', item['evidence']['files'])
                self.assertEqual(result['checks']['tokens']['status'], 'failed')

    def test_duplicate_json_keys_and_paths_are_confirmed(self):
        self.write('ds/tokens.json', '{"x":{"$type":"number","$value":1,"$value":2}}')
        self.assertEqual(self.codes(self.run_audit())['TOKEN_SOURCE']['certainty'], 'confirmed')
        self.save(); self.write('ds/other.json', self.tokens)
        result = self.run_audit(sources=['ds/tokens.json', 'ds/other.json'])
        self.assertEqual(self.codes(result)['TOKEN_INVALID']['certainty'], 'confirmed')

    def test_equivalent_values_are_grouped_risk_not_duplicate_defect(self):
        self.tokens['primitive']['other'] = color(0); self.save()
        item = self.codes(self.run_audit())['TOKEN_EQUIVALENT']
        self.assertEqual(item['certainty'], 'risk')
        self.assertEqual(item['severity'], 'low')
        self.assertEqual(item['evidence']['count'], 1)
        self.assertEqual(item['evidence']['examples'][0]['tokens'], ['primitive.black', 'primitive.other'])

    def test_valid_formats_outside_supported_subset_are_manual_not_defects(self):
        self.tokens['primitive']['white']['$value']['colorSpace'] = 'display-p3'; self.save()
        result = self.run_audit()
        self.assertEqual(self.codes(result)['TOKEN_UNSUPPORTED']['certainty'], 'manual')
        self.assertEqual(result['summary']['confirmed'], 0)
        self.assertEqual(result['checks']['tokens']['status'], 'blocked')

    def test_invalid_type_is_confirmed_and_causes_cli_failure_status(self):
        self.tokens['primitive']['bad'] = {'$type': 'colro', '$value': 1}
        self.save()
        result = self.run_audit()
        self.assertEqual(self.codes(result)['TOKEN_INVALID']['certainty'], 'confirmed')
        cli = subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True, text=True)
        self.assertEqual(cli.returncode, 2)

    def test_missing_decisions_or_tokens_are_limited_coverage_not_invented_defects(self):
        (self.root / 'design-system/decisions.json').unlink()
        result = self.run_audit()
        self.assertEqual(result['summary']['confirmed'], 0)
        self.assertIn('DECISIONS_UNKNOWN', self.codes(result))
        self.assertIn('TOKENS_UNKNOWN', self.codes(result))
        result = self.run_audit(sources=['does-not-exist.json'])
        self.assertEqual(self.codes(result)['TOKEN_SOURCE']['certainty'], 'manual')

    def test_literals_are_located_risks_and_zero_token_bindings_are_not_flagged(self):
        self.write('src/Shape.css', '.shape { border-radius: 9999px; padding: 16px; color: #fff; }')
        result = self.run_audit(); item = self.codes(result)['STYLE_LITERAL']
        self.assertEqual(item['certainty'], 'risk')
        self.assertEqual(item['evidence']['examples'][0]['file'], 'src/Shape.css')
        self.assertEqual(item['evidence']['examples'][0]['line'], 1)
        self.write('src/Shape.css', '.shape { margin: 0; padding: var(--gap); }')
        self.assertNotIn('STYLE_LITERAL', self.codes(self.run_audit()))

    def test_flutter_literal_candidates_and_token_usage(self):
        self.write('lib/control.dart', 'final gap = EdgeInsets.all(16);\nfinal color = Color(0xff112233);')
        result = self.run_audit()
        self.assertEqual(self.codes(result)['STYLE_LITERAL']['evidence']['count'], 2)
        self.write('lib/control.dart', 'final gap = EdgeInsets.all(AppTokens.space16);')
        self.assertNotIn('STYLE_LITERAL', self.codes(self.run_audit()))

    def test_image_without_explicit_alt_is_risk_even_with_spread(self):
        self.write('src/Image.tsx', 'return <img {...props} src="a.png" />;')
        item = self.codes(self.run_audit())['IMAGE_NAME']
        self.assertEqual(item['certainty'], 'risk')
        self.assertEqual(item['evidence']['line'], 1)
        self.write('src/Image.tsx', 'return <img src="a.png" alt="" />;')
        self.assertNotIn('IMAGE_NAME', self.codes(self.run_audit()))

    def component(self):
        self.write('src/Button.tsx', 'export const Button = ({loading, variant}) => null;')
        self.write('docs/button.md', 'Button tem loading e variant.')
        self.write('src/Button.stories.tsx', 'export const Loading = {}; export const Variants = {};')
        return {'name': 'Button', 'implementation': 'src/Button.tsx', 'documentation': 'docs/button.md',
                'catalog': 'src/Button.stories.tsx', 'expectations': [
                    {'name': 'loading', 'implementation': 'loading', 'documentation': 'loading', 'catalog': 'Loading'},
                    {'name': 'variant', 'implementation': 'variant', 'documentation': 'variant', 'catalog': 'Variants'}]}

    def test_component_contract_consistency_uses_real_evidence_and_reports_only_risks(self):
        self.c['components'] = [self.component()]
        self.assertNotIn('CONTRACT_COVERAGE', self.codes(self.run_audit()))
        self.write('docs/button.md', 'Button tem variant.')
        item = self.codes(self.run_audit())['CONTRACT_COVERAGE']
        self.assertEqual(item['certainty'], 'risk')
        self.assertEqual(item['evidence'][0]['role'], 'documentation')
        self.assertEqual(item['evidence'][0]['searched'], 'loading')

    def test_unknown_catalog_and_files_outside_scope_are_manual_not_absent_states(self):
        self.c['components'] = [self.component()]
        result = self.run_audit(scopes=['ds'])
        item = self.codes(result)['CONTRACT_COVERAGE']
        self.assertEqual(item['certainty'], 'manual')
        self.assertTrue(all(o['status'] == 'not_read' for o in item['evidence']))

    def test_binding_observed_for_unknown_token_is_risk(self):
        self.c['bindings'] = {'semantic.missing': ['--text']}
        item = self.codes(self.run_audit())['BINDING_UNKNOWN']
        self.assertEqual(item['certainty'], 'risk')
        self.assertEqual(item['evidence']['examples'][0]['file'], 'src/Button.css')
        self.c['bindings'] = {'semantic.text': ['--text']}
        self.assertNotIn('BINDING_UNKNOWN', self.codes(self.run_audit()))

    def test_sources_custom_decisions_and_multifile_alias_resolution(self):
        self.write('custom.json', {'paths': {'tokens': 'ds/tokens.json'}})
        result = self.run_audit(decisions='custom.json')
        self.assertEqual(result['checks']['tokens']['count'], 4)
        other = {'component': {'text': {'$type': 'color', '$value': '{semantic.text}'}}}
        self.write('ds/component.json', other)
        result = self.run_audit(sources=['ds/tokens.json', 'ds/component.json'])
        self.assertEqual(result['checks']['tokens']['count'], 5)

    def test_scopes_budget_and_skipped_symlinks_are_explicit(self):
        self.write('node_modules/hidden.css', 'color: #fff;')
        self.write('build/hidden.css', 'color: #fff;')
        self.write('src/big.css', 'x' * (1024 * 1024 + 1))
        (self.root / 'src/link.css').symlink_to(self.root / 'src/Button.css')
        result = self.run_audit(scopes=['src'], scan_limit=1)
        self.assertEqual(result['coverage']['files_read'], 1)
        self.assertGreaterEqual(result['coverage']['skipped'], 2)
        self.assertNotIn('STYLE_LITERAL', self.codes(result))
        self.assertTrue(self.run_audit(scan_limit=1)['coverage']['truncated'])

    def test_generated_artifacts_are_pruned_before_budget_even_in_nested_scopes(self):
        for directory in ('storybook-static', '.cache', '.turbo', '.vercel', '.nuxt', '.output', '.svelte-kit'):
            self.write(f'docs/{directory}/artifact.css', 'color: #f00;')
        for suffix in a.GENERATED_SUFFIXES:
            self.write('src/generated' + suffix, 'color: #f00;')
        self.write('src/real.css', 'color: #fff;')
        files, coverage = a.scan(self.root, ['docs', 'src'], limit=3)
        self.assertIn('src/real.css', files)
        self.assertEqual(set(files), {'src/Button.css', 'src/real.css'})
        self.assertFalse(coverage['truncated'])
        self.assertGreaterEqual(coverage['skipped'], 11)
        self.assertEqual(a.scan(self.root, ['docs/storybook-static'])[0], {})

    def test_explicit_exclusions_are_project_relative_and_do_not_hide_token_validation(self):
        self.write('src/vendor/fixture.css', 'color: #f00;')
        self.write('src/vendor-other.css', 'color: #fff;')
        files, coverage = a.scan(self.root, ['src', 'src/vendor'], excludes=['src/vendor', 'src/Button.css'])
        self.assertEqual(set(files), {'src/vendor-other.css'})
        self.assertEqual(coverage['exclusions'], ['src/vendor', 'src/Button.css'])
        self.tokens['bad'] = {'$type': 'color', '$value': '{missing}'}; self.save()
        result = self.run_audit(excludes=['ds', 'src'])
        self.assertIn('TOKEN_INVALID', self.codes(result))
        self.assertNotIn('STYLE_LITERAL', self.codes(result))
        self.assertNotIn('src/Button.css', a.scan(self.root, ['src/Button.css'], excludes=['src'])[0])

    def test_exclusion_paths_reject_traversal_symlinks_and_globs(self):
        (self.root / 'linked').symlink_to(self.root / 'src', target_is_directory=True)
        for value in ('../outside', '/tmp', 'src/../ds', 'linked', 'src/*.css', '', '.'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.run_audit(excludes=[value])

    def test_cli_exclusions_and_missing_evidence_remain_readonly_and_manual(self):
        self.c['contrast_pairs'] = [self.pair()]
        self.write('evidence.json', self.c)
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        cli = subprocess.run([sys.executable, str(SCRIPT), str(self.root), '--exclude', 'src',
                              '--exclude', 'missing-generated', '--config', str(self.root / 'evidence.json')],
                             capture_output=True, text=True)
        self.assertEqual(cli.returncode, 0, cli.stderr)
        result = json.loads(cli.stdout)
        self.assertEqual(self.codes(result)['CONTRAST_EVIDENCE']['certainty'], 'manual')
        self.assertEqual(result['coverage']['exclusions'], ['src', 'missing-generated'])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_bad_config_paths_and_evidence_schema_rejected(self):
        bad = self.pair(); bad['evidence']['line'] = True
        self.c['contrast_pairs'] = [bad]
        with self.assertRaises(ValueError): self.run_audit()
        bad['evidence']['line'] = 1; bad['evidence']['file'] = '../secret'
        with self.assertRaises(ValueError): self.run_audit()
        (self.root / 'linked').symlink_to(self.root / 'src', target_is_directory=True)
        bad['evidence']['file'] = 'linked/Button.css'
        with self.assertRaises(ValueError): self.run_audit()
        self.c['components'] = [{'name': 'missing-fields'}]; self.c['contrast_pairs'] = []
        with self.assertRaises(ValueError): self.run_audit()

    def test_bounded_findings_and_severity_prioritization(self):
        for n in range(105): self.write(f'src/C{n}.css', 'color: #fff;')
        self.c['contrast_pairs'] = [self.pair('primitive.white')]
        result = self.run_audit()
        self.assertEqual(len(result['findings']), 100)
        self.assertGreater(result['omitted_findings'], 0)
        self.assertEqual(result['findings'][0]['code'], 'CONTRAST_AA')
        self.assertEqual(result['summary']['risk'], 105)

    def test_passing_pairs_do_not_expand_report_without_bound(self):
        self.c['contrast_pairs'] = [self.pair() for _ in range(15)]
        self.c['contrast_pairs'].append(self.pair('primitive.white'))
        result = self.run_audit()
        self.assertEqual(result['checks']['contrast_total'], 16)
        self.assertEqual(result['checks']['contrast_omitted'], 6)
        self.assertEqual(len(result['checks']['contrast']), 10)
        self.assertFalse(result['checks']['contrast'][0]['AA'])

    def test_cli_readonly_even_when_skill_copied_inside_consumer_and_configs_are_executable(self):
        scripts = self.root / 'tools/prismo'; scripts.mkdir(parents=True)
        for script in SCRIPT.parent.glob('*.py'): shutil.copyfile(script, scripts / script.name)
        self.write('package.json', {'scripts': {'test': 'touch SHOULD_NOT_EXIST'}})
        self.write('docusaurus.config.js', "require('fs').writeFileSync('SHOULD_NOT_EXIST', 'x')")
        self.write('widgetbook/main.dart', 'void main() {}')
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = subprocess.run([sys.executable, str(scripts / 'audit.py'), str(self.root)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.assertFalse(list(self.root.rglob('__pycache__')))
        self.assertEqual(json.loads(result.stdout)['checks']['tokens']['status'], 'passed_supported_subset')

    def test_cli_exit_codes_for_confirmed_findings_and_bad_input(self):
        self.c['contrast_pairs'] = [self.pair('primitive.white')]
        cfg = self.write('evidence.json', self.c)
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root), '--config', str(cfg)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)['summary']['confirmed'], 1)
        self.write('evidence.json', {})
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root), '--config', str(cfg)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)


if __name__ == '__main__':
    unittest.main()
