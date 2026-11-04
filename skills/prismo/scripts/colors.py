#!/usr/bin/env python3
"""Colors: preview JSON determinístico. Não escreve tokens ou decisões no projeto."""
import argparse
import copy
import json
import strict_json
import math
from pathlib import Path
import re
import sys


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
    if kind not in ('normal_text', 'large_text', 'non_text'):
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


def build(plan, existing=None):
    if not isinstance(plan, dict) or set(plan) != {'palettes', 'themes', 'pairs'}:
        raise ValueError('Plano exige palettes, themes e pairs.')
    if not isinstance(plan['palettes'], dict) or not isinstance(plan['themes'], dict) or not plan['themes']:
        raise ValueError('Palettes e themes devem ser objetos; escolha temas explicitamente.')
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
            path = f'primitive.{palette}.{step}'
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
            path = f'semantic.{theme}.{role}'
            put(tree, path, {'$type': 'color', '$value': '{' + target + '}'})
            tokens = flatten(tree)
    if not isinstance(plan['pairs'], list) or not plan['pairs']:
        raise ValueError('Informe os pares de contraste e seus usos.')
    results = []
    for pair in plan['pairs']:
        if not isinstance(pair, dict) or set(pair) != {'foreground', 'background', 'usage'}:
            raise ValueError('Par exige foreground, background e usage.')
        fg, bg = (resolve(tokens, pair[k]) for k in ('foreground', 'background'))
        results.append({**pair, **evaluate(contrast(fg, bg), pair['usage'])})
    return {'status': 'preview', 'tokens': tree, 'swatches': swatches, 'reused': reused, 'contrast': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    palette = sub.add_parser('palette')
    palette.add_argument('--plan', type=Path, required=True)
    palette.add_argument('--existing', type=Path)
    palette.add_argument('--full', action='store_true', help='Incluir documento completo de tokens.')
    check = sub.add_parser('contrast')
    check.add_argument('foreground'); check.add_argument('background')
    check.add_argument('--usage', choices=['normal_text', 'large_text', 'non_text'], default='normal_text')
    check.add_argument('--fail-on', choices=['AA', 'AAA'])
    args = parser.parse_args()
    try:
        if args.command == 'palette':
            existing = strict_json.loads(args.existing.read_text()) if args.existing else None
            result = build(strict_json.loads(args.plan.read_text()), existing)
        else:
            result = evaluate(contrast(args.foreground, args.background), args.usage)
        if args.command == 'palette' and not args.full:
            from spacing import preview_summary
            result = preview_summary(result, existing)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        if args.command == 'contrast' and args.fail_on and result[args.fail_on] is not True:
            return 2
        return 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(f'Erro: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
