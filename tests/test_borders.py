"""Borders: raios/espessuras, full, aliases e preservação das fundações."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/prismo/scripts/borders.py'
spec = importlib.util.spec_from_file_location('borders', SCRIPT)
b = importlib.util.module_from_spec(spec)
with patch.object(sys, 'path', [str(SCRIPT.parent), *sys.path]):
    spec.loader.exec_module(b)


def plan():
    return json.loads((ROOT / 'tests/fixtures/borders-plan.json').read_text())


class BorderTests(unittest.TestCase):
    def test_known_scales_and_square_radius(self):
        result = b.build(plan())
        self.assertEqual([row['value']['value'] for row in result['scales']['radius'][:-1]], [0, 4, 8])
        self.assertEqual([row['value']['value'] for row in result['scales']['width']], [0, 1, 2])
        self.assertEqual(result['scales']['radius'][0]['flutter']['radius_logical_px'], 0)

    def test_fractional_multipliers_and_rounding(self):
        for mode, expected in [('half_up', 8), ('floor', 4), ('ceil', 8)]:
            p = plan(); p['radius']['steps']['sm'] = 1.5
            p['radius']['rounding'] = {'mode': mode, 'increment': 4}
            self.assertEqual(b.build(p)['scales']['radius'][1]['value']['value'], expected)
        p = plan(); p['width']['steps']['thin'] = .5
        self.assertEqual(b.build(p)['scales']['width'][1]['value']['value'], .5)

    def test_full_capsule_circle_and_dynamic_dimensions(self):
        self.assertEqual(b.full_radius(120, 40), 20)
        self.assertEqual(b.full_radius(40, 120), 20)
        self.assertEqual(b.full_radius(40, 40), 20)
        full = b.build(plan())['scales']['radius'][-1]
        self.assertEqual(full['web']['borderRadius'], '20.0px')
        self.assertEqual(full['flutter']['shape'], 'StadiumBorder')
        p = plan(); p['bounds_px'] = None
        full = b.build(p)['scales']['radius'][-1]
        self.assertIsNone(full['web']['borderRadius'])
        self.assertEqual(full['web']['formula_px'], 'min(width,height)/2')
        self.assertIsNone(full['flutter']['radius_for_bounds'])

    def test_full_uses_normative_number_and_typed_aliases(self):
        tokens = b.index(b.build(plan())['tokens'])
        self.assertEqual(tokens['primitive.borders.radius.full'], ('number', .5))
        self.assertEqual(tokens['semantic.borders.radius.pill'], ('number', '{primitive.borders.radius.full}'))
        self.assertEqual(b.resolve(tokens, 'semantic.borders.radius.pill', 'radius'), ('number', .5))
        with self.assertRaises(ValueError):
            b.resolve(tokens, 'primitive.borders.radius.full', 'width')

    def test_semantic_aliases_and_width_zero_omits_flutter_border(self):
        result = b.build(plan()); tokens = b.index(result['tokens'])
        for usage in result['usages']:
            self.assertTrue(b.alias(tokens[usage['token']][1]))
        zero = result['scales']['width'][0]
        self.assertEqual(zero['web']['borderWidth'], '0.0px')
        self.assertEqual(zero['flutter'], {'width_logical_px': 0, 'style': 'none'})

    def test_rem_conversion_and_explicit_root(self):
        p = plan(); p['radius']['base'] = {'value': .25, 'unit': 'rem'}
        p['radius']['rounding']['increment'] = .0001; p['root_px'] = 16
        self.assertEqual(b.build(p)['scales']['radius'][1]['flutter']['radius_logical_px'], 4)
        p['root_px'] = 20
        self.assertEqual(b.build(p)['scales']['radius'][1]['flutter']['radius_logical_px'], 5)
        p['root_px'] = None
        with self.assertRaises(ValueError):
            b.build(p)

    def test_duplicate_steps_reuse_literal_via_alias(self):
        p = plan(); p['radius']['steps']['md'] = 1
        result = b.build(p)
        tokens = b.index(result['tokens'])
        self.assertEqual(tokens['primitive.borders.radius.md'][1], '{primitive.borders.radius.sm}')
        self.assertEqual(tokens['primitive.borders.width.none'][1], '{primitive.borders.radius.none}')
        literals = [v for kind, v in tokens.values() if kind == 'dimension' and not b.alias(v)]
        self.assertEqual(len(literals), len({json.dumps(v, sort_keys=True) for v in literals}))

    def test_existing_alias_and_metadata_preserved(self):
        existing = {'rounding': {'$type': 'dimension', 'small': {'$value': {'value': 4, 'unit': 'px'}, '$description': 'keep'}}}
        p = plan(); p['radius']['steps']['sm'] = '{rounding.small}'
        result = b.build(p, existing)
        self.assertEqual(result['tokens']['rounding'], existing['rounding'])
        self.assertEqual(b.index(result['tokens'])['primitive.borders.radius.sm'][1], '{rounding.small}')

    def test_idempotency_reuse_only_and_immutability(self):
        p = plan(); before = copy.deepcopy(p)
        first = b.build(p)
        self.assertEqual(b.build(p), first); self.assertEqual(p, before)
        existing = first['tokens']; old = copy.deepcopy(existing)
        self.assertEqual(b.build(p, existing)['tokens'], existing)
        p['radius']['steps'] = {}; p['width']['steps'] = {}; p['full'] = False
        self.assertEqual(b.build(p, existing)['tokens'], existing)
        self.assertEqual(existing, old)

    def test_collisions_missing_aliases_and_cycles(self):
        existing = b.build(plan())['tokens']; old = copy.deepcopy(existing)
        p = plan(); p['radius']['base']['value'] = 8
        with self.assertRaises(ValueError):
            b.build(p, existing)
        self.assertEqual(existing, old)
        for tree in ({}, {'old': {'$type': 'dimension', '$value': '{old}'}},
                     {'old': {'$type': 'number', '$value': 4}}):
            p = plan(); p['radius']['steps']['sm'] = '{old}'
            with self.assertRaises(ValueError):
                b.build(p, tree)

    def test_invalid_full_values_types_bounds_and_width(self):
        for tree in [{'x': {'$type': 'string', '$value': 'full'}},
                     {'x': {'$type': 'number', '$value': 1}},
                     {'x': {'$type': 'dimension', '$value': '{y}'}, 'y': {'$type': 'number', '$value': .5}}]:
            with self.assertRaises(ValueError):
                b.resolve(b.index(tree), 'x', 'radius')
        p = plan(); p['semantics']['width']['divider'] = '{primitive.borders.radius.full}'
        with self.assertRaises(ValueError):
            b.build(p)
        for bounds in ({'width': 0, 'height': 40}, {'width': math.inf, 'height': 40}, {}, {'width': True, 'height': 40}):
            p = plan(); p['bounds_px'] = bounds
            with self.assertRaises(ValueError):
                b.build(p)

    def test_rejects_tokens_without_purpose_and_reserved_full(self):
        p = plan(); p['radius']['steps']['unused'] = 10
        with self.assertRaisesRegex(ValueError, 'sem uso'):
            b.build(p)
        p = plan(); del p['semantics']['radius']['pill']
        with self.assertRaisesRegex(ValueError, 'sem uso'):
            b.build(p)
        p = plan(); p['radius']['steps']['full'] = 9999
        with self.assertRaises(ValueError):
            b.build(p)

    def test_invalid_numeric_units_config_and_semantics(self):
        for value in (-1, 0, True, math.nan, math.inf):
            p = plan(); p['radius']['base']['value'] = value
            with self.assertRaises(ValueError):
                b.build(p)
        for unit in ('%', 'dp', 'sp', 'em'):
            p = plan(); p['width']['base']['unit'] = unit
            with self.assertRaises(ValueError):
                b.build(p)
        for field, value in [('full', 'yes'), ('root_px', 0), ('semantics', {}), ('semantics', {'shadow': {}})]:
            p = plan(); p[field] = value
            with self.assertRaises(ValueError):
                b.build(p)
        p = plan(); p['semantics']['radius']['card'] = 8
        with self.assertRaises(ValueError):
            b.build(p)

    def test_no_implicit_dependency_on_spacing_or_typography(self):
        existing = {'primitive': {'spacing': {'four': {'$type': 'dimension', '$value': {'value': 4, 'unit': 'px'}}}}}
        result = b.build(plan(), existing)
        self.assertEqual(result['tokens']['primitive']['spacing'], existing['primitive']['spacing'])
        self.assertEqual(result['tokens']['primitive']['borders']['radius']['sm']['$value'], {'value': 4, 'unit': 'px'})

    def test_cli_preserves_three_foundations_and_decisions(self):
        def run(script, args):
            return json.loads(subprocess.run([sys.executable, str(SCRIPT.parent / script), *args, '--full'], capture_output=True, text=True, check=True).stdout)
        with tempfile.TemporaryDirectory(prefix='prismo borders ') as tmp:
            directory = Path(tmp); token_file = directory / 'tokens.json'
            tokens = run('colors.py', ['palette', '--plan', str(ROOT / 'tests/fixtures/colors-plan.json')])['tokens']
            for script, fixture in [('typography.py', 'typography-plan.json'), ('spacing.py', 'spacing-plan.json')]:
                token_file.write_text(json.dumps(tokens))
                tokens = run(script, ['--plan', str(ROOT / 'tests/fixtures' / fixture), '--existing', str(token_file)])['tokens']
            token_file.write_text(json.dumps(tokens))
            decisions = directory / 'decisions.json'; decisions.write_text(json.dumps({'foundations': {k: {'approved': True} for k in ('colors', 'typography', 'spacing')}}))
            before = {p.name: p.read_bytes() for p in directory.iterdir()}
            result = run('borders.py', ['--plan', str(ROOT / 'tests/fixtures/borders-plan.json'), '--existing', str(token_file)])
            self.assertEqual(result['status'], 'preview')
            self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})
            for layer in ('primitive', 'semantic'):
                for key, value in tokens[layer].items():
                    self.assertEqual(result['tokens'][layer][key], value)

    def test_cli_invalid_plan_no_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'plan.json'; path.write_text('{}')
            result = subprocess.run([sys.executable, str(SCRIPT), '--plan', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1); self.assertFalse(result.stdout)
            self.assertEqual(list(Path(tmp).iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
