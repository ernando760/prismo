"""Spacing: vetores aritméticos, aliases DTCG e preservação de fundações."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/prismo/scripts/spacing.py'
spec = importlib.util.spec_from_file_location('spacing', SCRIPT)
s = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(SCRIPT.parent))
spec.loader.exec_module(s)


def plan():
    return json.loads((ROOT / 'tests/fixtures/spacing-plan.json').read_text())


class SpacingTests(unittest.TestCase):
    def test_base_four_linear_known_values(self):
        result = s.build(plan())
        self.assertEqual([row['dimension']['value'] for row in result['scale']], [0, 4, 8, 12, 16, 24])
        self.assertEqual([row['flutter_logical_px'] for row in result['scale']], [0, 4, 8, 12, 16, 24])

    def test_linear_start_and_increment(self):
        p = plan(); p['progression'].update(start=.5, increment=.5)
        self.assertEqual([row['dimension']['value'] for row in s.build(p)['scale']], [2, 4, 6, 8, 10, 14])

    def test_custom_fractional_multipliers(self):
        p = plan(); p['progression'] = {'type': 'custom'}
        p['steps'] = {'none': 0, 'xs': .5, 'sm': 1.5, 'md': 2, 'lg': 5, 'xl': 7.5}
        self.assertEqual([row['dimension']['value'] for row in s.build(p)['scale']], [0, 2, 6, 8, 20, 30])

    def test_grid_rounding_modes_and_ties(self):
        for mode, expected in [('half_up', 8), ('floor', 4), ('ceil', 8)]:
            self.assertEqual(s.calculate(4, 1.5, {'mode': mode, 'increment': 4}), (6, expected))
        self.assertEqual(s.calculate(.1, 3, {'mode': 'half_up', 'increment': .1}), (.3, .3))
        self.assertEqual(s.calculate(1, 1.005, {'mode': 'half_up', 'increment': .01}), (1.005, 1.01))

    def test_rounding_duplicate_and_zero_use_aliases(self):
        p = plan(); p['progression']['increment'] = .1
        result = s.build(p)
        tokens = s.index(result['tokens'])
        self.assertEqual(tokens['primitive.spacing.xs'][1], '{primitive.spacing.none}')
        dimensions = [value for kind, value in tokens.values() if kind == 'dimension' and not s.alias(value)]
        self.assertEqual(len(dimensions), len({json.dumps(d, sort_keys=True) for d in dimensions}))

    def test_dtcg_semantic_dimensions_and_aliases(self):
        result = s.build(plan()); tokens = s.index(result['tokens'])
        for usage, role, expected in [('gap', 'compact', 8), ('padding', 'container', 16), ('margin', 'section', 24)]:
            path = f'semantic.spacing.{usage}.{role}'
            self.assertEqual(tokens[path][0], 'dimension')
            self.assertTrue(s.alias(tokens[path][1]))
            self.assertEqual(s.resolve(tokens, path), {'value': expected, 'unit': 'px'})

    def test_rem_conversion_requires_explicit_root(self):
        p = plan(); p['base'] = {'value': .25, 'unit': 'rem'}
        p['rounding']['increment'] = .0001; p['root_px'] = 16
        result = s.build(p)
        self.assertEqual(result['scale'][2]['dimension'], {'value': .5, 'unit': 'rem'})
        self.assertEqual(result['scale'][2]['flutter_logical_px'], 8)
        p['root_px'] = 20
        self.assertEqual(s.build(p)['scale'][2]['flutter_logical_px'], 10)
        p['root_px'] = None
        with self.assertRaises(ValueError):
            s.build(p)

    def test_css_projection_preserves_exported_precision(self):
        p = plan(); p['base']['value'] = .12345678; p['rounding']['increment'] = .00000001
        self.assertEqual(s.build(p)['scale'][1]['web'], '0.12345678px')

    def test_explicit_legacy_alias_reuse_preserves_metadata(self):
        existing = {'space': {'$type': 'dimension', 'small': {'$value': {'value': 8, 'unit': 'px'}, '$description': 'keep'}}}
        p = plan(); p['steps']['sm'] = '{space.small}'
        result = s.build(p, existing)
        self.assertEqual(result['tokens']['space'], existing['space'])
        self.assertEqual(s.index(result['tokens'])['primitive.spacing.sm'][1], '{space.small}')

    def test_reuse_only_and_idempotency(self):
        existing = s.build(plan())['tokens']
        p = plan(); p['steps'] = {}
        self.assertEqual(s.build(p, existing)['tokens'], existing)
        self.assertEqual(s.build(plan(), existing)['tokens'], existing)

    def test_collision_and_input_immutability(self):
        p = plan(); before = copy.deepcopy(p)
        first = s.build(p)
        self.assertEqual(first, s.build(p)); self.assertEqual(p, before)
        existing = first['tokens']; old = copy.deepcopy(existing)
        p['base']['value'] = 8
        with self.assertRaisesRegex(ValueError, 'Colisão'):
            s.build(p, existing)
        self.assertEqual(existing, old)

    def test_missing_wrong_type_cycle_and_negative_existing(self):
        for existing in [{}, {'old': {'$type': 'number', '$value': 4}},
                         {'old': {'$type': 'dimension', '$value': '{old}'}},
                         {'old': {'$type': 'dimension', '$value': {'value': -4, 'unit': 'px'}}}]:
            p = plan(); p['steps']['sm'] = '{old}'
            with self.assertRaises(ValueError):
                s.build(p, existing)

    def test_invalid_parameters(self):
        for field, value in [('root_px', 0), ('progression', {'type': 'geometric'}),
                             ('rounding', {'mode': 'random', 'increment': 1}),
                             ('rounding', {'mode': 'floor', 'increment': 0}),
                             ('semantics', {}), ('semantics', {'radius': {'x': '{missing}'}})]:
            p = plan(); p[field] = value
            with self.assertRaises(ValueError):
                s.build(p)
        for value in (0, -1, True, math.nan, math.inf):
            p = plan(); p['base']['value'] = value
            with self.assertRaises(ValueError):
                s.build(p)
        for value in (True, -.5, 1.5):
            p = plan(); p['steps']['sm'] = value
            with self.assertRaises(ValueError):
                s.build(p)
        for unit in ('em', 'sp', 'dp', '%'):
            p = plan(); p['base']['unit'] = unit
            with self.assertRaises(ValueError):
                s.build(p)

    def test_invalid_groups_references_and_semantic_literals(self):
        p = plan(); p['semantics']['gap']['compact'] = 8
        with self.assertRaises(ValueError):
            s.build(p)
        for tree in [{'legacy': {'$extends': '{base}'}}, {'primitive': {'$type': 'number', '$value': 2}}]:
            with self.assertRaises(ValueError):
                s.build(plan(), tree)

    def test_no_implicit_dependency_on_typographic_dimensions(self):
        existing = {'primitive': {'typography': {'size': {'body': {'$type': 'dimension', '$value': {'value': 16, 'unit': 'px'}}}}}}
        result = s.build(plan(), existing)
        self.assertEqual(result['tokens']['primitive']['spacing']['lg']['$value'], {'value': 16, 'unit': 'px'})
        self.assertEqual(result['tokens']['primitive']['typography'], existing['primitive']['typography'])

    def test_cli_preserves_colors_typography_and_decisions(self):
        def run(script, args):
            return subprocess.run([sys.executable, str(ROOT / 'skills/prismo/scripts' / script), *args, '--full'], capture_output=True, text=True, check=True)
        with tempfile.TemporaryDirectory(prefix='prismo spacing ') as tmp:
            directory = Path(tmp)
            colors = json.loads(run('colors.py', ['palette', '--plan', str(ROOT / 'tests/fixtures/colors-plan.json')]).stdout)['tokens']
            token_file = directory / 'tokens.json'; token_file.write_text(json.dumps(colors))
            typography = json.loads(run('typography.py', ['--plan', str(ROOT / 'tests/fixtures/typography-plan.json'), '--existing', str(token_file)]).stdout)['tokens']
            token_file.write_text(json.dumps(typography))
            decisions = directory / 'decisions.json'
            decisions.write_text(json.dumps({'foundations': {'colors': {'approved': True}, 'typography': {'approved': True}}}))
            before = {p.name: p.read_bytes() for p in directory.iterdir()}
            result = json.loads(run('spacing.py', ['--plan', str(ROOT / 'tests/fixtures/spacing-plan.json'), '--existing', str(token_file)]).stdout)
            self.assertEqual(result['status'], 'preview')
            self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})
            for layer in ('primitive', 'semantic'):
                for name, value in typography[layer].items():
                    self.assertEqual(result['tokens'][layer][name], value)

    def test_cli_invalid_plan_fails_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'plan.json'; path.write_text('{}')
            result = subprocess.run([sys.executable, str(SCRIPT), '--plan', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1); self.assertFalse(result.stdout)
            self.assertEqual(list(Path(tmp).iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
