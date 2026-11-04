"""Vetores conhecidos, limites WCAG e integração do preview Colors."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/prismo/scripts/colors.py'
spec = importlib.util.spec_from_file_location('colors', SCRIPT)
c = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(SCRIPT.parent))
spec.loader.exec_module(c)


def plan():
    return {'palettes': {'neutral': {'seed': '#808080', 'steps': {'0': 1, '500': .6, '1000': 0}}},
            'themes': {'light': {'text': 'primitive.neutral.1000', 'surface': 'primitive.neutral.0'},
                       'dark': {'text': 'primitive.neutral.0', 'surface': 'primitive.neutral.1000'}},
            'pairs': [{'foreground': f'semantic.{theme}.text', 'background': f'semantic.{theme}.surface', 'usage': 'normal_text'} for theme in ('light', 'dark')]}


class ColorTests(unittest.TestCase):
    def test_known_red_oklch(self):
        light, chroma, hue = c.to_oklch('#ff0000')
        self.assertAlmostEqual(light, .62795536, places=7)
        self.assertAlmostEqual(chroma, .25768331, places=7)
        self.assertAlmostEqual(hue, 29.233885, places=5)

    def test_round_trip_srgb_grid(self):
        for r in (0, .1, .5, 1):
            for g in (0, .2, .7, 1):
                for b in (0, .3, .8, 1):
                    result = c.from_oklch(*c.to_oklch([r, g, b]))
                    for actual, expected in zip(result, (r, g, b)):
                        self.assertAlmostEqual(actual, expected, delta=2e-6)

    def test_out_of_gamut_reduces_chroma_only(self):
        value, lch, mapped = c.gamut_map(.6, .5, 30)
        self.assertTrue(mapped)
        self.assertEqual((lch[0], lch[2]), (.6, 30))
        self.assertLess(lch[1], .5)
        self.assertTrue(all(0 <= v <= 1 for v in value))
        self.assertAlmostEqual(c.to_oklch(value)[0], .6, places=7)
        self.assertTrue(any(v < 0 or v > 1 for v in c.from_oklch(.6, .5, 30)))

    def test_gamut_sweep(self):
        for light in (.01, .1, .5, .9, .99):
            for hue in range(0, 360, 15):
                value, lch, _ = c.gamut_map(light, .4, hue)
                self.assertTrue(all(0 <= channel <= 1 for channel in value))
                self.assertEqual(lch[0], light)
                self.assertEqual(lch[2], hue)
                self.assertLessEqual(lch[1], .4)

    def test_in_gamut_preserved(self):
        _, lch, mapped = c.gamut_map(.5, .05, 90)
        self.assertFalse(mapped)
        self.assertEqual(lch, (.5, .05, 90))

    def test_endpoints_and_neutral(self):
        self.assertEqual(c.gamut_map(0, .4, 20)[0], (0, 0, 0))
        self.assertEqual(c.gamut_map(1, .4, 20)[0], (1, 1, 1))
        self.assertEqual(c.to_oklch('#808080')[1:], (0, 0))

    def test_contrast_reference_values(self):
        self.assertEqual(c.contrast('#000000', '#ffffff'), 21)
        self.assertEqual(c.contrast('#ff0000', '#ff0000'), 1)
        self.assertAlmostEqual(c.contrast('#ff0000', '#ffffff'), 3.9984767707539985, places=12)
        self.assertAlmostEqual(c.contrast('#777777', '#ffffff'), 4.478089453577214, places=12)
        self.assertEqual(c.contrast('#ffffff', '#777777'), c.contrast('#777777', '#ffffff'))

    def test_transfer_function_breakpoint(self):
        self.assertAlmostEqual(c.linear(.04045), .04045 / 12.92, places=15)
        self.assertAlmostEqual(c.linear(.04046), ((.04046 + .055) / 1.055)**2.4, places=15)

    def test_wcag_thresholds_without_rounding(self):
        self.assertFalse(c.evaluate(4.499999, 'normal_text')['AA'])
        self.assertTrue(c.evaluate(4.5, 'normal_text')['AA'])
        self.assertFalse(c.evaluate(6.999999, 'normal_text')['AAA'])
        self.assertTrue(c.evaluate(7, 'normal_text')['AAA'])
        self.assertTrue(c.evaluate(3, 'large_text')['AA'])
        self.assertTrue(c.evaluate(4.5, 'large_text')['AAA'])
        self.assertTrue(c.evaluate(3, 'non_text')['AA'])
        self.assertIsNone(c.evaluate(21, 'non_text')['AAA'])

    def test_invalid_inputs_and_alpha_rejected(self):
        for value in ('red', '#fff', '#ffffff80', [-.1, 0, 0], [math.nan, 0, 0], [True, 0, 0]):
            with self.assertRaises(ValueError):
                c.rgb(value)
        with self.assertRaises(ValueError):
            c.gamut_map(.5, math.inf, 20)

    def test_dtcg_aliases_both_themes_and_determinism(self):
        p = plan()
        before = copy.deepcopy(p)
        first = c.build(p)
        self.assertEqual(first, c.build(p))
        self.assertEqual(p, before)
        tokens = c.flatten(first['tokens'])
        self.assertEqual(tokens['semantic.dark.text'][0]['$value'], '{primitive.neutral.0}')
        self.assertEqual(first['contrast'][0]['ratio'], 21)
        self.assertEqual(first['contrast'][1]['ratio'], 21)
        for swatch in first['swatches']:
            exported = c.resolve(tokens, swatch['token'])
            self.assertEqual(c.hex_color(exported), swatch['hex'])
        # Reexecutar sobre o documento gerado preserva os valores e não duplica tokens.
        self.assertEqual(c.build(p, first['tokens'])['tokens'], first['tokens'])

    def test_existing_color_reused_and_unrelated_tokens_preserved(self):
        existing = {'brand': {'white': {'$type': 'color', '$value': {'colorSpace': 'srgb', 'components': [1, 1, 1]}}},
                    'size': {'$type': 'dimension', '$value': {'value': 8, 'unit': 'px'}}}
        before = copy.deepcopy(existing)
        result = c.build(plan(), existing)
        self.assertEqual(result['tokens']['primitive']['neutral']['0']['$value'], '{brand.white}')
        self.assertEqual(result['tokens']['size'], existing['size'])
        self.assertEqual(existing, before)

    def test_existing_only_no_new_palette(self):
        existing = c.build(plan())['tokens']
        p = plan(); p['palettes'] = {}; p['themes'] = {'light': {}, 'dark': {}}
        self.assertEqual(c.build(p, existing)['tokens'], existing)

    def test_collisions_missing_tokens_cycles_and_transparency(self):
        p = plan()
        for existing in [
            {'primitive': {'neutral': {'0': {'$type': 'color', '$value': {'colorSpace': 'srgb', 'components': [0, 0, 0]}}}}},
            {'primitive': {'$type': 'string', '$value': 'preservar'}}
        ]:
            with self.assertRaises(ValueError):
                c.build(p, existing)
        p['themes']['light']['text'] = 'missing'
        with self.assertRaises(ValueError):
            c.build(p)
        for tree in [{'a': {'$type': 'color', '$value': '{a}'}},
                     {'a': {'$type': 'color', '$value': {'colorSpace': 'srgb', 'components': [1, 0, 0], 'alpha': .5}}}]:
            with self.assertRaises(ValueError):
                c.resolve(c.flatten(tree), 'a')

    def test_cli_preview_is_read_only_and_failure_exit_code(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'plan.json'
            path.write_text(json.dumps(plan()))
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), 'palette', '--plan', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'preview')
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(temp).iterdir()), [path])
        result = subprocess.run([sys.executable, str(SCRIPT), 'contrast', '#777777', '#ffffff', '--fail-on', 'AA'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)['AA'])


if __name__ == '__main__':
    unittest.main()
