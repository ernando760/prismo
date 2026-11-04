"""Cálculos independentes, contrato DTCG suportado e preservação das fundações."""
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
SCRIPT = ROOT / 'skills/prismo/scripts/typography.py'
spec = importlib.util.spec_from_file_location('typography', SCRIPT)
t = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(SCRIPT.parent))
spec.loader.exec_module(t)


def plan():
    return json.loads((ROOT / 'tests/fixtures/typography-plan.json').read_text())


class TypographyTests(unittest.TestCase):
    def test_known_modular_values_and_negative_steps(self):
        self.assertEqual(t.modular(16, 1.25, -1, 4), 12.8)
        self.assertEqual(t.modular(16, 1.25, 0, 4), 16)
        self.assertEqual(t.modular(16, 1.25, 2, 4), 25)
        self.assertEqual(t.modular(16, 1.5, -2, 6), 7.111111)

    def test_explicit_rounding_half_up(self):
        self.assertEqual(t.modular(1.005, 1.25, 0, 2), 1.01)
        self.assertEqual(t.modular(1.004, 1.25, 0, 2), 1)

    def test_sizes_height_and_tracking_known_values(self):
        rows = t.build(plan())['styles']
        for row, expected in zip(rows, [(25, 30, -.5), (16, 24, 0), (12.8, 16, .512)]):
            self.assertEqual(row['resolved']['fontSize']['value'], expected[0])
            self.assertEqual(row['lineHeightDimension']['value'], expected[1])
            self.assertEqual(row['resolved']['letterSpacing']['value'], expected[2])
            self.assertEqual(row['flutter']['fontSize'], expected[0])
            self.assertEqual(row['flutter']['letterSpacing'], expected[2])

    def test_rem_and_flutter_projection_require_explicit_root(self):
        p = plan(); p['base'] = {'value': 1, 'unit': 'rem'}; p['root_px'] = 16
        rows = t.build(p)['styles']
        self.assertEqual(rows[0]['resolved']['fontSize'], {'value': 1.5625, 'unit': 'rem'})
        self.assertEqual(rows[0]['flutter']['fontSize'], 25)
        # -0.03125rem é exportado como -0.0313rem, antes de converter.
        self.assertEqual(rows[0]['flutter']['letterSpacing'], -.5008)
        p['root_px'] = 20
        self.assertEqual(t.build(p)['styles'][0]['flutter']['fontSize'], 31.25)
        p['root_px'] = None
        with self.assertRaises(ValueError):
            t.build(p)

    def test_invariant_dtcg_composites_and_typed_aliases(self):
        result = t.build(plan())
        tokens = t.index(result['tokens'])
        for style in ('heading', 'body', 'label'):
            kind, value = tokens[f'semantic.typography.{style}']
            self.assertEqual(kind, 'typography')
            self.assertEqual(set(value), set(t.FIELDS))
            for field, expected_type in t.FIELDS.items():
                self.assertTrue(t.alias(value[field]))
                resolved = t.resolved(tokens, value[field][1:-1], expected_type)
                if field in ('fontSize', 'letterSpacing'):
                    self.assertEqual(set(resolved), {'value', 'unit'})
                    self.assertIn(resolved['unit'], ('px', 'rem'))
            self.assertIsInstance(t.resolved(tokens, f'semantic.typography.{style}', 'typography')['lineHeight'], (int, float))

    def test_preserves_actual_colors_output(self):
        run = subprocess.run([sys.executable, str(ROOT / 'skills/prismo/scripts/colors.py'),
                              'palette', '--plan', str(ROOT / 'tests/fixtures/colors-plan.json'), '--full'],
                             capture_output=True, text=True, check=True)
        existing = json.loads(run.stdout)['tokens']
        before = copy.deepcopy(existing)
        result = t.build(plan(), existing)
        for layer in ('primitive', 'semantic'):
            for name, value in before[layer].items():
                self.assertEqual(result['tokens'][layer][name], value)
        self.assertEqual(existing, before)

    def test_existing_literals_and_inherited_types_reused(self):
        existing = {'fonts': {'$type': 'fontFamily', 'sans': {'$value': ['Example Sans', 'sans-serif']}},
                    'size': {'$type': 'dimension', '$value': {'value': 16, 'unit': 'px'}}}
        result = t.build(plan(), existing)
        tokens = t.index(result['tokens'])
        self.assertEqual(tokens['primitive.typography.family.sans'][1], '{fonts.sans}')
        self.assertEqual(tokens['primitive.typography.size.base'][1], '{size}')

    def test_explicit_family_weight_and_composite_alias_reuse(self):
        existing = t.build(plan())['tokens']
        p = plan(); p['families'] = {}; p['weights'] = {}; p['steps'] = {}
        p['styles'] = {'heading': '{semantic.typography.heading}'}
        self.assertEqual(t.build(p, existing)['tokens'], existing)
        p = plan()
        p['families']['sans'] = '{primitive.typography.family.sans}'
        p['weights']['regular'] = '{primitive.typography.weight.regular}'
        self.assertEqual(t.build(p, existing)['tokens'], existing)

    def test_determinism_idempotency_and_input_immutable(self):
        p = plan(); before = copy.deepcopy(p)
        first = t.build(p)
        self.assertEqual(first, t.build(p))
        self.assertEqual(t.build(p, first['tokens'])['tokens'], first['tokens'])
        self.assertEqual(p, before)

    def test_collision_does_not_mutate_existing(self):
        existing = t.build(plan())['tokens']; before = copy.deepcopy(existing)
        p = plan(); p['ratio'] = 1.5
        with self.assertRaisesRegex(ValueError, 'Colisão'):
            t.build(p, existing)
        self.assertEqual(existing, before)

    def test_missing_wrong_type_and_circular_aliases(self):
        for existing in ({'font': {'$type': 'color', '$value': '#ffffff'}},
                         {'font': {'$type': 'fontFamily', '$value': '{font}'}}, {}):
            p = plan(); p['families']['sans'] = '{font}'
            with self.assertRaises(ValueError):
                t.build(p, existing)
        p = plan(); p['styles']['body']['step'] = 'missing'
        with self.assertRaises(ValueError):
            t.build(p)

    def test_invalid_scale_units_precision_and_exponents(self):
        for field, value in [('ratio', 1), ('ratio', 0), ('ratio', math.nan), ('ratio', True),
                             ('precision', 9), ('precision', False), ('root_px', 0)]:
            p = plan(); p[field] = value
            with self.assertRaises(ValueError):
                t.build(p)
        for unit in ('em', 'sp', 'dp', '%'):
            p = plan(); p['base']['unit'] = unit
            with self.assertRaises(ValueError):
                t.build(p)
        for step in (1.5, True, 101):
            p = plan(); p['steps']['small'] = step
            with self.assertRaises(ValueError):
                t.build(p)

    def test_invalid_families_weights_and_styles(self):
        for field, value in [('families', {'sans': []}), ('weights', {'regular': 0}),
                             ('weights', {'bold': 1001}), ('styles', {})]:
            p = plan(); p[field] = value
            with self.assertRaises(ValueError):
                t.build(p)
        for field, value in [('line_height', 0), ('line_height', math.inf), ('letter_spacing_em', True)]:
            p = plan(); p['styles']['body'][field] = value
            with self.assertRaises(ValueError):
                t.build(p)

    def test_weight_names_and_rounding_to_zero(self):
        p = plan(); p['weights']['bold'] = 'bold'
        self.assertEqual(t.build(p)['styles'][0]['resolved']['fontWeight'], 700)
        p = plan(); p['base']['value'] = .000001; p['precision'] = 2
        with self.assertRaises(ValueError):
            t.build(p)

    def test_unsupported_refs_and_invalid_composite(self):
        with self.assertRaises(ValueError):
            t.build(plan(), {'legacy': {'$extends': '{base}'}})
        p = plan(); p['styles'] = {'body': '{old.body}'}
        existing = {'old': {'body': {'$type': 'typography', '$value': {'fontSize': {'value': 16, 'unit': 'px'}}}}}
        with self.assertRaises(ValueError):
            t.build(p, existing)

    def test_cli_preview_read_only_and_error_exit(self):
        with tempfile.TemporaryDirectory(prefix='prismo typography ') as tmp:
            path = Path(tmp) / 'plan.json'; path.write_text(json.dumps(plan()))
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), '--plan', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'preview')
            self.assertEqual(list(Path(tmp).iterdir()), [path])
            self.assertEqual(path.read_bytes(), before)
            path.write_text('{}')
            result = subprocess.run([sys.executable, str(SCRIPT), '--plan', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(result.stdout)


if __name__ == '__main__':
    unittest.main()
