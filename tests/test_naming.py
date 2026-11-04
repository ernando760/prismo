"""Regressões da política opcional e sua integração com foundations."""
import copy
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/prismo/scripts'))
import foundations
import naming
import init
import tokens
import audit

CUSTOM = {'version': 1, 'mode': 'custom', 'levels': {
    'primitive': {'prefix': 'base'}, 'semantic': {'prefix': 'role'},
    'component': {'prefix': 'widget'}}, 'vocabulary': {'states': ['hover', 'pressed']}}


def transform(value):
    if isinstance(value, dict):
        return {k: transform(v) for k, v in value.items()}
    if isinstance(value, list):
        return [transform(v) for v in value]
    if isinstance(value, str):
        return value.replace('primitive.', 'base.').replace('semantic.', 'role.')
    return value


def specs():
    result = {}
    for name in foundations.ORDER:
        plan = transform(json.loads((ROOT / 'tests/fixtures' / (name + '-plan.json')).read_text()))
        result[name] = {'plan': plan, 'sources': {k: {'origin': 'user', 'evidence': 'brief'} for k in plan}, 'pending': []}
    return result


class NamingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'ds').mkdir()
        self.decisions = self.root / 'ds/decisions.json'
        self.tokenfile = self.root / 'ds/tokens.json'
        self.record = {'decisions': {'paths': {'tokens': 'ds/tokens.json'}, 'naming': CUSTOM}}
        self.decisions.write_text(json.dumps(self.record))
        self.tokenfile.write_text('{}')

    def run_flow(self, names=None, plans=None):
        return foundations.execute(self.root, names, plans, 'ds/decisions.json')

    def test_contract_and_ambiguous_prefixes(self):
        self.assertIsNone(naming.policy(None))
        self.assertEqual(naming.policy({'version': 1, 'mode': 'recommended'})['levels']['semantic']['prefix'], 'semantic')
        self.assertEqual(naming.policy(CUSTOM)['vocabulary']['states'], ['hover', 'pressed'])
        for bad in ({'version': 1, 'mode': 'unknown'}, {'version': 1, 'mode': 'custom', 'levels': {'semantic': {'prefix': 'primitive'}}}, {'version': 1, 'mode': 'custom', 'vocabulary': {'states': ['hover', 'hover']}}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                naming.policy(bad)
        empty = copy.deepcopy(CUSTOM); empty['levels']['primitive']['prefix'] = ''
        self.assertEqual(naming.path('primitive', 'color.brand.500', naming.policy(empty)), 'color.brand.500')
        self.assertEqual(naming.diagnose(['color.brand.500'], naming.policy(empty))['findings'][0]['certainty'], 'manual')

    def test_init_optional_policy_roundtrip(self):
        plan = {'name': 'DS', 'platforms': ['web'], 'identity': 'existing',
                'accessibility': 'AA', 'documentation': {'central': 'deferred', 'web': 'deferred'},
                'evidence': [], 'reuse': [], 'pending': [],
                'paths': {'decisions': 'new/decisions.json', 'tokens': 'new/tokens.json', 'components': {}}}
        init.validate(plan)
        plan['naming'] = CUSTOM
        files, _ = init.prepare(self.root, plan)
        self.assertEqual(json.loads(files['new/decisions.json'])['decisions']['naming'], CUSTOM)
        plan['naming'] = {'version': 1, 'mode': 'invalid'}
        with self.assertRaises(ValueError):
            init.validate(plan)

    def test_tokens_cli_separates_naming_and_dtcg(self):
        tree = {'legacy': {'$type': 'number', '$value': 2}, 'base': {'x': {'$type': 'number', '$value': 1}}}
        self.tokenfile.write_text(json.dumps(tree))
        command = [sys.executable, str(ROOT / 'skills/prismo/scripts/tokens.py'), 'validate', str(self.root), '--decisions', 'ds/decisions.json']
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['validation'], 'passed_supported_subset')
        self.assertEqual(output['naming']['findings'][0]['path'], 'legacy')
        self.assertEqual(output['naming']['findings'][0]['certainty'], 'manual')
        record = copy.deepcopy(self.record); del record['decisions']['naming']
        self.decisions.write_text(json.dumps(record))
        output = json.loads(subprocess.run(command, text=True, capture_output=True, check=True).stdout)
        self.assertNotIn('naming', output)

    def test_all_foundations_custom_aliases_and_resume(self):
        state = self.run_flow(plans=specs())
        for name in foundations.ORDER:
            self.assertEqual(state['steps'][name]['status'], 'completed', state['steps'][name])
        tree = json.loads(self.tokenfile.read_text())
        self.assertIn('base', tree); self.assertIn('role', tree)
        self.assertNotIn('primitive', tree); self.assertNotIn('semantic', tree)
        tokens.validate({'ds/tokens.json': tree})
        original = (self.tokenfile.read_bytes(), self.decisions.read_bytes())
        resumed = self.run_flow()
        self.assertTrue(all(resumed['steps'][n]['status'] == 'completed' for n in foundations.ORDER))
        self.assertEqual(original, (self.tokenfile.read_bytes(), self.decisions.read_bytes()))

    def test_custom_interrupted_transaction_recovers(self):
        original = foundations.atomic
        def interrupt(path, content):
            if path == self.decisions:
                raise KeyboardInterrupt()
            original(path, content)
        with patch.object(foundations, 'atomic', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_flow(['spacing'], {'spacing': specs()['spacing']})
        state = self.run_flow(['spacing'])
        self.assertEqual(state['steps']['spacing']['status'], 'completed')
        tree = json.loads(self.tokenfile.read_text())
        self.assertIn('base', tree)
        tokens.validate({'ds/tokens.json': tree})

    def test_policy_change_blocks_resume(self):
        self.run_flow(['spacing'], {'spacing': specs()['spacing']})
        record = json.loads(self.decisions.read_text())
        record['decisions']['naming']['levels']['primitive']['prefix'] = 'other'
        self.decisions.write_text(json.dumps(record))
        before = (self.decisions.read_bytes(), self.tokenfile.read_bytes())
        with self.assertRaisesRegex(ValueError, 'mudou'):
            self.run_flow(['spacing'])
        self.assertEqual(before, (self.decisions.read_bytes(), self.tokenfile.read_bytes()))

    def test_legacy_and_custom_collision_preserved(self):
        tree = {'base': {'spacing': {'xs': {'$type': 'dimension', '$value': {'value': 99, 'unit': 'px'}}}}, 'legacy': {'$type': 'number', '$value': 2}}
        self.tokenfile.write_text(json.dumps(tree))
        before = self.tokenfile.read_bytes()
        state = self.run_flow(['spacing'], {'spacing': specs()['spacing']})
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertEqual(before, self.tokenfile.read_bytes())

    def test_audit_same_alias_target_is_only_risk(self):
        tree = {'base': {'x': {'$type': 'number', '$value': 1}}, 'role': {'a': {'$type': 'number', '$value': '{base.x}'}, 'b': {'$type': 'number', '$value': '{base.x}'}}}
        self.tokenfile.write_text(json.dumps(tree))
        result = audit.audit(self.root, decisions='ds/decisions.json')
        alias = [f for f in result['findings'] if f['code'] == 'ALIAS_REVIEW']
        self.assertEqual(len(alias), 1)
        self.assertEqual(alias[0]['certainty'], 'risk')


if __name__ == '__main__':
    unittest.main()
