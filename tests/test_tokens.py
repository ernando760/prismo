"""Mudanças DTCG, validação e impacto em cópias temporárias; não avalia diálogo do agente."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'skills/prismo/scripts/tokens.py'
spec = importlib.util.spec_from_file_location('prismo_tokens', SCRIPT)
t = importlib.util.module_from_spec(spec)
with patch.object(sys, 'path', [str(SCRIPT.parent), *sys.path]):
    spec.loader.exec_module(t)


def dim(value):
    return {'value': value, 'unit': 'px'}


def token(kind, value):
    return {'$type': kind, '$value': value}


def sources():
    return {'ds/base.json': {'$description': 'Fundação preservada', 'primitive': {
        'space': {'$type': 'dimension', '$description': 'Grupo', 'base': {'$value': dim(4), '$description': 'Base', '$extensions': {'org.test': {'keep': True}}}},
        'ink': token('color', {'colorSpace': 'srgb', 'components': [0, 0, 0], 'alpha': 1})}},
        'ds/semantic.json': {'semantic': {'gap': token('dimension', '{primitive.space.base}'),
                                        'card': token('dimension', '{semantic.gap}')},
                             'component': {'button': {'gap': token('dimension', '{semantic.card}')}}}}


def plan(*changes, bindings=None):
    return {'changes': list(changes), 'bindings': bindings or {}}


class TokensTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='prismo tokens ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = sources()
        for filename, tree in self.sources.items():
            self.write(filename, tree)
        self.write('design-system/decisions.json', {'decisions': {'paths': {'tokens': 'ds/base.json'}, 'keep': ['colors', 'typography', 'spacing', 'borders', 'elevation']}})

    def write(self, filename, content):
        path = self.root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content) if isinstance(content, dict) else content)
        return path

    def run_cli(self, mode, *args):
        return subprocess.run([sys.executable, str(SCRIPT), mode, str(self.root), *args], cwd=self.root, capture_output=True, text=True)

    def test_create_primitive_semantic_and_component_tokens_without_namespace_rules(self):
        result = t.preview(self.sources, plan(
            {'op': 'create', 'file': 'ds/base.json', 'path': 'primitive.space.large', 'token': {'$value': dim(16)}},
            {'op': 'create', 'file': 'ds/semantic.json', 'path': 'semantic.layout', 'token': token('dimension', '{primitive.space.large}')},
            {'op': 'create', 'file': 'ds/semantic.json', 'path': 'component.panel.padding', 'token': token('dimension', '{semantic.layout}')}))
        self.assertTrue(result['approval_required'])
        self.assertEqual(len(result['changes']), 3)
        self.assertEqual(result['files']['ds/base.json']['primitive']['space']['large']['$value'], dim(16))

    def test_edit_preserves_metadata_and_finds_transitive_dependents(self):
        result = t.preview(self.sources, plan({'op': 'edit', 'path': 'primitive.space.base', 'patch': {'$value': dim(8)}}))
        self.assertEqual(set(result['affected_tokens']), {'primitive.space.base', 'semantic.gap', 'semantic.card', 'component.button.gap'})
        self.assertEqual(set(result['resolved_value_changes']), set(result['affected_tokens']))
        item = result['files']['ds/base.json']['primitive']['space']['base']
        self.assertEqual(item['$extensions'], {'org.test': {'keep': True}})
        self.assertEqual(item['$description'], 'Base')
        self.assertEqual(self.sources, sources())

    def test_rename_rewrites_cross_file_aliases_not_descriptions(self):
        self.sources['ds/semantic.json']['$description'] = '{primitive.space.base}'
        result = t.preview(self.sources, plan({'op': 'move', 'path': 'primitive.space.base', 'file': 'ds/base.json', 'to': 'primitive.space.unit'}))
        after = result['files']
        self.assertEqual(after['ds/semantic.json']['semantic']['gap']['$value'], '{primitive.space.unit}')
        self.assertEqual(after['ds/semantic.json']['$description'], '{primitive.space.base}')
        self.assertEqual(after['ds/base.json']['primitive']['space']['unit']['$type'], 'dimension')
        self.assertIn('component.button.gap', result['affected_tokens'])
        self.assertNotIn('component.button.gap', result['resolved_value_changes'])

    def test_reorganize_between_sources_preserves_inherited_type(self):
        result = t.preview(self.sources, plan({'op': 'move', 'path': 'primitive.space.base', 'file': 'ds/semantic.json', 'to': 'base.space'}))
        self.assertEqual(result['files']['ds/semantic.json']['base']['space']['$type'], 'dimension')
        self.assertEqual(result['files']['ds/base.json']['primitive']['space']['$description'], 'Grupo')
        t.validate(result['files'])

    def test_move_same_path_between_files(self):
        result = t.preview(self.sources, plan({'op': 'move', 'path': 'primitive.ink', 'file': 'ds/semantic.json', 'to': 'primitive.ink'}))
        self.assertEqual(result['changes'][0]['before_file'], 'ds/base.json')
        self.assertEqual(result['changes'][0]['after_file'], 'ds/semantic.json')

    def test_remove_with_dependents_rejected_then_explicit_removal_set_validates(self):
        with self.assertRaisesRegex(ValueError, 'inexistente'):
            t.preview(self.sources, plan({'op': 'remove', 'path': 'semantic.gap'}))
        result = t.preview(self.sources, plan(*({'op': 'remove', 'path': p} for p in ('semantic.gap', 'semantic.card', 'component.button.gap'))))
        self.assertEqual(len(result['changes']), 3)
        self.assertEqual(result['files']['ds/semantic.json']['semantic'], {})

    def test_collisions_and_unknown_paths_never_overwrite(self):
        for change in (
            {'op': 'create', 'file': 'ds/base.json', 'path': 'primitive.space', 'token': token('number', 1)},
            {'op': 'move', 'path': 'primitive.ink', 'file': 'ds/base.json', 'to': 'primitive.space.base'},
            {'op': 'edit', 'path': 'unknown', 'patch': {'$value': 1}},
            {'op': 'remove', 'path': 'unknown'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                t.preview(self.sources, plan(change))
        self.assertEqual(self.sources, sources())

    def test_missing_alias_cycle_and_type_mismatch(self):
        for value, kind in (('{missing}', 'number'), ('{x}', 'number'), ('{primitive.ink}', 'dimension')):
            bad = copy.deepcopy(self.sources); bad['ds/base.json']['x'] = token(kind, value)
            with self.subTest(value=value), self.assertRaises(ValueError): t.validate(bad)
        bad = {'a.json': {'a': token('number', '{b}'), 'b': token('number', '{a}')}}
        with self.assertRaisesRegex(ValueError, 'Ciclo'): t.validate(bad)

    def test_repair_invalid_baseline_without_claiming_resolved_comparison(self):
        broken = {'a.json': {'x': token('dimension', '{missing}'), 'y': token('dimension', '{x}')}}
        result = t.preview(broken, plan({'op': 'edit', 'path': 'x', 'patch': {'$value': dim(4)}}))
        self.assertFalse(result['baseline_validation']['passed'])
        self.assertIn('inexistente', result['baseline_validation']['error'])
        self.assertIsNone(result['resolved_value_changes'])
        self.assertEqual(result['affected_tokens'], ['x', 'y'])
        t.validate(result['files'])

    def test_repair_cannot_leave_other_invalid_tokens_and_cycles_can_be_repaired(self):
        broken = {'a.json': {'x': token('number', '{y}'), 'y': token('number', '{x}')}}
        result = t.preview(broken, plan({'op': 'edit', 'path': 'y', 'patch': {'$value': 1}}))
        self.assertFalse(result['baseline_validation']['passed'])
        broken['a.json']['bad'] = token('number', True)
        with self.assertRaises(ValueError):
            t.preview(broken, plan({'op': 'edit', 'path': 'y', 'patch': {'$value': 1}}))

    def test_duplicate_json_keys_and_duplicate_paths_across_sources(self):
        path = self.write('duplicate.json', '{"x":{"$type":"number","$value":1,"$value":2}}')
        with self.assertRaisesRegex(ValueError, 'Chave JSON duplicada'): t.read(path)
        with self.assertRaisesRegex(ValueError, 'duplicado entre fontes'):
            t.validate({'a.json': {'x': token('number', 1)}, 'b.json': {'x': token('number', 2)}})
        with self.assertRaisesRegex(ValueError, 'Token usado como grupo'):
            t.validate({'a.json': {'x': token('number', 1)}, 'b.json': {'x': {'y': token('number', 2)}}})

    def test_equal_values_are_candidates_not_automatic_merges(self):
        source = {'a.json': {'x': token('number', 4), 'y': token('number', 4), 'alias': token('number', '{x}')}}
        result = t.preview(source, plan())
        self.assertEqual(result['equivalent_value_candidates'], [['x', 'y']])
        self.assertEqual(result['files'], source)
        self.assertEqual(result['changes'], [])

    def test_root_tokens_and_inherited_types(self):
        source = {'a.json': {'space': {'$type': 'dimension', '$root': {'$value': dim(4)}, 'alias': {'$value': '{space.$root}'}}}}
        t.validate(source)
        result = t.preview(source, plan({'op': 'move', 'path': 'space.$root', 'file': 'a.json', 'to': 'size.base'}))
        self.assertEqual(result['files']['a.json']['space']['alias']['$value'], '{size.base}')

    def test_supported_scalar_and_composite_types(self):
        source = {'a.json': {'ink': token('color', {'colorSpace': 'srgb', 'components': [0, .25, 1], 'alpha': .5}),
                  'px': token('dimension', dim(1)), 'family': token('fontFamily', ['Example', 'sans-serif']),
                  'weight': token('fontWeight', 'bold'), 'factor': token('number', 1.5),
                  'time': token('duration', {'value': 100, 'unit': 'ms'}), 'ease': token('cubicBezier', [.1, -1, .9, 2]),
                  'stroke': token('strokeStyle', {'dashArray': ['{px}'], 'lineCap': 'round'}),
                  'border': token('border', {'color': '{ink}', 'width': '{px}', 'style': '{stroke}'}),
                  'transition': token('transition', {'duration': '{time}', 'delay': {'value': 0, 'unit': 's'}, 'timingFunction': '{ease}'}),
                  'gradient': token('gradient', [{'color': '{ink}', 'position': 0}, {'color': '{ink}', 'position': 1}]),
                  'type': token('typography', {'fontFamily': '{family}', 'fontWeight': '{weight}', 'fontSize': '{px}', 'lineHeight': '{factor}', 'letterSpacing': dim(0)}),
                  'shadow': token('shadow', {'color': '{ink}', 'offsetX': dim(-1), 'offsetY': '{px}', 'blur': '{px}', 'spread': dim(-1)})}}
        tokens, _, _, resolved, _ = t.validate(source)
        self.assertEqual({kind for kind, _ in tokens.values()}, t.TYPES)
        self.assertEqual(resolved['border']['width'], dim(1))
        self.assertEqual(resolved['type']['fontWeight'], 700)

    def test_invalid_values_and_formats_block_validation(self):
        cases = [('number', True), ('number', float('nan')), ('dimension', {'value': 1, 'unit': 'em'}),
                 ('color', '#ffffff'), ('color', {'colorSpace': 'oklch', 'components': [.5, .1, 180]}),
                 ('fontWeight', 1001), ('duration', {'value': -1, 'unit': 'ms'}),
                 ('cubicBezier', [2, 0, 1, 1]), ('strokeStyle', 'invented'),
                 ('border', {}), ('transition', {}), ('gradient', 'red'), ('invented', 1)]
        for kind, value in cases:
            with self.subTest(kind=kind, value=value), self.assertRaises(ValueError):
                t.validate({'a.json': {'x': token(kind, value)}})
        for tree in ({'$extends': '{x}'}, {'x': {'$type': 'color', '$value': {'$ref': '#/y'}}}):
            with self.assertRaises(ValueError): t.validate({'a.json': tree})

    def test_gradient_clamps_resolved_positions_without_changing_the_source(self):
        color = {'colorSpace': 'srgb', 'components': [0, 0, 0]}
        tree = {'a.json': {'gradient': token('gradient', [{'color': color, 'position': 42}])}}
        before = copy.deepcopy(tree)
        result = t.validate(tree)
        self.assertEqual(result[3]['gradient'][0]['position'], 1)
        self.assertEqual(tree, before)
        t.validate({'a.json': {'empty': token('gradient', [])}})

    def test_stroke_and_border_resolve_changed_dash_alias(self):
        source = {'a.json': {'dash': token('dimension', dim(2)), 'ink': token('color', {'colorSpace': 'srgb', 'components': [0, 0, 0]}),
                  'stroke': token('strokeStyle', {'dashArray': ['{dash}'], 'lineCap': 'round'}),
                  'border': token('border', {'color': '{ink}', 'width': dim(1), 'style': '{stroke}'})}}
        before = t.validate(source)[3]
        result = t.preview(source, plan({'op': 'edit', 'path': 'dash', 'patch': {'$value': dim(8)}}))
        after = t.validate(result['files'])[3]
        self.assertEqual(before['stroke']['dashArray'], [dim(2)])
        self.assertEqual(after['border']['style']['dashArray'], [dim(8)])
        self.assertEqual(set(result['resolved_value_changes']), {'dash', 'stroke', 'border'})
        self.assertEqual(result['resolved_value_diffs']['stroke']['before']['dashArray'], [dim(2)])
        self.assertEqual(result['resolved_value_diffs']['stroke']['after']['dashArray'], [dim(8)])

    def test_composite_nested_alias_updates_and_cycles(self):
        self.sources['ds/base.json']['shadow'] = token('shadow', {'color': '{primitive.ink}', 'offsetX': dim(0), 'offsetY': dim(1), 'blur': dim(2), 'spread': dim(0)})
        result = t.preview(self.sources, plan({'op': 'move', 'path': 'primitive.ink', 'file': 'ds/base.json', 'to': 'primitive.black'}))
        self.assertEqual(result['files']['ds/base.json']['shadow']['$value']['color'], '{primitive.black}')
        self.assertIn('shadow', result['affected_tokens'])
        bad = {'a.json': {'x': token('shadow', {'color': '{x}', 'offsetX': dim(0), 'offsetY': dim(1), 'blur': dim(2), 'spread': dim(0)})}}
        with self.assertRaisesRegex(ValueError, 'Ciclo'): t.validate(bad)

    def test_impact_finds_bindings_docs_and_decisions_without_changing_consumers(self):
        self.write('src/Button.tsx', 'const gap = "--ds-gap";')
        self.write('docs/spacing.mdx', 'Use {semantic.card}')
        self.write('lib/tokens.dart', 'const gap = AppTokens.gap;')
        result = t.impact(self.root, self.sources, ['semantic.card', 'component.button.gap'], {'component.button.gap': ['--ds-gap', 'AppTokens.gap']}, None)
        self.assertEqual({item['file'] for item in result['candidates']}, {'src/Button.tsx', 'docs/spacing.mdx', 'lib/tokens.dart'})
        self.assertIn('não prova', result['coverage'])
        self.assertEqual((self.root / 'src/Button.tsx').read_text(), 'const gap = "--ds-gap";')

    def test_impact_scopes_limits_and_skipped_files_are_explicit(self):
        self.write('node_modules/a/x.ts', 'semantic.gap')
        self.write('src/big.ts', 'x' * (1024 * 1024 + 1))
        self.write('src/doc.md', '\n'.join(['semantic.gap'] * 201))
        result = t.impact(self.root, self.sources, ['semantic.gap'], {}, ['src'])
        self.assertTrue(result['truncated'])
        self.assertEqual(len(result['candidates']), 200)
        self.assertEqual(result['skipped_files'], 1)
        self.assertEqual(t.impact(self.root, self.sources, [], {}, None)['files_scanned'], 0)

    def test_unsafe_paths_symlinks_and_unprovided_destination_rejected(self):
        for path in ('../a.json', '/tmp/a.json', 'a\\b.json'):
            with self.assertRaises(ValueError): t.relative(self.root, path)
        (self.root / 'linked').symlink_to(self.root / 'ds', target_is_directory=True)
        with self.assertRaises(ValueError): t.relative(self.root, 'linked/base.json')
        with self.assertRaisesRegex(ValueError, 'fonte fornecida'):
            t.preview(self.sources, plan({'op': 'move', 'path': 'primitive.ink', 'file': 'new.json', 'to': 'ink'}))

    def test_cli_preview_is_read_only_and_validate_runs_against_persisted_candidate(self):
        p = self.write('plan.json', plan({'op': 'edit', 'path': 'primitive.space.base', 'patch': {'$value': dim(8)}}, bindings={'component.button.gap': ['--ds-gap']}))
        self.write('src/Button.css', 'padding: var(--ds-gap);')
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        args = ['--source', 'ds/base.json', '--source', 'ds/semantic.json']
        result = self.run_cli('preview', *args, '--plan', str(p), '--full')
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report['approval_required'])
        self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        # Somente a fixture aplica o candidato, simulando a etapa após aprovação.
        for filename, tree in report['files'].items(): self.write(filename, tree)
        validated = self.run_cli('validate', *args)
        self.assertEqual(validated.returncode, 0, validated.stderr)
        self.assertEqual((self.root / 'design-system/decisions.json').read_bytes(), before['design-system/decisions.json'])
        self.assertEqual((self.root / 'src/Button.css').read_bytes(), before['src/Button.css'])

    def test_cli_decision_source_default_custom_and_errors(self):
        result = self.run_cli('validate')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write('other.json', {'paths': {'tokens': 'ds/base.json'}})
        self.assertEqual(self.run_cli('validate', '--decisions', 'other.json').returncode, 0)
        self.assertEqual(self.run_cli('preview').returncode, 1)
        self.assertEqual(self.run_cli('validate', '--source', 'ds/base.json', '--source', 'ds/base.json').returncode, 1)
        self.write('invalid.json', '{"x": NaN}')
        self.assertEqual(self.run_cli('validate', '--source', 'invalid.json').returncode, 1)

    def test_all_foundations_preserved_in_real_cli_generation_chain(self):
        def generate(script, *args):
            result = subprocess.run([sys.executable, str(SCRIPT.parent / script), *args, '--full'], capture_output=True, text=True, check=True)
            return json.loads(result.stdout)['tokens']
        tree = generate('colors.py', 'palette', '--plan', str(REPO / 'tests/fixtures/colors-plan.json'))
        path = self.write('all.json', tree)
        for foundation in ('typography', 'spacing', 'borders', 'elevation'):
            tree = generate(foundation + '.py', '--plan', str(REPO / 'tests/fixtures' / (foundation + '-plan.json')), '--existing', str(path))
            self.write('all.json', tree)
        gap = next(path for path, (kind, _) in t.index(tree).items() if path.startswith('semantic.spacing.') and kind == 'dimension')
        result = t.preview({'all.json': tree}, plan({'op': 'create', 'file': 'all.json', 'path': 'component.test.gap', 'token': token('dimension', '{' + gap + '}')}))
        self.assertEqual({k: v for k, v in result['files']['all.json'].items() if k != 'component'}, tree)
        self.assertEqual(json.loads(path.read_text()), tree)


if __name__ == '__main__':
    unittest.main()
