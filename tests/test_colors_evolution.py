"""Coverage contract, incremental planning, perception and transactional recovery."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/prismo/scripts'))
import colors as c
import foundations as f
from naming import policy


def plan():
    fg, bg = 'primitive.gray.900', 'primitive.gray.100'
    pair = {'foreground': fg, 'background': bg, 'usage': 'normal_text'}
    row = {'id': 'body', 'use': 'Body text on surface', 'theme': 'light',
           'horizon': 'functional', 'status': 'partial', 'evidence': 'Approved brief',
           'pending': ['Visual inspection'], 'tokens': [fg, bg], 'pairs': [pair],
           'visual': {'status': 'pending', 'evidence': 'Not inspected'},
           'decision': 'extension', 'alternatives': 'No existing palette',
           'review_when': 'Inspect real component'}
    return {'palettes': {'gray': {'seed': '#808080', 'steps': {'100': 1, '900': 0}}},
            'themes': {'light': {}}, 'pairs': [pair],
            'coverage': {'version': 1, 'uses': [row], 'steps': [
                {'token': t, 'uses': ['body'], 'reason': 'Required text pair',
                 'naming_evidence': 'Existing numeric convention, lighter first'} for t in (bg, fg)]}}


def spec(p):
    return {'plan': p, 'sources': {k: {'origin': 'user', 'evidence': 'Approved test brief'}
                                  for k in p}, 'pending': ['Visual inspection']}


class CoverageTests(unittest.TestCase):
    def test_calculated_is_not_visually_validated_or_conformant(self):
        result = c.build(plan())
        row = result['coverage']['uses'][0]
        self.assertEqual(row['calculation'], 'passed')
        self.assertEqual(row['status'], 'partial')
        self.assertEqual(row['visual']['status'], 'pending')
        self.assertEqual(row['conformance'], 'not_assessed')
        self.assertEqual(result['perceptual_review']['visual_validation'], 'not_performed')

    def test_covered_requires_separate_evidence_and_no_pending(self):
        p = plan(); row = p['coverage']['uses'][0]; row['status'] = 'covered'
        with self.assertRaises(ValueError): c.build(p)
        row['pending'] = []; row['visual'] = {'status': 'passed', 'evidence': 'Browser capture reviewed by designer'}
        result = c.build(p)['coverage']['uses'][0]
        self.assertEqual(result['status'], 'covered')
        self.assertEqual(result['conformance'], 'not_assessed')
        row['pairs'] = []
        with self.assertRaises(ValueError): c.build(p)

    def test_deferred_and_unknown_evolution_do_not_generate_tokens(self):
        p = plan(); p['palettes'] = {}; p['pairs'] = []; p['coverage']['steps'] = []
        row = p['coverage']['uses'][0]
        row.update(horizon='evolution', status='deferred', decision='undecided', tokens=[], pairs=[])
        result = c.build(p)
        self.assertEqual(result['tokens'], {})
        row['status'] = 'not_evaluated'
        self.assertEqual(c.build(p)['coverage']['summary']['not_evaluated'], 1)

    def test_expected_evolution_may_justify_step_without_fixed_count(self):
        for count in (1, 3, 5):
            p = plan(); p['palettes']['gray']['steps'] = {str(i): (i+1)/(count+1) for i in range(count)}
            row = p['coverage']['uses'][0]
            row.update(horizon='evolution', evidence='Approved roadmap: navigation states', pairs=[],
                       tokens=['primitive.gray.'+str(i) for i in range(count)])
            p['pairs'] = []
            p['coverage']['steps'] = [{'token': t, 'uses': ['body'], 'reason': 'Roadmap coverage benefit',
                                      'naming_evidence': 'Explicit approved steps'} for t in row['tokens']]
            result = c.build(p)
            self.assertEqual(len(result['swatches']), count)
            row['status'] = 'deferred'
            with self.assertRaises(ValueError): c.build(p)

    def test_invalid_contracts_and_unjustified_steps_rejected(self):
        edits = [lambda p: p['coverage'].update(version=True),
                 lambda p: p['coverage']['uses'].append(copy.deepcopy(p['coverage']['uses'][0])),
                 lambda p: p['coverage']['uses'][0].update(theme='dark'),
                 lambda p: p['coverage']['uses'][0].update(evidence=''),
                 lambda p: p['coverage'].update(steps=[]),
                 lambda p: p['coverage']['steps'][0].update(naming_evidence=''),
                 lambda p: p['coverage']['steps'][0].update(uses=['missing']),
                 lambda p: p['coverage']['uses'][0].update(status='not_evaluated'),
                 lambda p: p['coverage']['uses'][0].update(pairs=[{'foreground': 'missing', 'background': 'primitive.gray.100', 'usage': 'normal_text'}])]
        for edit in edits:
            p = plan(); edit(p)
            with self.subTest(plan=p), self.assertRaises(ValueError): c.build(p)

    def test_legacy_reuse_has_unknown_coverage_and_no_new_tokens(self):
        p = plan(); del p['coverage']
        existing = c.build(p)['tokens']; original = copy.deepcopy(existing)
        reuse = {'palettes': {}, 'themes': {'light': {}}, 'pairs': p['pairs']}
        result = c.build(reuse, existing)
        self.assertEqual(result['tokens'], original)
        self.assertEqual(existing, original)
        self.assertEqual(result['coverage']['status'], 'unknown_legacy')

    def test_exception_and_same_value_different_intentions_are_not_promoted(self):
        p = plan(); existing = c.build(p)['tokens']
        p['palettes'] = {}; p['coverage']['steps'] = []
        row = p['coverage']['uses'][0]; row['decision'] = 'exception'
        row['alternatives'] = 'Component purpose differs despite same resolved color'
        result = c.build(p, existing)
        self.assertEqual(result['tokens'], existing)
        self.assertEqual(result['coverage']['uses'][0]['decision'], 'exception')
        row['decision'] = 'reuse'
        self.assertEqual(c.build(p, existing)['tokens'], existing)

    def test_poc5_style_four_component_exceptions_do_not_expand_shared_palette(self):
        p = plan(); existing = c.build(p)['tokens']
        p['palettes'] = {}; p['coverage']['steps'] = []; p['coverage']['uses'] = []
        p['pairs'] = []; p['themes']['dark'] = {}
        for theme, state, color in [('light', 'hover', '#30259b'), ('light', 'pressed', '#453cca'),
                                    ('dark', 'hover', '#c8ccff'), ('dark', 'pressed', '#a3a9ff')]:
            path = 'component.button.' + theme + '.' + state
            c.put(existing, path, {'$type': 'color', '$value': {'colorSpace': 'srgb',
                                  'components': list(c.rgb(color)), 'alpha': 1}})
            foreground = 'primitive.gray.' + ('100' if theme == 'light' else '900')
            pair = {'foreground': foreground, 'background': path, 'usage': 'normal_text'}
            row = copy.deepcopy(plan()['coverage']['uses'][0])
            row.update(id=theme+'-'+state, theme=theme, decision='exception',
                       tokens=[foreground, path], pairs=[pair],
                       alternatives='Component-specific trajectory; shared use not demonstrated',
                       review_when='Another real consumer or revised brand trajectory')
            p['coverage']['uses'].append(row); p['pairs'].append(pair)
        before = copy.deepcopy(existing)
        result = c.build(p, existing)
        self.assertEqual(result['tokens'], before)
        self.assertEqual(result['swatches'], [])
        self.assertTrue(all(row['calculation'] == 'passed' for row in result['coverage']['uses']))
        self.assertTrue(all(row['status'] == 'partial' for row in result['coverage']['uses']))

    def test_custom_names_insertion_and_collision_preserve_tokens(self):
        naming = policy({'version': 1, 'mode': 'custom', 'levels': {'primitive': {'prefix': 'base'}}})
        p = plan(); del p['coverage']; p['pairs'] = [{**r, 'foreground': 'base.gray.900',
                                                    'background': 'base.gray.100'} for r in p['pairs']]
        existing = c.build(p, naming=naming)['tokens']; before = copy.deepcopy(existing)
        p['palettes']['gray']['steps'] = {'450': .55}
        result = c.build(p, existing, naming)
        self.assertIn('450', result['tokens']['base']['gray'])
        self.assertEqual(existing, before)
        p['palettes']['gray']['steps'] = {'900': .55}
        with self.assertRaises(ValueError): c.build(p, existing, naming)
        self.assertEqual(existing, before)

    def test_alias_trace_missing_cycle_and_theme_context(self):
        p = plan(); existing = c.build(p)['tokens']; p['palettes'] = {}; p['coverage']['steps'] = []
        existing['label'] = {'$type': 'color', '$value': '{primitive.gray.900}'}
        p['coverage']['uses'][0]['tokens'].append('label')
        trace = c.build(p, existing)['coverage']['uses'][0]['traces'][-1]
        self.assertEqual(trace['chain'], ['label', 'primitive.gray.900'])
        existing['label']['$value'] = '{label}'
        with self.assertRaises(ValueError): c.build(p, existing)
        existing['label']['$value'] = '{absent}'
        with self.assertRaises(ValueError): c.build(p, existing)

    def test_final_perception_quantization_gamut_and_order(self):
        p = plan(); del p['coverage']
        p['palettes']['gray'] = {'seed': [0.5, .8, 30], 'steps': {'100': .6, '200': .60000000001, '900': .2}}
        p['themes'] = {'light': {}}
        result = c.build(p)
        review = result['perceptual_review']
        self.assertTrue(result['swatches'][0]['gamut_mapped'])
        self.assertTrue(review['adjacent_in_plan_order'][0]['identical_after_quantization'])
        self.assertLess(review['adjacent_in_plan_order'][1]['delta_L'], 0)
        for value, swatch in zip(review['values'], result['swatches']):
            self.assertEqual(value['final_oklch'], list(c.to_oklch(swatch['hex'])))
        self.assertEqual(c.build(p), result)

    def test_summary_keeps_material_decisions_and_details_are_available(self):
        full = c.build(plan()); brief = c.summary(full, {})
        self.assertEqual(brief['coverage']['summary'], full['coverage']['summary'])
        self.assertEqual(brief['coverage']['uses'][0]['pending'], ['Visual inspection'])
        self.assertNotIn('traces', brief['coverage']['uses'][0])
        self.assertTrue(full['coverage']['uses'][0]['traces'])
        self.assertEqual(len(brief['token_changes']), 2)

    def test_split_sources_theme_mappings_and_failed_pairs_remain_separate(self):
        p = plan(); existing = c.build(p)['tokens']
        p['palettes'] = {}; p['coverage']['steps'] = []
        p['themes']['dark'] = {}
        row = copy.deepcopy(p['coverage']['uses'][0]); row.update(id='dark-body', theme='dark')
        pair = {'foreground': 'primitive.gray.100', 'background': 'primitive.gray.900', 'usage': 'normal_text'}
        row['pairs'] = [pair]; p['pairs'].append(pair); p['coverage']['uses'].append(row)
        record = {'foundations': {'colors': {'plan': p}}}
        trees = {'base.json': existing, 'semantic.json': {'text': {'$type': 'color', '$value': '{primitive.gray.900}'}}}
        before = copy.deepcopy(trees)
        result = c.recorded_coverage(record, trees)
        self.assertEqual([r['theme'] for r in result['uses']], ['light', 'dark'])
        self.assertTrue(all(r['calculation'] == 'passed' for r in result['uses']))
        self.assertEqual(trees, before)
        with self.assertRaises(ValueError): c.recorded_coverage(record, {'a': existing, 'b': existing})
        pair['foreground'] = pair['background']
        self.assertEqual(c.recorded_coverage(record, trees)['uses'][1]['calculation'], 'failed')



class CoveragePersistenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name); (self.root / 'ds').mkdir()
        self.decisions = self.root / 'ds/decisions.json'; self.tokens = self.root / 'ds/tokens.json'
        self.checklist = self.root / 'ds/foundations-plan.json'
        self.decisions.write_text(json.dumps({'decisions': {'paths': {'tokens': 'ds/tokens.json'}}, 'keep': 42}))
        self.tokens.write_text('{}')

    def run_flow(self, specs=None):
        return f.execute(self.root, ['colors'], specs, 'ds/decisions.json')

    def test_persist_and_resume_without_rewrite_or_visual_claim(self):
        self.run_flow({'colors': spec(plan())})
        before = [p.read_bytes() for p in (self.tokens, self.decisions)]
        state = self.run_flow()
        self.assertEqual(state['steps']['colors']['status'], 'completed')
        self.assertEqual(state['steps']['colors']['validation']['coverage']['uses'][0]['status'], 'partial')
        self.assertEqual(before, [p.read_bytes() for p in (self.tokens, self.decisions)])
        self.assertEqual(json.loads(self.decisions.read_text())['keep'], 42)

    def test_interrupt_each_transaction_boundary_recovers_coherent_matrix(self):
        original = f.atomic
        for target in (self.tokens, self.decisions, self.checklist):
            with self.subTest(target=target.name):
                self.setUp()
                # Match newly created temporary paths by basename.
                def interrupt(path, content):
                    if path.name == target.name and ((path == self.checklist and '"completed_once"' in content)
                                                     or path in (self.tokens, self.decisions)):
                        raise KeyboardInterrupt()
                    original(path, content)
                with patch.object(f, 'atomic', side_effect=interrupt):
                    with self.assertRaises(KeyboardInterrupt): self.run_flow({'colors': spec(plan())})
                state = self.run_flow()
                self.assertEqual(state['steps']['colors']['status'], 'completed')
                saved = json.loads(self.decisions.read_text())['foundations']['colors']
                self.assertEqual(saved['validation']['coverage'], state['steps']['colors']['validation']['coverage'])
                self.assertEqual(saved['plan']['coverage'], plan()['coverage'])

    def test_conflict_blocks_recovery_and_different_scope(self):
        original = f.atomic
        def interrupt(path, content):
            if path == self.decisions: raise KeyboardInterrupt()
            original(path, content)
        with patch.object(f, 'atomic', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt): self.run_flow({'colors': spec(plan())})
        with self.assertRaises(ValueError): f.execute(self.root, ['spacing'], decisions='ds/decisions.json')
        self.tokens.write_text('{"external": {"$type": "number", "$value": 5}}')
        state = self.run_flow()
        self.assertEqual(state['steps']['colors']['status'], 'failed')
        self.assertIn('Conflito', state['steps']['colors']['error'])
        self.assertIn('external', json.loads(self.tokens.read_text()))

    def test_corrupted_coverage_cannot_be_reported_as_persisted(self):
        self.run_flow({'colors': spec(plan())})
        record = json.loads(self.decisions.read_text())
        record['foundations']['colors']['validation']['coverage']['uses'][0]['status'] = 'covered'
        self.decisions.write_text(json.dumps(record))
        state = self.run_flow()
        self.assertEqual(state['steps']['colors']['status'], 'failed')
        self.assertNotIn('persisted', state['steps']['colors']['checks'])

    def test_audit_recalculates_existing_pairs_without_palette_generation_or_writes(self):
        import audit
        self.run_flow({'colors': spec(plan())})
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(c, 'build', side_effect=AssertionError('Audit must not generate')):
            result = audit.audit(self.root, decisions='ds/decisions.json')
        self.assertEqual(result['checks']['colors_coverage']['uses'][0]['calculation'], 'passed')
        self.assertEqual(result['checks']['colors_coverage']['uses'][0]['visual']['status'], 'pending')
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        tokens = json.loads(self.tokens.read_text()); tokens['primitive']['gray']['900']['$value'] = tokens['primitive']['gray']['100']['$value']
        self.tokens.write_text(json.dumps(tokens))
        result = audit.audit(self.root, decisions='ds/decisions.json')
        self.assertEqual(result['checks']['colors_coverage']['uses'][0]['calculation'], 'failed')
        self.assertTrue(any(item['code'] == 'COLORS_DECLARED_CONTRAST' for item in result['findings']))

    def test_malformed_legacy_colors_record_is_review_not_crash(self):
        import audit
        self.run_flow({'colors': spec(plan())})
        record = json.loads(self.decisions.read_text()); record['foundations']['colors'] = []
        self.decisions.write_text(json.dumps(record))
        result = audit.audit(self.root, decisions='ds/decisions.json')
        self.assertEqual(result['checks']['colors_coverage']['status'], 'needs_review')
        self.assertTrue(any(item['code'] == 'COLORS_COVERAGE' for item in result['findings']))

    def test_full_flow_document_inventory_and_token_preview_preserve_matrix(self):
        import document
        import tokens
        self.run_flow({'colors': spec(plan())})
        saved = self.decisions.read_bytes()
        inventory = document.inventory(self.root, decisions='ds/decisions.json')
        self.assertTrue(inventory['declared_token_source_exists'])
        original = json.loads(self.tokens.read_text())
        result = tokens.preview({'ds/tokens.json': original}, {'changes': [], 'bindings': {}})
        self.assertEqual(result['changes'], [])
        self.assertEqual(self.decisions.read_bytes(), saved)
        self.assertEqual(c.recorded_coverage(json.loads(saved), {'ds/tokens.json': original})['uses'][0]['status'], 'partial')


class CoverageCLITests(unittest.TestCase):
    def test_template_summary_and_full_cli_match(self):
        import subprocess
        root = Path(__file__).resolve().parents[1]
        template = root / 'skills/prismo/assets/templates/colors-coverage-plan.json'
        self.assertEqual(json.loads(template.read_text()), plan())
        command = [sys.executable, str(root / 'skills/prismo/scripts/colors.py'), 'palette', '--plan', str(template)]
        short = subprocess.run(command, capture_output=True, text=True)
        full = subprocess.run(command + ['--full'], capture_output=True, text=True)
        self.assertEqual(short.returncode, 0, short.stderr)
        self.assertEqual(full.returncode, 0, full.stderr)
        a, b = json.loads(short.stdout), json.loads(full.stdout)
        self.assertEqual(a['coverage'], c.coverage_summary(b['coverage']))
        self.assertNotIn('tokens', a)
        self.assertEqual(len(a['token_changes']), 2)
        self.assertEqual(len(b['coverage']['uses'][0]['traces']), 2)
