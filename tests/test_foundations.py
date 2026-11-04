"""Fluxo persistente de foundations: escopo, ordem, retomada e preservação."""
import copy
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/prismo/scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('foundations', SCRIPTS / 'foundations.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


def plans(*names):
    result = {}
    for name in names or f.ORDER:
        plan = json.loads((ROOT / 'tests/fixtures' / (name + '-plan.json')).read_text())
        result[name] = {'plan': plan, 'sources': {
            key: {'origin': 'user', 'evidence': 'Explicit test design brief'} for key in plan},
            'pending': ['Revisão visual em contexto real.']}
    return result


class FoundationsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='prismo foundations ')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'custom-ds').mkdir()
        self.decisions = self.root / 'custom-ds/decisions.json'
        self.tokens = self.root / 'custom-ds/tokens.json'
        self.checklist = self.root / 'custom-ds/foundations-plan.json'
        self.record = {'prismo_version': 1, 'decisions': {'identity': 'Approved identity',
            'paths': {'tokens': 'custom-ds/tokens.json'}}, 'unrelated': {'keep': True}}
        self.decisions.write_text(json.dumps(self.record))
        self.existing = {'legacy': {'$type': 'number', '$value': 42, '$description': 'preserve'}}
        self.tokens.write_text(json.dumps(self.existing))

    def run_flow(self, names=None, specs=None):
        return f.execute(self.root, names, specs, 'custom-ds/decisions.json')

    def load(self, path):
        return json.loads(path.read_text())

    def assert_completed(self, state, names):
        for name in names:
            self.assertEqual(state['steps'][name]['status'], 'completed', state['steps'][name])
            self.assertEqual(state['steps'][name]['checks']['persisted'], 'passed')
            self.assertIn('validation', state['steps'][name])

    def test_complete_in_order_and_preserve_existing_data(self):
        state = self.run_flow(specs=plans())
        self.assertEqual(list(state['steps']), list(f.ORDER))
        self.assert_completed(state, f.ORDER)
        record, tokens = self.load(self.decisions), self.load(self.tokens)
        for key, value in self.record.items():
            self.assertEqual(record[key], value)
        self.assertEqual(tokens['legacy'], self.existing['legacy'])
        self.assertEqual(list(record['foundations']), list(f.ORDER))
        self.assertEqual(self.load(self.checklist), state)

    def test_partial_order_deduplication_and_only_requested_foundations(self):
        state = self.run_flow(['elevation', 'spacing', 'spacing'], plans('spacing', 'elevation'))
        self.assertEqual(state['requested'], ['spacing', 'elevation'])
        self.assert_completed(state, state['requested'])
        self.assertEqual(list(self.load(self.decisions)['foundations']), ['spacing', 'elevation'])
        self.assertNotIn('borders', self.load(self.tokens)['primitive'])

    def test_each_individual_foundation_without_implicit_dependencies(self):
        for name in f.ORDER:
            with self.subTest(name=name):
                self.tokens.write_text(json.dumps(self.existing))
                self.decisions.write_text(json.dumps(self.record))
                self.checklist.unlink(missing_ok=True)
                state = self.run_flow([name], plans(name))
                self.assert_completed(state, [name])
                self.assertEqual(list(state['steps']), [name])
                self.assertEqual(list(self.load(self.decisions)['foundations']), [name])

    def test_resume_completed_without_rewriting_tokens_or_decisions(self):
        self.run_flow(specs=plans())
        before = [(p.read_bytes(), p.stat().st_mtime_ns) for p in (self.tokens, self.decisions)]
        state = self.run_flow()
        self.assert_completed(state, f.ORDER)
        self.assertEqual(before, [(p.read_bytes(), p.stat().st_mtime_ns) for p in (self.tokens, self.decisions)])

    def test_extend_partial_request_without_recreating_completed(self):
        first = self.run_flow(['spacing'], plans('spacing'))
        saved = copy.deepcopy(self.load(self.decisions)['foundations']['spacing'])
        state = self.run_flow(['borders', 'spacing'], plans('borders'))
        self.assert_completed(state, ['spacing', 'borders'])
        self.assertEqual(state['steps']['spacing']['spec'], first['steps']['spacing']['spec'])
        self.assertEqual(self.load(self.decisions)['foundations']['spacing'], saved)

    def test_resume_same_values_preserves_original_decision_origins(self):
        first = self.run_flow(['spacing'], plans('spacing'))
        data = plans('spacing')
        for source in data['spacing']['sources'].values():
            source.update(origin='existing', evidence='Saved decisions from previous request')
        state = self.run_flow(['spacing'], data)
        self.assert_completed(state, ['spacing'])
        self.assertEqual(state['steps']['spacing']['spec'], first['steps']['spacing']['spec'])

    def test_reference_defaults_with_explicit_identity_complete_all_foundations(self):
        data = {}
        for name in f.ORDER:
            text = (f.REFERENCES / (name + '.md')).read_text()
            plan = json.loads(re.search(r'```json\n(.*?)\n```', text, re.S)[1])
            if name == 'typography':
                plan['families']['sans'] = ['Approved Sans', 'sans-serif']
            if name == 'borders':
                plan.update(full=False, bounds_px=None)
                del plan['semantics']['radius']['pill']
            data[name] = {'plan': plan, 'sources': {key: {
                'origin': 'default', 'evidence': 'references/' + name + '.md: Padrões seguros'}
                for key in plan}, 'pending': ['Revisão visual em contexto real.']}
        for key in ('palettes', 'themes', 'pairs'):
            data['colors']['sources'][key].update(origin='user', evidence='Explicit brand, light theme and usage brief')
        for key in ('families', 'weights'):
            data['typography']['sources'][key].update(origin='existing', evidence='Project font configuration')
        state = self.run_flow(specs=data)
        self.assert_completed(state, f.ORDER)
        self.assertFalse(self.load(self.tokens)['primitive']['borders']['radius'].get('full'))

    def test_concurrent_helper_is_blocked_without_modifying_inputs(self):
        lock = self.decisions.with_name('.foundations-plan.lock')
        with lock.open('a') as stream:
            f.fcntl.flock(stream, f.fcntl.LOCK_EX | f.fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError, 'ativa'):
                self.run_flow(['spacing'], plans('spacing'))
        self.assertFalse(self.checklist.exists())
        self.assertEqual(self.load(self.decisions), self.record)

    def test_external_edit_during_calculation_is_not_overwritten(self):
        calculate = f.calculate
        def edited(name, plan, tokens):
            result = calculate(name, plan, tokens)
            self.tokens.write_text(json.dumps({**self.existing, 'new': {'$type': 'number', '$value': 7}}))
            return result
        with patch.object(f, 'calculate', side_effect=edited):
            state = self.run_flow(['spacing', 'borders'], plans('spacing', 'borders'))
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertEqual(state['steps']['borders']['status'], 'pending')
        self.assertEqual(self.load(self.tokens)['new']['$value'], 7)
        self.assertEqual(self.load(self.decisions), self.record)

    def test_journal_cannot_target_an_unrelated_project_file(self):
        self.run_flow(['spacing'], plans('spacing'))
        unrelated = self.root / 'unrelated.txt'; unrelated.write_text('keep')
        state = self.load(self.checklist)
        state['steps']['spacing']['transaction'] = [
            {'path': 'unrelated.txt', 'before': 'keep', 'after': 'changed'}]
        self.checklist.write_text(json.dumps(state))
        state = self.run_flow(['spacing'])
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertEqual(unrelated.read_text(), 'keep')

    def test_missing_essential_plan_stops_and_resume_continues(self):
        state = self.run_flow(specs=plans('colors'))
        self.assert_completed(state, ['colors'])
        self.assertEqual(state['steps']['typography']['status'], 'failed')
        self.assertIn('essenciais', state['steps']['typography']['error'])
        self.assertEqual(state['steps']['spacing']['status'], 'pending')
        self.assertEqual(list(self.load(self.decisions)['foundations']), ['colors'])
        state = self.run_flow(specs=plans('typography', 'spacing', 'borders', 'elevation'))
        self.assert_completed(state, f.ORDER)

    def test_invalid_stage_records_failure_and_does_not_advance(self):
        data = plans()
        data['spacing']['plan']['base']['value'] = -1
        state = self.run_flow(specs=data)
        self.assert_completed(state, ['colors', 'typography'])
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertEqual(state['steps']['borders']['status'], 'pending')
        state = self.run_flow(specs=plans('spacing', 'borders', 'elevation'))
        self.assert_completed(state, f.ORDER)

    def test_resume_keeps_plans_for_stages_not_yet_reached(self):
        data = plans()
        data['colors']['plan']['pairs'][0]['foreground'] = 'semantic.light.surface'
        state = self.run_flow(specs=data)
        self.assertEqual(state['steps']['colors']['status'], 'failed')
        for name in f.ORDER[1:]:
            self.assertEqual(state['steps'][name]['status'], 'pending')
            self.assertEqual(state['steps'][name]['spec'], data[name])
        state = self.run_flow(specs=plans('colors'))
        self.assert_completed(state, f.ORDER)

    def test_approved_decision_conflict_does_not_overwrite(self):
        self.run_flow(['spacing'], plans('spacing'))
        before = [p.read_bytes() for p in (self.tokens, self.decisions)]
        data = plans('spacing'); data['spacing']['plan']['base']['value'] = 8
        state = self.run_flow(['spacing'], data)
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertIn('Conflito', state['steps']['spacing']['error'])
        self.assertEqual(before, [p.read_bytes() for p in (self.tokens, self.decisions)])
        self.assert_completed(self.run_flow(['spacing']), ['spacing'])

    def test_legacy_approved_record_is_reused_without_overwriting_metadata(self):
        data = plans('spacing')['spacing']
        self.record['foundations'] = {'spacing': {**data, 'approved': True, 'notes': 'keep'}}
        self.decisions.write_text(json.dumps(self.record))
        self.tokens.write_text(json.dumps(f.calculate('spacing', data['plan'], self.existing)['tokens']))
        before = [p.read_bytes() for p in (self.tokens, self.decisions)]
        state = self.run_flow(['spacing'])
        self.assert_completed(state, ['spacing'])
        self.assertTrue(all(s['origin'] == 'existing' for s in state['steps']['spacing']['spec']['sources'].values()))
        self.assertEqual(before, [p.read_bytes() for p in (self.tokens, self.decisions)])

    def test_existing_record_without_plan_requires_clarification(self):
        self.record['foundations'] = {'spacing': {'approved': True}}
        self.decisions.write_text(json.dumps(self.record))
        state = self.run_flow(['spacing'], plans('spacing'))
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertEqual(self.load(self.decisions), self.record)

    def test_malformed_existing_decisions_are_preserved(self):
        self.record['foundations'] = {'spacing': None}
        self.decisions.write_text(json.dumps(self.record))
        state = self.run_flow(['spacing'], plans('spacing'))
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertEqual(self.load(self.decisions), self.record)
        self.record['decisions'] = None
        self.decisions.write_text(json.dumps(self.record))
        with self.assertRaisesRegex(ValueError, 'Configuração'):
            self.run_flow(['spacing'], plans('spacing'))
        self.assertEqual(self.load(self.decisions), self.record)

    def test_collision_does_not_rename_or_modify_existing_tokens(self):
        existing = f.calculate('spacing', plans('spacing')['spacing']['plan'], {})['tokens']
        existing['primitive']['spacing']['xs']['$value'] = {'value': 99, 'unit': 'px'}
        self.tokens.write_text(json.dumps(existing))
        before = self.tokens.read_bytes()
        state = self.run_flow(['spacing', 'borders'], plans('spacing', 'borders'))
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertEqual(state['steps']['borders']['status'], 'pending')
        self.assertEqual(before, self.tokens.read_bytes())

    def test_contrast_failure_is_not_treated_as_success(self):
        data = plans('colors')
        pair = data['colors']['plan']['pairs'][0]
        pair['foreground'] = pair['background']
        state = self.run_flow(['colors'], data)
        self.assertEqual(state['steps']['colors']['status'], 'failed')
        self.assertIn('AA', state['steps']['colors']['error'])
        self.assertEqual(self.load(self.tokens), self.existing)

    def test_decision_origins_and_pending_items_are_persisted(self):
        data = plans('spacing')
        data['spacing']['sources']['base'] = {'origin': 'default', 'evidence': 'references/spacing.md#padrões-seguros'}
        data['spacing']['sources']['root_px'] = {'origin': 'existing', 'evidence': 'decisions.paths'}
        self.run_flow(['spacing'], data)
        record = self.load(self.decisions)['foundations']['spacing']
        self.assertEqual(record['sources'], data['spacing']['sources'])
        self.assertEqual(record['pending'], data['spacing']['pending'])

    def test_missing_provenance_fails_before_persistence(self):
        data = plans('spacing'); del data['spacing']['sources']['base']
        state = self.run_flow(['spacing'], data)
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertNotIn('persisted', state['steps']['spacing']['checks'])
        self.assertEqual(self.load(self.tokens), self.existing)

    def test_interrupted_transaction_is_completed_without_losing_decisions(self):
        original = f.atomic
        def interrupt(path, content):
            if path == self.decisions:
                raise KeyboardInterrupt()
            original(path, content)
        with patch.object(f, 'atomic', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_flow(['spacing'], plans('spacing'))
        self.assertIn('transaction', self.load(self.checklist)['steps']['spacing'])
        state = self.run_flow(['spacing'])
        self.assert_completed(state, ['spacing'])
        self.assertNotIn('transaction', state['steps']['spacing'])
        self.assertEqual(self.load(self.decisions)['unrelated'], self.record['unrelated'])

    def test_interrupted_transaction_blocks_other_scope_until_recovered(self):
        original = f.atomic
        def interrupt(path, content):
            if path == self.decisions:
                raise KeyboardInterrupt()
            original(path, content)
        with patch.object(f, 'atomic', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_flow(['spacing'], plans('spacing'))
        before = [p.read_bytes() for p in (self.tokens, self.decisions, self.checklist)]
        with self.assertRaisesRegex(ValueError, 'Transação pendente em spacing'):
            self.run_flow(['borders'], plans('borders'))
        self.assertEqual(before, [p.read_bytes() for p in (self.tokens, self.decisions, self.checklist)])
        state = self.run_flow(['spacing'])
        self.assert_completed(state, ['spacing'])
        self.assertNotIn('transaction', state['steps']['spacing'])
        state = self.run_flow(['borders'], plans('borders'))
        self.assert_completed(state, ['borders'])
        self.assertEqual(set(self.load(self.decisions)['foundations']), {'spacing', 'borders'})

    def test_recovery_precedes_other_requested_steps_and_checks_external_edits(self):
        original = f.atomic
        def interrupt(path, content):
            if path == self.decisions:
                raise KeyboardInterrupt()
            original(path, content)
        with patch.object(f, 'atomic', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_flow(['spacing'], plans('spacing'))
        self.decisions.write_text(json.dumps({**self.record, 'external_edit': True}))
        before = [p.read_bytes() for p in (self.tokens, self.decisions)]
        with patch.object(f, 'calculate', wraps=f.calculate) as calculate:
            state = self.run_flow(['colors', 'spacing'], plans('colors'))
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertIn('Conflito durante retomada', state['steps']['spacing']['error'])
        self.assertEqual(state['steps']['colors']['status'], 'pending')
        calculate.assert_not_called()
        self.assertEqual(before, [p.read_bytes() for p in (self.tokens, self.decisions)])

    def test_recovery_runs_first_when_original_step_is_in_broader_scope(self):
        original = f.atomic
        def interrupt(path, content):
            if path == self.decisions:
                raise KeyboardInterrupt()
            original(path, content)
        with patch.object(f, 'atomic', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_flow(['spacing'], plans('spacing'))
        with patch.object(f, 'calculate', wraps=f.calculate) as calculate:
            state = self.run_flow(['colors', 'spacing'], plans('colors'))
        self.assert_completed(state, ['spacing', 'colors'])
        self.assertEqual(calculate.call_args_list[0].args[0], 'spacing')
        self.assertEqual(state['requested'], ['colors', 'spacing'])
        self.assertNotIn('transaction', state['steps']['spacing'])

    def test_multiple_pending_journals_are_rejected_without_changes(self):
        self.run_flow(['spacing', 'borders'], plans('spacing', 'borders'))
        state = self.load(self.checklist)
        for name in ('spacing', 'borders'):
            state['steps'][name]['transaction'] = []
        self.checklist.write_text(json.dumps(state))
        before = [p.read_bytes() for p in (self.tokens, self.decisions, self.checklist)]
        with self.assertRaisesRegex(ValueError, 'Múltiplas transações pendentes'):
            self.run_flow(['spacing', 'borders'])
        self.assertEqual(before, [p.read_bytes() for p in (self.tokens, self.decisions, self.checklist)])

    def test_empty_journal_preserves_interrupted_plan(self):
        self.run_flow(['spacing'], plans('spacing'))
        state = self.load(self.checklist)
        step = state['steps']['spacing']
        step['status'] = 'running'
        step.pop('completed_once')
        step['transaction'] = []
        self.checklist.write_text(json.dumps(state))
        before = [p.read_bytes() for p in (self.tokens, self.decisions)]
        changed = plans('spacing')
        changed['spacing']['plan']['base']['value'] = 8
        result = self.run_flow(['spacing'], changed)
        self.assertEqual(result['steps']['spacing']['status'], 'failed')
        self.assertIn('Conflito com etapa persistida', result['steps']['spacing']['error'])
        self.assertEqual(result['steps']['spacing']['spec'], step['spec'])
        self.assertEqual(before, [p.read_bytes() for p in (self.tokens, self.decisions)])

    def test_external_edit_during_interrupted_write_blocks_recovery(self):
        original = f.atomic
        def interrupt(path, content):
            if path == self.decisions:
                raise KeyboardInterrupt()
            original(path, content)
        with patch.object(f, 'atomic', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_flow(['spacing'], plans('spacing'))
        self.decisions.write_text(json.dumps({**self.record, 'new_decision': 'keep'}))
        before = self.decisions.read_bytes()
        state = self.run_flow(['spacing'])
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertIn('Conflito durante retomada', state['steps']['spacing']['error'])
        self.assertEqual(before, self.decisions.read_bytes())

    def test_completed_tokens_removed_are_not_silently_recreated(self):
        self.run_flow(['spacing'], plans('spacing'))
        self.tokens.write_text(json.dumps(self.existing))
        state = self.run_flow(['spacing'])
        self.assertEqual(state['steps']['spacing']['status'], 'failed')
        self.assertNotIn('persisted', state['steps']['spacing']['checks'])
        self.assertEqual(self.load(self.tokens), self.existing)

    def test_invalid_scope_is_rejected_without_creating_checklist(self):
        for names in ([], ['unknown']):
            with self.assertRaises(ValueError):
                self.run_flow(names)
        with self.assertRaises(ValueError):
            self.run_flow(['spacing'], plans('borders'))
        self.assertFalse(self.checklist.exists())

    def test_symlink_and_overlapping_destinations_rejected(self):
        self.checklist.symlink_to(self.tokens)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.run_flow(['spacing'], plans('spacing'))
        self.checklist.unlink()
        self.record['decisions']['paths']['tokens'] = 'custom-ds/decisions.json'
        self.decisions.write_text(json.dumps(self.record))
        with self.assertRaisesRegex(ValueError, 'sobrepostos'):
            self.run_flow(['spacing'], plans('spacing'))

    def test_cli_custom_paths_and_failure_exit_codes(self):
        manifest = self.root / 'plans.json'; manifest.write_text(json.dumps(plans('spacing')))
        args = [sys.executable, str(SCRIPTS / 'foundations.py'), str(self.root),
                '--decisions', 'custom-ds/decisions.json', '--only', 'spacing', '--plans', str(manifest)]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_completed(json.loads(result.stdout), ['spacing'])
        result = subprocess.run(args[:5] + ['--only', 'typography'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)['steps']['typography']['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
