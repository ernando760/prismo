"""CLI planning contract: strict opt-in, stdin, diagnostics and incremental previews."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_colors_evolution import plan

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/prismo/scripts/colors.py'


class ColorsCLIContractTests(unittest.TestCase):
    def call(self, value, *flags, existing=None, filename=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'tokens.json'
            source.write_text(json.dumps(existing or {}))
            before = source.read_bytes()
            path = root / 'plan.json'
            path.write_text(json.dumps(value))
            args = [sys.executable, '-B', str(SCRIPT), 'palette', '--plan',
                    str(path) if filename else '-', '--existing', str(source), *flags]
            result = subprocess.run(args, input=None if filename else json.dumps(value),
                                    capture_output=True, text=True)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['plan.json', 'tokens.json'])
            return result

    def test_subcommand_help_exposes_json_contract_and_examples(self):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), 'palette', '--help'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        for term in ('--require-coverage', '--plan -', 'normal_text', 'large_text', 'non_text',
                     'light', 'dark', 'coverage', 'partial', 'functional', 'evolution',
                     'colors-coverage-plan.json'):
            self.assertIn(term, result.stdout)

    def test_legacy_accepted_but_strict_missing_coverage_rejected(self):
        p = plan(); del p['coverage']
        legacy = self.call(p)
        self.assertEqual(legacy.returncode, 0, legacy.stderr)
        self.assertEqual(json.loads(legacy.stdout)['coverage']['status'], 'unknown_legacy')
        strict = self.call(p, '--require-coverage')
        self.assertEqual(strict.returncode, 1)
        self.assertEqual(strict.stdout, '')
        self.assertIn('plan.coverage', strict.stderr)

    def test_stdin_and_file_are_equivalent_in_summary_and_full(self):
        for flags in (('--require-coverage',), ('--require-coverage', '--full')):
            stdin = self.call(plan(), *flags)
            file = self.call(plan(), *flags, filename=True)
            self.assertEqual(stdin.returncode, 0, stdin.stderr)
            self.assertEqual(file.returncode, 0, file.stderr)
            self.assertEqual(json.loads(stdin.stdout), json.loads(file.stdout))

    def test_empty_or_invalid_coverage_does_not_satisfy_strict_mode(self):
        for coverage in (None, {}, {'version': 1, 'uses': [], 'steps': []}):
            p = {'palettes': {}, 'themes': {'light': {}}, 'pairs': [], 'coverage': coverage}
            result = self.call(p, '--require-coverage')
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, '')
            self.assertTrue(result.stderr.strip())

    def test_invalid_usage_has_field_diagnostic_and_no_json(self):
        p = plan(); del p['coverage']; p['pairs'][0]['usage'] = 'ui_component'
        result = self.call(p)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertIn('pairs[0].usage', result.stderr)
        self.assertIn('non_text', result.stderr)
        self.assertNotIn('JSONDecodeError', result.stderr)

    def test_other_failed_recovery_inputs_explain_valid_alternatives(self):
        p = plan(); del p['coverage']; p['themes'] = {}
        result = self.call(p)
        self.assertEqual(result.returncode, 1)
        self.assertIn('light', result.stderr)
        p['themes'] = {'light': {}}; p['pairs'] = []
        result = self.call(p)
        self.assertEqual(result.returncode, 1)
        self.assertIn('coverage', result.stderr)

    def test_incremental_subset_does_not_require_history_or_create_aliases(self):
        complete = self.call(plan(), '--require-coverage', '--full')
        existing = json.loads(complete.stdout)['tokens']
        existing['unrelated'] = {'$type': 'color', '$value': {
            'colorSpace': 'srgb', 'components': [1, 0, 0], 'alpha': 1}}
        row = copy.deepcopy(plan()['coverage']['uses'][0])
        row.update(id='affected-link', use='Link default', decision='reuse')
        p = {'palettes': {}, 'themes': {'light': {}}, 'pairs': row['pairs'],
             'coverage': {'version': 1, 'uses': [row], 'steps': []}}
        before = copy.deepcopy(existing)
        result = self.call(p, '--require-coverage', '--full', existing=existing)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['tokens'], before)
        self.assertEqual([u['id'] for u in output['coverage']['uses']], ['affected-link'])
        self.assertEqual(output['coverage']['uses'][0]['status'], 'partial')
        self.assertEqual(output['coverage']['conformance'], 'not_assessed')

    def test_planning_without_pairs_is_valid_without_fabricated_calculation(self):
        row = copy.deepcopy(plan()['coverage']['uses'][0])
        row.update(horizon='evolution', status='not_evaluated', decision='undecided', tokens=[], pairs=[])
        p = {'palettes': {}, 'themes': {'light': {}}, 'pairs': [],
             'coverage': {'version': 1, 'uses': [row], 'steps': []}}
        result = self.call(p, '--require-coverage')
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['token_changes'], [])
        self.assertEqual(output['coverage']['uses'][0]['calculation'], 'not_evaluated')
        self.assertEqual(output['coverage']['uses'][0]['visual']['status'], 'pending')

    def test_malformed_stdin_is_a_diagnostic_not_a_partial_result(self):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), 'palette',
                                 '--plan', '-', '--require-coverage'], input='{"coverage":',
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertTrue(result.stderr.startswith('Erro:'))
