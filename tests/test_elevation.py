"""Elevação: parâmetros assinados, alpha, shadow DTCG e preservação."""
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
SCRIPT = ROOT / 'skills/prismo/scripts/elevation.py'
spec = importlib.util.spec_from_file_location('elevation', SCRIPT)
e = importlib.util.module_from_spec(spec)
with patch.object(sys, 'path', [str(SCRIPT.parent), *sys.path]):
    spec.loader.exec_module(e)


def plan():
    return json.loads((ROOT / 'tests/fixtures/elevation-plan.json').read_text())


def shadow_layer():
    return {'color': {'colorSpace': 'srgb', 'components': [0, 0, 0], 'alpha': .5},
            **{key: {'value': (4 if key == 'blur' else 0), 'unit': 'px'} for key in e.DIMENSIONS}}


class ElevationTests(unittest.TestCase):
    def test_hierarchical_semantics_dotted_and_nested_are_equivalent(self):
        dotted = plan()
        dotted['semantics'] = {'surface.' + key: value for key, value in dotted['semantics'].items()}
        nested = plan(); nested['semantics'] = {'surface': nested['semantics']}
        before = copy.deepcopy(nested)
        result = e.build(nested)
        self.assertEqual(result, e.build(dotted))
        self.assertEqual(nested, before)
        self.assertEqual(e.build(nested, result['tokens'])['tokens'], result['tokens'])
        old = e.build(plan())
        for flat, hierarchical in zip(old['usages'], result['usages']):
            self.assertEqual(flat['resolved'], hierarchical['resolved'])
            self.assertEqual(flat['web'], hierarchical['web'])
            self.assertEqual(flat['flutter'], hierarchical['flutter'])
        self.assertIn('semantic.elevation.surface.card', e.index(result['tokens']))

    def test_hierarchical_names_and_collisions_are_rejected_without_mutation(self):
        reference = '{primitive.elevation.shadow.low}'
        for semantics in ({'surface..card': reference}, {'.card': reference}, {'card.': reference},
                          {'surface.$bad': reference}, {'surface': {}}, {'surface': {'card': 1}},
                          {'surface.card': reference, 'surface': {'card': reference}},
                          {'surface': reference, 'surface.card': reference}):
            p = plan(); p['semantics'].update(semantics)
            before = copy.deepcopy(p)
            with self.assertRaises(ValueError): e.build(p)
            self.assertEqual(p, before)
        p = plan(); p['semantics']['surface.card'] = reference
        existing = {'semantic': {'elevation': {'surface': {'$type': 'shadow', '$value': []}}}}
        before = copy.deepcopy(existing)
        with self.assertRaises(ValueError): e.build(p, existing)
        self.assertEqual(existing, before)

    def test_known_values_and_scale(self):
        levels = e.build(plan())['levels']
        for row, expected in zip(levels[1:], [(1, 2, 0, .12), (2, 4, -.5, .16), (6, 12, 0, .2)]):
            layer = row['resolved'][0]
            self.assertEqual((layer['offsetY']['value'], layer['blur']['value'], layer['spread']['value'], layer['color']['alpha']), expected)
        self.assertEqual(levels[3]['flutter']['boxShadow'][0]['blurRadius'], 12)

    def test_negative_offset_and_spread_valid_blur_not_negative(self):
        p = plan(); layer = p['levels']['low'][0]
        layer.update(offsetX=-2, offsetY=-1, spread=-1.5)
        value = e.build(p)['levels'][1]['resolved'][0]
        self.assertEqual([value[k]['value'] for k in ('offsetX', 'offsetY', 'spread')], [-2, -1, -1.5])
        layer['blur'] = -.01
        with self.assertRaises(ValueError):
            e.build(p)

    def test_signed_rounding_modes_and_decimal_tie(self):
        self.assertEqual(e.calculate(-1.25, 1, {'mode': 'half_up', 'increment': .5}), -1.5)
        self.assertEqual(e.calculate(-1.25, 1, {'mode': 'floor', 'increment': .5}), -1.5)
        self.assertEqual(e.calculate(-1.25, 1, {'mode': 'ceil', 'increment': .5}), -1)
        self.assertEqual(e.calculate(.1, 3, {'mode': 'half_up', 'increment': .1}), .3)

    def test_alpha_product_and_precision(self):
        self.assertEqual(e.alpha_product(.5, .24, 4), .12)
        self.assertEqual(e.alpha_product(.5, .3333, 4), .1667)
        self.assertEqual(e.alpha_product(0, 1, 4), 0)
        self.assertEqual(e.alpha_product(1, 1, 4), 1)

    def test_none_and_arbitrary_level_names(self):
        p = plan(); p['levels']['custom'] = p['levels'].pop('low')
        p['semantics']['card'] = '{primitive.elevation.shadow.custom}'
        levels = e.build(p)['levels']
        self.assertEqual(levels[0]['resolved'], [])
        self.assertEqual(levels[0]['web']['boxShadow'], 'none')
        self.assertEqual(levels[0]['flutter']['boxShadow'], [])
        p['levels']['none'] = p['levels']['custom']
        with self.assertRaises(ValueError):
            e.build(p)

    def test_typed_shadow_color_and_semantic_aliases(self):
        result = e.build(plan()); tokens = e.index(result['tokens'])
        self.assertEqual(tokens['primitive.elevation.shadow.low'][0], 'shadow')
        layer = tokens['primitive.elevation.shadow.low'][1][0]
        self.assertEqual(set(layer), {*e.SHADOW_FIELDS, 'inset'})
        self.assertTrue(e.alias(layer['color']))
        for key in e.DIMENSIONS:
            self.assertEqual(set(layer[key]), {'value', 'unit'})
        self.assertEqual(tokens['semantic.elevation.card'], ('shadow', '{primitive.elevation.shadow.low}'))

    def test_existing_color_alpha_multiplied_without_mutation(self):
        existing = {'ink': {'$type': 'color', '$value': {'colorSpace': 'srgb', 'components': [0, 0, 0], 'alpha': .5}, '$description': 'keep'}}
        before = copy.deepcopy(existing)
        p = plan(); p['levels']['low'][0].update(color='{ink}', opacity=.24)
        result = e.build(p, existing)
        self.assertEqual(result['levels'][1]['resolved'][0]['color']['alpha'], .12)
        self.assertEqual(result['tokens']['ink'], before['ink']); self.assertEqual(existing, before)
        p['levels']['low'][0]['opacity'] = 1
        result = e.build(p, existing)
        self.assertEqual(e.index(result['tokens'])['primitive.elevation.color.low.layer0'][1], '{ink}')

    def test_duplicate_shadows_and_colors_reuse_aliases(self):
        p = plan(); p['levels']['medium'] = copy.deepcopy(p['levels']['low'])
        result = e.build(p); tokens = e.index(result['tokens'])
        self.assertEqual(tokens['primitive.elevation.shadow.medium'][1], '{primitive.elevation.shadow.low}')
        self.assertNotIn('primitive.elevation.color.medium.layer0', tokens)
        self.assertNotIn('medium', result['tokens']['primitive']['elevation']['color'])

    def test_multiple_layers_reverse_flutter_order(self):
        p = plan(); p['levels']['low'].append(copy.deepcopy(p['levels']['medium'][0]))
        row = e.build(p)['levels'][1]
        self.assertEqual([l['source_layer'] for l in row['flutter']['boxShadow']], [1, 0])
        self.assertEqual([l['offsetY']['value'] for l in row['resolved']], [1, 2])
        self.assertTrue(row['web']['boxShadow'].startswith('0.0px 1.0px'))

    def test_inset_blocks_flutter_projection_without_silent_drop(self):
        p = plan(); p['levels']['low'][0]['inset'] = True
        row = e.build(p)['levels'][1]
        self.assertTrue(row['web']['boxShadow'].startswith('inset '))
        self.assertFalse(row['flutter']['supported']); self.assertIsNone(row['flutter']['boxShadow'])
        self.assertTrue(row['warnings'])

    def test_sigma_diagnostic_and_no_false_css_equivalence(self):
        self.assertEqual(e.flutter_sigma(0), 0)
        self.assertEqual(e.flutter_sigma(4), 2.8094)
        self.assertNotEqual(e.flutter_sigma(4), 4 / 2)

    def test_rem_conversion_and_root_required_for_existing(self):
        p = plan(); p['unit'] = 'rem'; p['root_px'] = 16
        row = e.build(p)['levels'][1]
        self.assertEqual(row['flutter']['boxShadow'][0]['blurRadius'], 32)
        self.assertIn('2.0rem', row['web']['boxShadow'])
        p['root_px'] = None
        with self.assertRaises(ValueError):
            e.build(p)
        existing = {'x': {'$type': 'shadow', '$value': shadow_layer()}}
        existing['x']['$value']['blur']['unit'] = 'rem'
        p = plan(); p['levels'] = {}; p['semantics'] = {'card': '{x}'}
        with self.assertRaises(ValueError):
            e.build(p, existing)

    def test_existing_shadow_field_and_single_layer_aliases(self):
        layer = shadow_layer(); layer['blur'] = '{softness}'
        existing = {'base': {'$type': 'shadow', '$value': layer}, 'softness': {'$type': 'dimension', '$value': {'value': 4, 'unit': 'px'}}}
        p = plan(); p['levels']['low'] = ['{base}']
        result = e.build(p, existing)
        self.assertEqual(result['levels'][1]['resolved'][0]['blur']['value'], 4)
        p['levels']['low'] = '{base}'
        self.assertEqual(e.build(p, existing)['levels'][1]['resolved']['blur']['value'], 4)
        p['levels']['low'] = ['{multi}']
        existing['multi'] = {'$type': 'shadow', '$value': [shadow_layer()]}
        with self.assertRaises(ValueError):
            e.build(p, existing)

    def test_idempotency_reuse_only_and_inputs_immutable(self):
        p = plan(); before = copy.deepcopy(p)
        first = e.build(p)
        self.assertEqual(e.build(p), first); self.assertEqual(p, before)
        existing = first['tokens']; old = copy.deepcopy(existing)
        self.assertEqual(e.build(p, existing)['tokens'], existing)
        p['levels'] = {}
        self.assertEqual(e.build(p, existing)['tokens'], existing)
        self.assertEqual(existing, old)

    def test_collision_cycles_missing_and_wrong_types(self):
        existing = e.build(plan())['tokens']; before = copy.deepcopy(existing)
        p = plan(); p['levels']['low'][0]['blur'] = 8
        with self.assertRaises(ValueError):
            e.build(p, existing)
        self.assertEqual(existing, before)
        for tree in ({}, {'x': {'$type': 'number', '$value': 1}}, {'x': {'$type': 'shadow', '$value': '{x}'}}):
            p = plan(); p['levels']['low'] = '{x}'
            with self.assertRaises(ValueError):
                e.build(p, tree)

    def test_invalid_opacity_alpha_and_nonfinite_values(self):
        for key in ('opacity', 'blur', 'scale', 'offsetX', 'spread'):
            for value in (math.nan, math.inf, True):
                p = plan(); p['levels']['low'][0][key] = value
                with self.assertRaises(ValueError):
                    e.build(p)
        for value in (-.01, 1.01):
            p = plan(); p['levels']['low'][0]['opacity'] = value
            with self.assertRaises(ValueError):
                e.build(p)
            p = plan(); p['levels']['low'][0]['color'] = {'colorSpace': 'srgb', 'components': [0, 0, 0], 'alpha': value}
            with self.assertRaises(ValueError):
                e.build(p)

    def test_invalid_configuration_and_unused_levels(self):
        for field, value in [('unit', 'dp'), ('root_px', 0), ('opacity_precision', True), ('opacity_precision', 9),
                             ('semantics', {}), ('rounding', {'mode': 'floor', 'increment': 0})]:
            p = plan(); p[field] = value
            with self.assertRaises(ValueError):
                e.build(p)
        p = plan(); p['levels']['unused'] = []
        with self.assertRaisesRegex(ValueError, 'sem finalidade'):
            e.build(p)
        p = plan(); p['levels']['low'][0]['inset'] = 1
        with self.assertRaises(ValueError):
            e.build(p)

    def test_unsupported_color_legacy_hex_and_invisible_warning(self):
        p = plan(); p['levels']['low'][0]['color'] = '{old}'
        with self.assertRaises(ValueError):
            e.build(p, {'old': {'$type': 'color', '$value': '#000000'}})
        p['levels']['low'][0]['color'] = {'colorSpace': 'display-p3', 'components': [0, 0, 0]}
        with self.assertRaises(ValueError):
            e.build(p)
        p = plan(); p['levels']['low'][0]['opacity'] = 0
        self.assertTrue(e.build(p)['levels'][1]['warnings'])

    def test_cli_preserves_four_foundations_and_decisions(self):
        def run(script, args):
            return json.loads(subprocess.run([sys.executable, str(SCRIPT.parent / script), *args, '--full'], capture_output=True, text=True, check=True).stdout)
        with tempfile.TemporaryDirectory(prefix='prismo elevation ') as tmp:
            directory = Path(tmp); token_file = directory / 'tokens.json'
            tokens = run('colors.py', ['palette', '--plan', str(ROOT / 'tests/fixtures/colors-plan.json')])['tokens']
            for foundation in ('typography', 'spacing', 'borders'):
                token_file.write_text(json.dumps(tokens))
                tokens = run(foundation + '.py', ['--plan', str(ROOT / 'tests/fixtures' / (foundation + '-plan.json')), '--existing', str(token_file)])['tokens']
            token_file.write_text(json.dumps(tokens))
            decisions = directory / 'decisions.json'; decisions.write_text(json.dumps({'foundations': {k: {'approved': True} for k in ('colors', 'typography', 'spacing', 'borders')}}))
            before = {p.name: p.read_bytes() for p in directory.iterdir()}
            result = run('elevation.py', ['--plan', str(ROOT / 'tests/fixtures/elevation-plan.json'), '--existing', str(token_file)])
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
