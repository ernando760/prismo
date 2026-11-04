#!/usr/bin/env python3
"""Elevation: sombras DTCG e projeções de plataforma, apenas preview."""
import argparse
from naming import path as naming_path
import copy
from decimal import Decimal, ROUND_HALF_UP, localcontext
import json
import strict_json
from spacing import preview_summary
from token_errors import UnsupportedTokenFormat
import math
from pathlib import Path
import sys

from spacing import MODES, alias, exported, index, name, number
from borders import insert
from colors import rgb

DIMENSIONS = ('offsetX', 'offsetY', 'blur', 'spread')
SHADOW_FIELDS = {'color', *DIMENSIONS}


def signed(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Parâmetro deve ser um número finito: ' + str(value))
    return Decimal(str(value))


def opacity(value):
    result = number(value)
    if result > 1:
        raise ValueError('Opacidade/alpha deve estar entre 0 e 1.')
    return result


def alpha_product(alpha, multiplier, precision):
    if isinstance(precision, bool) or not isinstance(precision, int) or not 0 <= precision <= 8:
        raise ValueError('opacity_precision deve estar entre 0 e 8 casas.')
    with localcontext() as ctx:
        ctx.prec = 40
        value = (opacity(alpha) * opacity(multiplier)).quantize(Decimal(1).scaleb(-precision), rounding=ROUND_HALF_UP)
    return exported(value)


def validate_rounding(rounding):
    if not isinstance(rounding, dict) or set(rounding) != {'mode', 'increment'} or rounding['mode'] not in MODES:
        raise ValueError('rounding exige mode half_up/floor/ceil e increment positivo.')
    return number(rounding['increment'], True)


def calculate(value, scale, rounding):
    quantum = validate_rounding(rounding)
    with localcontext() as ctx:
        ctx.prec = 40
        raw = signed(value) * number(scale)
        result = (raw / quantum).to_integral_value(rounding=MODES[rounding['mode']]) * quantum
    return exported(result)


def flutter_sigma(blur):
    value = number(blur)
    with localcontext() as ctx:
        ctx.prec = 40
        return exported(value * Decimal('0.57735') + Decimal('0.5')) if value > 0 else 0.0


def checked(value, kind, tokens, seen=()):
    if alias(value):
        return resolve(tokens, value[1:-1], kind, seen)
    if kind == 'dimension':
        if not isinstance(value, dict) or set(value) != {'value', 'unit'} or value['unit'] not in ('px', 'rem'):
            raise ValueError('Dimensão exige value e unit px/rem.')
        signed(value['value'])
        return copy.deepcopy(value)
    if kind == 'color':
        if isinstance(value, str):
            value = {'colorSpace': 'srgb', 'components': list(rgb(value)), 'alpha': 1}
        if not isinstance(value, dict) or value.get('colorSpace') != 'srgb':
            raise UnsupportedTokenFormat('Sombras suportam apenas cores sRGB explícitas.')
        return {'colorSpace': 'srgb', 'components': list(rgb(value.get('components'))),
                'alpha': exported(opacity(value.get('alpha', 1)))}
    if kind == 'shadow':
        if isinstance(value, list):
            result = [checked(item, 'shadow', tokens, seen) for item in value]
            if any(isinstance(item, list) for item in result):
                raise ValueError('Alias de camada deve resolver objeto único; arrays não são achatados.')
            return result
        if not isinstance(value, dict) or not SHADOW_FIELDS <= set(value) or set(value) - SHADOW_FIELDS - {'inset'}:
            raise ValueError('Shadow exige color, offsetX, offsetY, blur, spread e inset opcional.')
        if not alias(value['color']) and not isinstance(value['color'], dict):
            raise ValueError('Cor em shadow DTCG deve ser objeto color ou alias.')
        result = {'color': checked(value['color'], 'color', tokens, seen)}
        for key in DIMENSIONS:
            result[key] = checked(value[key], 'dimension', tokens, seen)
        number(result['blur']['value'])
        if not isinstance(value.get('inset', False), bool):
            raise ValueError('inset deve ser booleano.')
        result['inset'] = value.get('inset', False)
        return result
    raise ValueError('Tipo não suportado: ' + str(kind))


def resolve(tokens, path, kind, seen=()):
    if not isinstance(path, str) or path in seen:
        raise ValueError('Alias circular ou caminho inválido: ' + str(path))
    if path not in tokens or tokens[path][0] != kind:
        raise ValueError(f'Token {kind} ausente ou com tipo incompatível: {path}')
    value = tokens[path][1]
    if kind == 'color' and isinstance(value, str) and not alias(value):
        raise ValueError('Token color DTCG existente exige objeto, não hex legado.')
    return checked(value, kind, tokens, (*seen, path))


def project(value, root):
    layers = value if isinstance(value, list) else [value]
    css, flutter, warnings = [], [], []
    def logical(dimension):
        if dimension['unit'] == 'rem' and root is None:
            raise ValueError('Informe root_px para projetar rem em pixels lógicos.')
        with localcontext() as ctx:
            ctx.prec = 40
            return exported(signed(dimension['value']) * (number(root, True) if dimension['unit'] == 'rem' else Decimal(1)))
    for i, layer in enumerate(layers):
        dims = {key: logical(layer[key]) for key in DIMENSIONS}
        rgba = layer['color']
        components = ' '.join(str(exported(signed(v) * Decimal(255))) for v in rgba['components'])
        css_color = f"rgb({components} / {rgba['alpha']})"
        css_dimensions = ' '.join(f"{layer[k]['value']}{layer[k]['unit']}" for k in DIMENSIONS)
        css.append(('inset ' if layer['inset'] else '') + css_dimensions + ' ' + css_color)
        flutter.append({'source_layer': i, 'offset': [dims['offsetX'], dims['offsetY']],
                        'blurRadius': dims['blur'], 'spreadRadius': dims['spread'],
                        'color': rgba, 'diagnostic_blur_sigma': flutter_sigma(dims['blur'])})
        if layer['inset']:
            warnings.append(f'Camada {i}: inset não tem equivalente direto em BoxShadow.')
        if rgba['alpha'] == 0:
            warnings.append(f'Camada {i}: alpha final zero; rever finalidade da camada invisível.')
    supported = not any(layer['inset'] for layer in layers)
    return {'web': {'boxShadow': ', '.join(css) if css else 'none'},
            'flutter': {'supported': supported, 'boxShadow': list(reversed(flutter)) if supported else None,
                        'order': 'back-to-front; reverse da ordem CSS/DTCG'},
            'warnings': warnings}


def semantic_aliases(semantics, prefix=()):
    """Normaliza nomes legados, caminhos pontuados e grupos aninhados."""
    for role, reference in semantics.items():
        if not isinstance(role, str):
            raise ValueError('Nome semântico deve ser textual.')
        parts = role.split('.')
        for part in parts:
            name(part)
        path = (*prefix, *parts)
        if isinstance(reference, dict) and reference:
            yield from semantic_aliases(reference, path)
        elif alias(reference):
            yield '.'.join(path), reference
        else:
            raise ValueError('Semânticos exigem aliases {caminho} ou grupos não vazios.')


def build(plan, existing=None, naming=None):
    required = {'unit', 'root_px', 'rounding', 'opacity_precision', 'levels', 'semantics'}
    if not isinstance(plan, dict) or set(plan) != required:
        raise ValueError('Plano exige unit, root_px, rounding, opacity_precision, levels e semantics.')
    if plan['unit'] not in ('px', 'rem'):
        raise ValueError('Unidade deve ser px ou rem.')
    root = plan['root_px']
    if root is not None:
        number(root, True)
    if plan['unit'] == 'rem' and root is None:
        raise ValueError('Informe root_px para unidade rem.')
    validate_rounding(plan['rounding']); alpha_product(1, 1, plan['opacity_precision'])
    if not isinstance(plan['levels'], dict) or not isinstance(plan['semantics'], dict) or not plan['semantics']:
        raise ValueError('levels e semantics devem ser objetos, com ao menos uma finalidade semântica.')
    tree = copy.deepcopy(existing if existing is not None else {})
    tokens = index(tree)
    reused, levels, usages = [], [], []
    created_colors = set()

    def emit(path, kind, value):
        nonlocal tokens
        expected = checked(value, kind, tokens)
        if path in tokens:
            if resolve(tokens, path, kind) != expected:
                raise ValueError('Colisão com token existente: ' + path)
            reused.append(path)
            return '{' + path + '}'
        if not alias(value):
            for candidate in tokens:
                if candidate.startswith(naming_path('primitive', 'elevation', naming) + '.') and tokens[candidate][0] == kind:
                    try:
                        equal = resolve(tokens, candidate, kind) == expected
                    except ValueError:
                        continue
                    if equal:
                        value = '{' + candidate + '}'
                        break
        if alias(value):
            reused.append({'token': path, 'alias': value})
        insert(tree, path, kind, value)
        tokens = index(tree)
        return '{' + path + '}'

    for level, configs in plan['levels'].items():
        name(level)
        if alias(configs):
            value = configs
        elif isinstance(configs, list):
            value = []
            for i, config in enumerate(configs):
                if alias(config):
                    if isinstance(checked(config, 'shadow', tokens), list):
                        raise ValueError('Alias de camada deve resolver objeto único.')
                    value.append(config)
                    continue
                if not isinstance(config, dict) or set(config) != {*SHADOW_FIELDS, 'opacity', 'scale', 'inset'}:
                    raise ValueError('Camada exige color, opacity, scale, inset, offsetX/Y, blur e spread.')
                if not isinstance(config['inset'], bool):
                    raise ValueError('inset deve ser booleano.')
                number(config['blur'])
                base_color = checked(config['color'], 'color', tokens)
                final_color = copy.deepcopy(base_color)
                final_color['alpha'] = alpha_product(base_color['alpha'], config['opacity'], plan['opacity_precision'])
                # Preserve alias da cor de origem quando o alpha não muda.
                color_value = config['color'] if alias(config['color']) and final_color == base_color else final_color
                color_path = naming_path('primitive', f'elevation.color.{level}.layer{i}', naming)
                if color_path not in tokens:
                    created_colors.add(color_path)
                color_alias = emit(color_path, 'color', color_value)
                layer = {'color': color_alias, 'inset': config['inset']}
                for key in DIMENSIONS:
                    layer[key] = {'value': calculate(config[key], config['scale'], plan['rounding']), 'unit': plan['unit']}
                value.append(layer)
        else:
            raise ValueError('Nível exige lista de camadas ou alias de shadow existente.')
        path = naming_path('primitive', f'elevation.shadow.{level}', naming)
        reference = emit(path, 'shadow', value)
        final = checked(reference, 'shadow', tokens)
        if level == 'none' and final != []:
            raise ValueError('Nível none deve representar lista vazia de sombras.')
        levels.append({'token': path, 'resolved': final, 'validation': 'valid', **project(final, root)})
    semantics = list(semantic_aliases(plan['semantics']))
    paths = [role for role, _ in semantics]
    if len(set(paths)) != len(paths):
        raise ValueError('Caminho semântico repetido após normalização.')
    for role in paths:
        if any(parent in paths for parent in ('.'.join(role.split('.')[:i]) for i in range(1, len(role.split('.'))))):
            raise ValueError('Semântico usado como token e grupo: ' + role)
    for role, reference in semantics:
        path = naming_path('semantic', f'elevation.{role}', naming)
        emit(path, 'shadow', reference)
        final = resolve(tokens, path, 'shadow')
        usages.append({'token': path, 'resolved': final, 'validation': 'valid', **project(final, root)})
    needed = set()
    def visit(value):
        if alias(value):
            path = value[1:-1]
            if path not in needed:
                needed.add(path); visit(tokens[path][1])
        elif isinstance(value, dict):
            for child in value.values(): visit(child)
        elif isinstance(value, list):
            for child in value: visit(child)
    for usage in usages: visit('{' + usage['token'] + '}')
    for level in levels:
        if level['token'] not in needed:
            raise ValueError('Nível sem finalidade definida: ' + level['token'])
    # Um shadow deduplicado pode dispensar cores intermediárias recém-criadas.
    removed = created_colors - needed
    def existed(parts):
        node = existing if existing is not None else {}
        for part in parts:
            if not isinstance(node, dict) or part not in node:
                return False
            node = node[part]
        return True
    for path in removed:
        parts, stack, node = path.split('.'), [], tree
        for part in parts[:-1]:
            stack.append((node, part))
            node = node[part]
        del node[parts[-1]]
        for depth in range(len(stack) - 1, -1, -1):
            parent, key = stack[depth]
            if not parent[key] and not existed(parts[:depth + 1]):
                del parent[key]
            else:
                break
    reused = [entry for entry in reused if (entry['token'] if isinstance(entry, dict) else entry) not in removed]
    return {'status': 'preview', 'tokens': tree, 'levels': levels, 'usages': usages, 'reused': reused,
            'validation': 'Parâmetros, tipos e aliases emitidos validados; equivalência visual e custo de renderização não medidos.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--existing', type=Path)
    parser.add_argument('--full', action='store_true', help='Incluir documento completo de tokens.')
    args = parser.parse_args()
    try:
        existing = strict_json.loads(args.existing.read_text(encoding='utf-8')) if args.existing else None
        result = build(strict_json.loads(args.plan.read_text(encoding='utf-8')), existing)
        if not args.full:
            result = preview_summary(result, existing)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError, TypeError, KeyError, ArithmeticError) as error:
        print(f'Erro: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
