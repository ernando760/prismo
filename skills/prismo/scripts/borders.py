#!/usr/bin/env python3
"""Borders: escalas dimensionais e intenção full; preview DTCG sem escrita."""
import argparse
from naming import path as naming_path
import copy
from decimal import Decimal, localcontext
import json
import strict_json
from spacing import preview_summary
from pathlib import Path
import sys

# Reutiliza apenas utilitários determinísticos; não executa a fundação Spacing.
from spacing import alias, calculate, dimension, exported, index, name, number


def full_radius(width, height):
    """Raio circular uniforme que produz cápsula/círculo no retângulo informado."""
    with localcontext() as ctx:
        ctx.prec = 40
        return exported(min(number(width, True), number(height, True)) / Decimal(2))


def resolve(tokens, path, category, seen=()):
    if not isinstance(path, str) or path in seen:
        raise ValueError('Alias circular ou caminho inválido: ' + str(path))
    if path not in tokens:
        raise ValueError('Token ausente: ' + path)
    kind, value = tokens[path]
    if kind not in ('dimension', 'number'):
        raise ValueError('Bordas exigem dimension ou multiplicador full tipado como number.')
    if alias(value):
        target_kind, target_value = resolve(tokens, value[1:-1], category, (*seen, path))
        if target_kind != kind:
            raise ValueError('Alias com tipos incompatíveis: ' + path)
        return kind, target_value
    if kind == 'dimension':
        return kind, dimension(value)
    if category == 'radius' and value == 0.5:
        return kind, value
    raise ValueError('Multiplicador full deve ser number 0.5 e é permitido somente para raios.')


def insert(tree, path, kind, value):
    node = tree
    parts = path.split('.')
    for part in parts[:-1]:
        if '$value' in node:
            raise ValueError('Token usado como grupo: ' + path)
        node = node.setdefault(part, {})
        if not isinstance(node, dict):
            raise ValueError('Grupo inválido: ' + path)
    if '$value' in node or parts[-1] in node:
        raise ValueError('Colisão com token/grupo existente: ' + path)
    node[parts[-1]] = {'$type': kind, '$value': copy.deepcopy(value)}


def build(plan, existing=None, naming=None):
    required = {'radius', 'width', 'full', 'bounds_px', 'root_px', 'semantics'}
    if not isinstance(plan, dict) or set(plan) != required:
        raise ValueError('Plano exige radius, width, full, bounds_px, root_px e semantics.')
    if not isinstance(plan['full'], bool):
        raise ValueError('full deve ser true ou false, conforme decisão explícita.')
    root = plan['root_px']
    if root is not None:
        number(root, True)
    bounds = plan['bounds_px']
    radius_for_bounds = None
    if bounds is not None:
        if not isinstance(bounds, dict) or set(bounds) != {'width', 'height'}:
            raise ValueError('bounds_px exige width e height, ou null.')
        radius_for_bounds = full_radius(bounds['width'], bounds['height'])
    semantics = plan['semantics']
    if not isinstance(semantics, dict) or not semantics or any(k not in ('radius', 'width') for k in semantics):
        raise ValueError('Semânticos permitidos: radius e width.')
    tree = copy.deepcopy(existing if existing is not None else {})
    tokens = index(tree)
    reused, scales, usages = [], {}, []

    def emit(path, category, kind, value, sources=()):
        nonlocal tokens
        if alias(value):
            expected_kind, expected = resolve(tokens, value[1:-1], category)
            if expected_kind != kind:
                raise ValueError('Tipo incompatível no alias: ' + path)
        else:
            expected = dimension(value) if kind == 'dimension' else value
        if path in tokens:
            if resolve(tokens, path, category) != (kind, expected):
                raise ValueError('Colisão com token existente: ' + path)
            reused.append(path)
            return
        if not alias(value):
            for candidate in tokens:
                # Não vincule raios/espessuras a outras fundações por coincidência.
                if candidate.startswith(naming_path('primitive', 'borders', naming) + '.') or candidate in sources:
                    try:
                        equal = resolve(tokens, candidate, category) == (kind, expected)
                    except ValueError:
                        continue
                    if equal:
                        value = '{' + candidate + '}'
                        break
        if alias(value):
            reused.append({'token': path, 'alias': value})
        insert(tree, path, kind, value)
        tokens = index(tree)

    def project(category, kind, value):
        if kind == 'number':
            return {'web': {'mode': 'runtime', 'formula_px': 'min(width,height)/2',
                            'borderRadius': None if radius_for_bounds is None else f'{radius_for_bounds}px'},
                    'flutter': {'shape': 'StadiumBorder', 'radius_for_bounds': radius_for_bounds}}
        if value['unit'] == 'rem' and root is None:
            raise ValueError('Informe root_px para dimensões rem.')
        with localcontext() as ctx:
            ctx.prec = 40
            logical = exported(number(value['value']) * (number(root, True) if value['unit'] == 'rem' else Decimal(1)))
        if category == 'radius':
            return {'web': {'borderRadius': f"{value['value']}{value['unit']}"},
                    'flutter': {'radius_logical_px': logical}}
        flutter = {'width_logical_px': logical}
        if logical == 0:
            flutter['style'] = 'none'  # BorderSide(width: 0) sozinho desenha hairline.
        return {'web': {'borderWidth': f"{value['value']}{value['unit']}"}, 'flutter': flutter}

    for category in ('radius', 'width'):
        config = plan[category]
        if not isinstance(config, dict) or set(config) != {'base', 'steps', 'rounding'} or not isinstance(config['steps'], dict):
            raise ValueError('Escala exige base, steps (multiplicadores) e rounding.')
        base = dimension(config['base']); number(base['value'], True)
        calculate(base['value'], 0, config['rounding'])
        if base['unit'] == 'rem' and root is None:
            raise ValueError('Informe root_px para a escala rem.')
        sources = {v[1:-1] for v in config['steps'].values() if alias(v)}
        scales[category] = []
        for step, multiplier in config['steps'].items():
            name(step)
            if category == 'radius' and step == 'full':
                raise ValueError('Nome radius.full reservado à intenção full; use a opção full.')
            raw = None
            if alias(multiplier):
                kind, value = resolve(tokens, multiplier[1:-1], category)
                if kind != 'dimension':
                    raise ValueError('Passos dimensionais não aceitam intenção full.')
                value = multiplier
            else:
                raw, size = calculate(base['value'], multiplier, config['rounding'])
                value = {'value': size, 'unit': base['unit']}
            path = naming_path('primitive', f'borders.{category}.{step}', naming)
            emit(path, category, 'dimension', value, sources)
            kind, final = resolve(tokens, path, category)
            scales[category].append({'token': path, 'raw_value': raw, 'value': final, **project(category, kind, final)})
    if plan['full']:
        path = naming_path('primitive', 'borders.radius.full', naming)
        emit(path, 'radius', 'number', 0.5)
        scales['radius'].append({'token': path, 'raw_value': None, 'value': 0.5, **project('radius', 'number', 0.5)})
    for category, roles in semantics.items():
        if not isinstance(roles, dict):
            raise ValueError('Papéis semânticos devem ser objetos.')
        for role, reference in roles.items():
            name(role)
            if not alias(reference):
                raise ValueError('Semânticos exigem aliases {caminho}.')
            kind, value = resolve(tokens, reference[1:-1], category)
            path = naming_path('semantic', f'borders.{category}.{role}', naming)
            emit(path, category, kind, reference)
            usages.append({'token': path, 'value': value, **project(category, kind, value)})
    if not usages:
        raise ValueError('Informe pelo menos um uso semântico definido.')
    # Evite gerar escalas sem finalidade: todo novo primitivo deve participar de um uso.
    needed = set()
    def visit(path):
        if path in needed:
            return
        needed.add(path)
        value = tokens[path][1]
        if alias(value):
            visit(value[1:-1])
    for usage in usages:
        visit(usage['token'])
    for rows in scales.values():
        for row in rows:
            if row['token'] not in needed:
                raise ValueError('Passo sem uso definido; remova do plano: ' + row['token'])
    return {'status': 'preview', 'tokens': tree, 'scales': scales, 'usages': usages, 'reused': reused,
            'validation': 'Tipos e aliases emitidos resolvidos; full é number 0.5 aplicado ao menor lado, não unidade DTCG. Layout não validado.'}


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
