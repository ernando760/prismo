"""Saída resumida preserva precisão e permite recuperar candidatos completos."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/prismo/scripts'
FIXTURES = ROOT / 'tests/fixtures'

class ContextOutputTests(unittest.TestCase):
    def run_helper(self, name, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / name), *args], capture_output=True, text=True)

    def test_foundation_summaries_and_full_outputs_share_exact_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'tokens.json'; source.write_text('{}')
            for name in ('colors', 'typography', 'spacing', 'borders', 'elevation'):
                args = (['palette'] if name == 'colors' else []) + ['--plan', str(FIXTURES / (name + '-plan.json')), '--existing', str(source)]
                summary = self.run_helper(name + '.py', *args)
                full = self.run_helper(name + '.py', *args, '--full')
                self.assertEqual(summary.returncode, 0, summary.stderr)
                self.assertEqual(full.returncode, 0, full.stderr)
                short, complete = json.loads(summary.stdout), json.loads(full.stdout)
                self.assertNotIn('tokens', short)
                self.assertTrue(short['token_changes'])
                for change in short['token_changes']:
                    node = complete['tokens']
                    for part in change['path'].split('.'): node = node[part]
                    self.assertEqual(change['after'], node)
                source.write_text(json.dumps(complete['tokens']))
                unchanged = self.run_helper(name + '.py', *args)
                self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
                self.assertEqual(json.loads(unchanged.stdout)['token_changes'], [])

    def test_tokens_noop_summary_and_full_preserve_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'ds').mkdir()
            source = {'sizes': {str(i): {'$type': 'dimension', '$value': {'value': i + .123456789, 'unit': 'px'}} for i in range(80)}}
            (root / 'ds/tokens.json').write_text(json.dumps(source))
            plan = root / 'plan.json'; plan.write_text(json.dumps({'changes': [], 'bindings': {}}))
            args = ['preview', str(root), '--source', 'ds/tokens.json', '--plan', str(plan)]
            short, full = self.run_helper('tokens.py', *args), self.run_helper('tokens.py', *args, '--full')
            self.assertEqual(short.returncode, 0, short.stderr); self.assertEqual(full.returncode, 0, full.stderr)
            brief, complete = json.loads(short.stdout), json.loads(full.stdout)
            self.assertEqual(brief['status'], 'no_changes'); self.assertNotIn('files', brief)
            self.assertEqual(complete['files']['ds/tokens.json'], source)
            self.assertEqual(brief['changes'], complete['changes'])
            self.assertLess(len(short.stdout), len(full.stdout) // 3)
            self.assertEqual(json.loads((root / 'ds/tokens.json').read_text()), source)

    def test_changed_token_summary_retains_precise_diff_and_impact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = {'size': {'$type': 'dimension', '$value': {'value': 4.123456789, 'unit': 'px'}},
                      'alias': {'$type': 'dimension', '$value': '{size}'}}
            (root / 'tokens.json').write_text(json.dumps(source))
            plan = root / 'plan.json'
            plan.write_text(json.dumps({'changes': [{'op': 'edit', 'path': 'size', 'patch': {'$value': {'value': 8.987654321, 'unit': 'px'}}}], 'bindings': {}}))
            args = ['preview', str(root), '--source', 'tokens.json', '--plan', str(plan)]
            short, full = self.run_helper('tokens.py', *args), self.run_helper('tokens.py', *args, '--full')
            self.assertEqual(short.returncode, 0, short.stderr); self.assertEqual(full.returncode, 0, full.stderr)
            brief, complete = json.loads(short.stdout), json.loads(full.stdout)
            for key in ('changes', 'affected_tokens', 'resolved_value_diffs', 'consumer_impact', 'validation'):
                self.assertEqual(brief[key], complete[key])
            self.assertEqual(brief['resolved_value_diffs']['alias']['before']['value'], 4.123456789)
            self.assertEqual(brief['resolved_value_diffs']['alias']['after']['value'], 8.987654321)
            self.assertNotIn('files', brief)

    def test_errors_remain_visible_in_both_modes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'bad.json').write_text('{"x":1,"x":2}')
            for extra in ([], ['--full']):
                result = self.run_helper('tokens.py', 'validate', str(root), '--source', 'bad.json', *extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('duplicada', result.stderr)
