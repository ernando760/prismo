#!/usr/bin/env python3
"""Colors: preview JSON determinístico. Não escreve tokens ou decisões no projeto."""
import argparse
from naming import path as naming_path
import copy
import json
import strict_json
import math
from pathlib import Path
import re
import sys


USAGES = ('normal_text', 'large_text', 'non_text')


def number(value, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'Número finito esperado entre {low} e {high}: {value!r}')
    return value


def rgb(value):
    """Apenas sRGB opaco explícito; transparência exige composição externa conhecida."""
    if isinstance(value, str) and re.fullmatch(r'#[0-9a-fA-F]{6}', value):
        return tuple(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5))
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return tuple(number(v, 0, 1) for v in value)
    raise ValueError('Use #RRGGBB opaco ou três componentes sRGB entre 0 e 1.')


def linear(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def encoded(v):
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def to_oklch(value):
    r, g, b = map(linear, rgb(value))
    l = (0.4122214708*r + 0.5363325363*g + 0.0514459929*b) ** (1/3)
    m = (0.2119034982*r + 0.6806995451*g + 0.1073969566*b) ** (1/3)
    s = (0.0883024619*r + 0.2817188376*g + 0.6299787005*b) ** (1/3)
    light = 0.2104542553*l + 0.7936177850*m - 0.0040720468*s
    a = 1.9779984951*l - 2.4285922050*m + 0.4505937099*s
    b = 0.0259040371*l + 0.7827717662*m - 0.8086757660*s
    chroma = math.hypot(a, b)
    return (light, 0.0, 0.0) if chroma < 1e-7 else (light, chroma, math.degrees(math.atan2(b, a)) % 360)


def from_oklch(light, chroma, hue):
    a, b = chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))
    l = (light + 0.3963377774*a + 0.2158037573*b) ** 3
    m = (light - 0.1055613458*a - 0.0638541728*b) ** 3
    s = (light - 0.0894841775*a - 1.2914855480*b) ** 3
    return tuple(map(encoded, (4.0767416621*l - 3.3077115913*m + 0.2309699292*s,
                              -1.2684380046*l + 2.6097574011*m - 0.3413193965*s,
                              -0.0041960863*l - 0.7034186147*m + 1.7076147010*s)))


def gamut_map(light, chroma, hue):
    """Busca binária de chroma, 48 passos; não é o gamut mapping CSS local-MINDE."""
    number(light, 0, 1); number(chroma, 0, 1); number(hue, 0, 360)
    if light in (0, 1):
        return (light, light, light), (light, 0, hue), chroma != 0
    def inside(c):
        return all(-1e-10 <= v <= 1 + 1e-10 for v in from_oklch(light, c, hue))
    mapped = not inside(chroma)
    if mapped:
        low, high = 0.0, chroma
        for _ in range(48):
            middle = (low + high) / 2
            if inside(middle):
                low = middle
            else:
                high = middle
        chroma = low
    # Clamp somente do erro numérico na fronteira; não recorta canais fora da gama.
    return tuple(min(1, max(0, v)) for v in from_oklch(light, chroma, hue)), (light, chroma, hue), mapped


def quantize(value):
    return tuple(math.floor(v * 255 + 0.5) / 255 for v in rgb(value))


def hex_color(value):
    return '#' + ''.join(f'{math.floor(v * 255 + 0.5):02x}' for v in rgb(value))


def contrast(foreground, background):
    def luminance(value):
        return sum(w * linear(v) for w, v in zip((0.2126, 0.7152, 0.0722), rgb(value)))
    a, b = sorted((luminance(foreground), luminance(background)))
    return (b + 0.05) / (a + 0.05)


def evaluate(ratio, kind):
    number(ratio, 1, 21)
    if kind not in USAGES:
        raise ValueError('Uso esperado: normal_text, large_text ou non_text.')
    aa = 4.5 if kind == 'normal_text' else 3
    aaa = {'normal_text': 7, 'large_text': 4.5, 'non_text': None}[kind]
    return {'ratio': ratio, 'usage': kind, 'AA': ratio >= aa,
            'AAA': None if aaa is None else ratio >= aaa,
            'threshold_AA': aa, 'threshold_AAA': aaa}


def name(value):
    if not isinstance(value, str) or not value or any(c in value for c in '.{}') or value.startswith('$'):
        raise ValueError(f'Nome de token inválido: {value!r}')
    return value


def flatten(tree, prefix=(), inherited=None):
    if not isinstance(tree, dict):
        raise ValueError('Documento DTCG deve conter objetos.')
    if '$extends' in tree or '$ref' in tree:
        raise ValueError('Expanda $extends/$ref antes de usar este helper.')
    token_type = tree.get('$type', inherited)
    if '$value' in tree:
        return {'.'.join(prefix): (tree, token_type)}
    result = {}
    for key, child in tree.items():
        if key == '$root':
            result.update(flatten(child, prefix + (key,), token_type))
        elif not key.startswith('$'):
            name(key)
            result.update(flatten(child, prefix + (key,), token_type))
    return result


def resolve(tokens, path, seen=()):
    if path in seen:
        raise ValueError('Alias circular: ' + path)
    if path not in tokens or tokens[path][1] != 'color':
        raise ValueError('Token de cor ausente ou sem tipo color: ' + path)
    value = tokens[path][0]['$value']
    if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
        return resolve(tokens, value[1:-1], (*seen, path))
    if not isinstance(value, dict) or value.get('colorSpace') != 'srgb' or value.get('alpha', 1) != 1:
        raise ValueError('Reuso direto exige DTCG color sRGB opaco: ' + path)
    return rgb(value.get('components'))


def put(tree, path, token):
    node = tree
    parts = path.split('.')
    for part in parts[:-1]:
        if '$value' in node:
            raise ValueError('Token usado como grupo: ' + path)
        node = node.setdefault(part, {})
        if not isinstance(node, dict):
            raise ValueError('Grupo inválido: ' + path)
    if '$value' in node:
        raise ValueError('Token usado como grupo: ' + path)
    if parts[-1] in node and node[parts[-1]] != token:
        raise ValueError('Colisão com token existente: ' + path)
    node[parts[-1]] = token


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Coverage exige texto não vazio.')
    return value


def coverage_report(coverage, plan, tokens, results, generated):
    """Contrato opt-in; evidência declarada não é inspeção executada pelo helper."""
    if (not isinstance(coverage, dict) or set(coverage) != {'version', 'uses', 'steps'}
            or type(coverage['version']) is not int or coverage['version'] != 1
            or not isinstance(coverage['uses'], list) or not isinstance(coverage['steps'], list)):
        raise ValueError('Coverage exige version 1, uses e steps.')
    rows, ids = [], set()
    for use in coverage['uses']:
        required = {'id', 'use', 'theme', 'horizon', 'status', 'evidence', 'pending',
                    'tokens', 'pairs', 'visual', 'decision', 'alternatives', 'review_when'}
        if not isinstance(use, dict) or set(use) != required:
            raise ValueError('Uso de coverage tem campos ausentes/desconhecidos.')
        for key in ('id', 'use', 'evidence', 'review_when'):
            text(use[key])
        if use['id'] in ids:
            raise ValueError('ID de coverage duplicado: ' + use['id'])
        ids.add(use['id'])
        if use['theme'] not in plan['themes']:
            raise ValueError('Tema de coverage fora do escopo.')
        if use['horizon'] not in ('functional', 'evolution') or use['status'] not in (
                'covered', 'partial', 'deferred', 'not_evaluated'):
            raise ValueError('Horizonte/status de coverage inválido.')
        if use['decision'] not in ('reuse', 'extension', 'exception', 'undecided'):
            raise ValueError('Decisão de coverage inválida.')
        text(use['alternatives'])
        for key in ('pending', 'tokens', 'pairs'):
            if not isinstance(use[key], list):
                raise ValueError('Coverage exige listas em pending, tokens e pairs.')
        for pending in use['pending']:
            text(pending)
        traces = []
        for path in use['tokens']:
            text(path)
            value = resolve(tokens, path)
            chain, current = [], path
            while True:
                chain.append(current)
                alias = tokens[current][0]['$value']
                if not isinstance(alias, str):
                    break
                current = alias[1:-1]
            traces.append({'token': path, 'chain': chain, 'hex': hex_color(value),
                           'resolved_srgb': list(value)})
        checked = []
        for pair in use['pairs']:
            if not isinstance(pair, dict) or set(pair) != {'foreground', 'background', 'usage'}:
                raise ValueError('Par de coverage inválido.')
            match = next((r for r in results if all(r[k] == pair[k] for k in pair)), None)
            if match is None:
                raise ValueError('Par de coverage não consta dos pares calculados.')
            if any(pair[k] not in use['tokens'] for k in ('foreground', 'background')):
                raise ValueError('Par deve constar dos tokens do uso.')
            checked.append(match)
        visual = use['visual']
        if (not isinstance(visual, dict) or set(visual) != {'status', 'evidence'}
                or visual['status'] not in ('passed', 'failed', 'pending', 'not_applicable')):
            raise ValueError('Visual exige status e evidence.')
        text(visual['evidence'])
        calculation = ('not_evaluated' if not checked else
                       'passed' if all(r['AA'] for r in checked) else 'failed')
        if use['status'] == 'covered' and (not traces or use['pending']
                or calculation == 'failed' or visual['status'] not in ('passed', 'not_applicable')
                or use['decision'] == 'undecided'):
            raise ValueError('Uso coberto exige evidências e ausência de pendências relevantes.')
        if use['status'] == 'covered' and not checked:
            raise ValueError('Uso sem cálculo fica parcial; cálculo externo é limitação explícita.')
        if use['status'] == 'not_evaluated' and (checked or visual['status'] in ('passed', 'failed')):
            raise ValueError('Uso já avaliado não pode ser not_evaluated.')
        rows.append({**copy.deepcopy(use), 'calculation': calculation, 'contrast': checked,
                     'traces': traces, 'conformance': 'not_assessed',
                     'visual_source': 'declared_evidence_not_verified_by_helper'})
    planned = set()
    for step in coverage['steps']:
        if (not isinstance(step, dict) or set(step) != {'token', 'uses', 'reason', 'naming_evidence'}
                or not isinstance(step['uses'], list) or not step['uses']):
            raise ValueError('Passo exige token, uses, reason e naming_evidence.')
        text(step['reason']); text(step['naming_evidence']); text(step['token'])
        if step['token'] in planned or step['token'] not in generated:
            raise ValueError('Passo duplicado ou fora da escala proposta.')
        planned.add(step['token'])
        for uid in step['uses']:
            row = next((r for r in rows if r['id'] == uid), None)
            if row is None or step['token'] not in row['tokens'] or row['decision'] != 'extension':
                raise ValueError('Passo exige uso concreto/evolução com decisão extension e token rastreado.')
            if row['status'] in ('deferred', 'not_evaluated'):
                raise ValueError('Uso adiado/não avaliado não autoriza gerar passo.')
    if planned != set(generated):
        raise ValueError('Justifique cada passo proposto em coverage.steps.')
    return {'status': 'recorded', 'uses': rows, 'steps': copy.deepcopy(coverage['steps']),
            'summary': {status: sum(r['status'] == status for r in rows)
                        for status in ('covered', 'partial', 'deferred', 'not_evaluated')},
            'conformance': 'not_assessed'}


def palette_review(swatches, tokens=None):
    """Valores finais e relações, sem limiar universal de harmonia/distinção."""
    values, adjacent = [], []
    for swatch in swatches:
        final = to_oklch(swatch['hex'])
        values.append({'token': swatch['token'], 'final_oklch': list(final)})
        if len(values) > 1:
            prev = values[-2]
            if prev['token'].rsplit('.', 1)[0] == swatch['token'].rsplit('.', 1)[0]:
                a = prev['final_oklch']; b = final
                hue_delta = (b[2] - a[2] + 180) % 360 - 180 if min(a[1], b[1]) > 1e-7 else None
                distance = math.sqrt(max(0, (b[0]-a[0])**2 + a[1]**2 + b[1]**2 -
                                     2*a[1]*b[1]*math.cos(math.radians(b[2]-a[2]))))
                adjacent.append({'from': prev['token'], 'to': swatch['token'],
                                 'delta_L': b[0]-a[0], 'delta_C': b[1]-a[1],
                                 'delta_H': hue_delta, 'distance_oklab': distance,
                                 'identical_after_quantization': swatches[len(values)-2]['hex'] == swatch['hex']})
    families = {}
    if tokens is not None:
        prefixes = {swatch['token'].rsplit('.', 1)[0] for swatch in swatches}
        for prefix in sorted(prefixes):
            members = []
            for path, (_, kind) in tokens.items():
                if kind != 'color' or path.rsplit('.', 1)[0] != prefix:
                    continue
                try:
                    value = resolve(tokens, path)
                    members.append({'token': path, 'hex': hex_color(value),
                                    'final_oklch': list(to_oklch(value))})
                except ValueError:
                    members.append({'token': path, 'status': 'unsupported_manual_review'})
            families[prefix] = members
    return {'families_including_existing': families, 'values': values, 'adjacent_in_plan_order': adjacent,
            'visual_validation': 'not_performed',
            'limitations': 'Vizinhos na ordem explícita do plano; famílias incluem tokens existentes para revisão contextual. Números dos nomes não são luminosidade. Medidas não garantem harmonia ou distinção.'}


def summary(result, existing):
    from spacing import preview_summary
    brief = preview_summary(result, existing)
    if 'coverage' in brief:
        brief['coverage'] = coverage_summary(brief['coverage'])
    review = brief.pop('perceptual_review')
    brief['perceptual_review'] = {'visual_validation': review['visual_validation'],
        'limitations': review['limitations'],
        'identical_pairs': [p for p in review['adjacent_in_plan_order'] if p['identical_after_quantization']]}
    return brief


def recorded_coverage(record, trees, naming=None):
    """Recalcula somente pares existentes; nunca gera escalas nem tokens."""
    foundations = record.get('foundations', {})
    if not isinstance(foundations, dict) or not isinstance(foundations.get('colors', {}), dict):
        raise ValueError('Registro de Colors inválido; investigar sem sobrescrever.')
    foundation = foundations.get('colors', {})
    plan = foundation.get('plan', {})
    if not isinstance(plan, dict):
        raise ValueError('Plano registrado de Colors inválido.')
    if 'coverage' not in plan:
        return {'status': 'unknown_legacy', 'conformance': 'not_assessed'}
    tokens = {}
    for tree in trees.values():
        for path, token in flatten(tree).items():
            if path in tokens:
                raise ValueError('Contextos de cor sobrepostos: ' + path)
            tokens[path] = token
    results = [{**pair, **evaluate(contrast(resolve(tokens, pair['foreground']),
                                          resolve(tokens, pair['background'])), pair['usage'])}
               for pair in plan['pairs']]
    generated = [naming_path('primitive', palette + '.' + step, naming)
                 for palette, config in plan['palettes'].items() for step in config['steps']]
    return coverage_report(plan['coverage'], plan, tokens, results, generated)


def coverage_summary(coverage):
    return {**{k: v for k, v in coverage.items() if k not in ('uses', 'steps')},
            'uses': [{k: row[k] for k in ('id', 'use', 'theme', 'horizon', 'status',
                      'decision', 'calculation', 'visual', 'pending', 'conformance')}
                     for row in coverage.get('uses', [])]}


def build(plan, existing=None, naming=None, *, require_coverage=False):
    if not isinstance(plan, dict) or set(plan) - {'palettes', 'themes', 'pairs', 'coverage'} or not {'palettes', 'themes', 'pairs'} <= set(plan):
        raise ValueError('Plano exige palettes, themes e pairs; coverage é opcional no modo legado.')
    if require_coverage and 'coverage' not in plan:
        raise ValueError('--require-coverage exige plan.coverage para os usos afetados; consulte colors-coverage.md.')
    if not isinstance(plan['palettes'], dict) or not isinstance(plan['themes'], dict) or not plan['themes']:
        raise ValueError('palettes e themes devem ser objetos; themes exige ao menos light ou dark (papéis podem ser {}).')
    if any(t not in ('light', 'dark') for t in plan['themes']):
        raise ValueError('Temas suportados: light e dark.')
    tree = copy.deepcopy(existing if existing is not None else {})
    tokens = flatten(tree)
    swatches, reused = [], []
    for palette, config in plan['palettes'].items():
        name(palette)
        if not isinstance(config, dict) or set(config) != {'seed', 'steps'} or not isinstance(config['steps'], dict) or not config['steps']:
            raise ValueError('Paleta exige seed e steps não vazios.')
        seed = config['seed']
        if isinstance(seed, list) and len(seed) == 3:
            light, chroma, hue = seed
            number(light, 0, 1); number(chroma, 0, 1); number(hue, 0, 360)
        else:
            light, chroma, hue = to_oklch(seed)
        # Seed não é alterada nem implicitamente adicionada à escala.
        for step, level in config['steps'].items():
            name(step); number(level, 0, 1)
            raw, mapped_lch, mapped = gamut_map(level, chroma, hue)
            final = quantize(raw)
            path = naming_path('primitive', f'{palette}.{step}', naming)
            duplicate = None
            for candidate, (_, token_type) in tokens.items():
                if token_type == 'color':
                    try:
                        value = resolve(tokens, candidate)
                    except ValueError:
                        continue  # Cores existentes não suportadas ficam intocadas.
                    if max(abs(a-b) for a, b in zip(value, final)) < 1e-12:
                        duplicate = candidate
                        break
            if path in tokens:
                if max(abs(a-b) for a, b in zip(resolve(tokens, path), final)) >= 1e-12:
                    raise ValueError('Colisão com token existente: ' + path)
                reused.append(path)
            else:
                value = '{' + duplicate + '}' if duplicate else {'colorSpace': 'srgb', 'components': list(final), 'alpha': 1, 'hex': hex_color(final)}
                put(tree, path, {'$type': 'color', '$value': value})
                if duplicate:
                    reused.append({'token': path, 'alias': duplicate})
                tokens = flatten(tree)
            swatches.append({'token': path, 'hex': hex_color(final), 'requested_oklch': [level, chroma, hue],
                             'mapped_oklch': list(mapped_lch), 'gamut_mapped': mapped})
    for theme, roles in plan['themes'].items():
        if not isinstance(roles, dict):
            raise ValueError('Papéis semânticos devem ser um objeto (vazio para reutilizar existentes).')
        for role, target in roles.items():
            name(role)
            if not isinstance(target, str):
                raise ValueError('Papel semântico exige caminho de token.')
            resolve(tokens, target)
            path = naming_path('semantic', f'{theme}.{role}', naming)
            put(tree, path, {'$type': 'color', '$value': '{' + target + '}'})
            tokens = flatten(tree)
    if not isinstance(plan['pairs'], list) or (not plan['pairs'] and 'coverage' not in plan):
        raise ValueError('pairs exige lista não vazia no modo legado; pairs: [] só é permitido com coverage válido, sem declarar cálculo aprovado.')
    results = []
    for index, pair in enumerate(plan['pairs']):
        if not isinstance(pair, dict) or set(pair) != {'foreground', 'background', 'usage'}:
            raise ValueError(f'pairs[{index}] exige foreground, background e usage.')
        if pair['usage'] not in USAGES:
            raise ValueError(f'pairs[{index}].usage: use ' + ', '.join(USAGES) + '.')
        fg, bg = (resolve(tokens, pair[k]) for k in ('foreground', 'background'))
        results.append({**pair, **evaluate(contrast(fg, bg), pair['usage'])})
    coverage = (coverage_report(plan['coverage'], plan, tokens, results,
                [s['token'] for s in swatches]) if 'coverage' in plan else
                {'status': 'unknown_legacy', 'conformance': 'not_assessed'})
    if require_coverage and not coverage['uses']:
        raise ValueError('--require-coverage exige ao menos um uso afetado em coverage.uses.')
    return {'status': 'preview', 'tokens': tree, 'swatches': swatches, 'reused': reused,
            'contrast': results, 'coverage': coverage, 'perceptual_review': palette_review(swatches, tokens)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    palette = sub.add_parser('palette', formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Preview somente leitura; valida o contrato JSON, sem aprovar nem persistir.',
        epilog="""Contrato JSON:
  palettes: objeto {familia: {seed: "#RRGGBB" ou [L,C,H], steps: {nome: L}}};
    use {} para reuso. Sem quantidade fixa nem geração implícita de passos.
  themes: objeto não vazio com light e/ou dark; {"light": {}} reutiliza papéis.
  pairs: [{"foreground": "caminho", "background": "caminho", "usage": "normal_text"}].
    usage aceita somente normal_text, large_text, non_text (não ui_component).
    pairs: [] exige coverage válido e não significa contraste aprovado.
  coverage: {"version": 1, "uses": [...], "steps": [...]}.
    uses: id, use, theme, horizon (functional|evolution), status
    (covered|partial|deferred|not_evaluated), evidence, pending, tokens, pairs,
    visual {status: passed|failed|pending|not_applicable, evidence}, decision
    (reuse|extension|exception|undecided), alternatives, review_when.
    steps: token, uses [IDs], reason, naming_evidence; justifique os passos propostos.
    Matriz incremental: somente usos afetados; não copie o histórico inteiro.

Exemplos:
  python3 colors.py palette --plan /tmp/plan.json --existing tokens.json --require-coverage
  python3 colors.py palette --plan - --existing tokens.json --require-coverage < /tmp/plan.json
  python3 colors.py palette --plan legacy.json --existing tokens.json

Novas propostas: leia references/colors-coverage.md, adapte
assets/templates/colors-coverage-plan.json e valide antes de apresentar a matriz.
Arquivo/--plan - (stdin) são equivalentes. Confira retorno e stderr antes de ler
stdout como JSON. Exit 0 = cálculo/contrato concluídos, não aprovação visual,
contraste garantido ou autorização. Exit 1 = entrada inválida (stderr; stdout vazio).
Resumo por padrão; --full somente para detalhes. Planos legados não exigem coverage.
""")
    palette.add_argument('--plan', type=Path, required=True, help='Plano JSON; - lê stdin, sem arquivo temporário.')
    palette.add_argument('--existing', type=Path, help='Fonte DTCG existente, somente leitura.')
    palette.add_argument('--require-coverage', action='store_true',
                         help='Exigir cobertura válida e não vazia dos usos afetados em novas propostas.')
    palette.add_argument('--full', action='store_true', help='Incluir documento completo de tokens.')
    check = sub.add_parser('contrast')
    check.add_argument('foreground'); check.add_argument('background')
    check.add_argument('--usage', choices=USAGES, default='normal_text')
    check.add_argument('--fail-on', choices=['AA', 'AAA'])
    args = parser.parse_args()
    try:
        if args.command == 'palette':
            existing = strict_json.loads(args.existing.read_text()) if args.existing else None
            content = sys.stdin.read() if args.plan == Path('-') else args.plan.read_text()
            result = build(strict_json.loads(content), existing, require_coverage=args.require_coverage)
        else:
            result = evaluate(contrast(args.foreground, args.background), args.usage)
        if args.command == 'palette' and not args.full:
            result = summary(result, existing)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        if args.command == 'contrast' and args.fail_on and result[args.fail_on] is not True:
            return 2
        return 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(f'Erro: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
