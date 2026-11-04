#!/usr/bin/env python3
"""Spacing: escalas e aliases DTCG determinísticos; preview sem escrita."""
import argparse
import copy
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR, ROUND_CEILING, localcontext
import json
import strict_json
from token_errors import UnsupportedTokenFormat
import math
from pathlib import Path
import sys

MODES = {'half_up': ROUND_HALF_UP, 'floor': ROUND_FLOOR, 'ceil': ROUND_CEILING}


def number(value, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'Número finito esperado: {value!r}')
    if value < 0 or (positive and value == 0):
        raise ValueError('Valor deve ser positivo.' if positive else 'Valor deve ser não negativo.')
    return Decimal(str(value))


def name(value):
    if not isinstance(value, str) or not value.strip() or value.startswith('$') or any(c in value for c in '.{}'):
        raise ValueError(f'Nome de token inválido: {value!r}')
    return value


def alias(value):
    return isinstance(value, str) and value.startswith('{') and value.endswith('}')


def index(tree, prefix='', inherited=None):
    if not isinstance(tree, dict):
        raise ValueError('Documento DTCG deve conter objetos.')
    if '$extends' in tree or '$ref' in tree:
        raise UnsupportedTokenFormat('Expanda $extends/$ref em cópia temporária antes de usar o helper.')
    kind = tree.get('$type', inherited)
    if '$value' in tree:
        if any(not key.startswith('$') for key in tree):
            raise ValueError('Token não pode ter tokens filhos: ' + prefix)
        return {prefix: (kind, tree['$value'])}
    result = {}
    for key, child in tree.items():
        if key == '$root' or not key.startswith('$'):
            if key != '$root':
                name(key)
            result.update(index(child, f'{prefix}.{key}' if prefix else key, kind))
    return result


def preview_summary(result, existing):
    """Omite documento completo e apresenta apenas tokens novos/alterados."""
    before = index(existing or {})
    after = index(result['tokens'])
    def leaf(tree, path):
        for part in path.split('.'):
            tree = tree[part]
        return tree
    changes = []
    for path in sorted(set(before) | set(after)):
        old = leaf(existing, path) if path in before else None
        new = leaf(result['tokens'], path) if path in after else None
        if old != new or before.get(path) != after.get(path):
            changes.append({'path': path, 'before': old, 'after': new})
    return {**{key: value for key, value in result.items() if key != 'tokens'}, 'token_changes': changes}


def dimension(value):
    if not isinstance(value, dict) or set(value) != {'value', 'unit'} or value['unit'] not in ('px', 'rem'):
        raise ValueError('Dimensão exige value e unit (px ou rem).')
    number(value['value'])
    return value


def resolve(tokens, path, seen=()):
    if not isinstance(path, str) or path in seen:
        raise ValueError('Alias circular ou caminho inválido: ' + str(path))
    if path not in tokens or tokens[path][0] != 'dimension':
        raise ValueError('Token dimension ausente ou de tipo incompatível: ' + path)
    value = tokens[path][1]
    return resolve(tokens, value[1:-1], (*seen, path)) if alias(value) else dimension(value)


def put(tree, path, value):
    parts = path.split('.')
    node = tree
    for part in parts[:-1]:
        if '$value' in node:
            raise ValueError('Token usado como grupo: ' + path)
        node = node.setdefault(part, {})
        if not isinstance(node, dict):
            raise ValueError('Grupo inválido: ' + path)
    if '$value' in node or parts[-1] in node:
        raise ValueError('Colisão com token/grupo existente: ' + path)
    node[parts[-1]] = {'$type': 'dimension', '$value': copy.deepcopy(value)}


def exported(value):
    result = float(value)
    if not math.isfinite(result) or (value != 0 and result == 0):
        raise ValueError('Resultado fora do intervalo numérico suportado.')
    return 0.0 if result == 0 else result


def _calculate(base, multiplier, rounding):
    if not isinstance(rounding, dict) or set(rounding) != {'mode', 'increment'} or rounding['mode'] not in MODES:
        raise ValueError('rounding exige mode (half_up/floor/ceil) e increment.')
    quantum = number(rounding['increment'], True)
    with localcontext() as ctx:
        ctx.prec = 40
        raw = base * multiplier
        snapped = (raw / quantum).to_integral_value(rounding=MODES[rounding['mode']]) * quantum
    return exported(raw), exported(snapped)


def calculate(base, multiplier, rounding):
    return _calculate(number(base, True), number(multiplier), rounding)


def build(plan, existing=None):
    if not isinstance(plan, dict) or set(plan) != {'base', 'progression', 'rounding', 'root_px', 'steps', 'semantics'}:
        raise ValueError('Plano exige base, progression, rounding, root_px, steps e semantics.')
    base = dimension(plan['base']); number(base['value'], True)
    root = plan['root_px']
    if root is not None:
        number(root, True)
    if base['unit'] == 'rem' and root is None:
        raise ValueError('Informe root_px para a projeção Flutter de rem.')
    # Valide arredondamento mesmo quando todos os passos são aliases.
    calculate(base['value'], 0, plan['rounding'])
    progression = plan['progression']
    if not isinstance(progression, dict):
        raise ValueError('progression deve ser um objeto.')
    if progression.get('type') == 'linear' and set(progression) == {'type', 'start', 'increment'}:
        start, increment = number(progression['start']), number(progression['increment'], True)
    elif progression == {'type': 'custom'}:
        start = increment = None
    else:
        raise ValueError('Progressão linear exige start/increment; custom exige apenas type.')
    if not isinstance(plan['steps'], dict) or not isinstance(plan['semantics'], dict):
        raise ValueError('steps e semantics devem ser objetos.')
    if not plan['semantics'] or any(k not in ('gap', 'padding', 'margin') for k in plan['semantics']):
        raise ValueError('Semânticos permitidos: gap, padding e margin.')
    tree = copy.deepcopy(existing if existing is not None else {})
    tokens = index(tree)
    reused, scale, usages = [], [], []
    # Reuso automático só dentro da escala de spacing ou em fontes explicitamente indicadas.
    reuse_sources = {v[1:-1] for v in plan['steps'].values() if alias(v)}

    def emit(path, value, deduplicate=False):
        nonlocal tokens
        expected = resolve(tokens, value[1:-1]) if alias(value) else dimension(value)
        if path in tokens:
            if resolve(tokens, path) != expected:
                raise ValueError('Colisão com token existente: ' + path)
            reused.append(path)
            return
        if deduplicate and not alias(value):
            for candidate in tokens:
                if candidate.startswith('primitive.spacing.') or candidate in reuse_sources:
                    try:
                        equal = resolve(tokens, candidate) == expected
                    except ValueError:
                        continue
                    if equal:
                        value = '{' + candidate + '}'
                        break
        if alias(value):
            reused.append({'token': path, 'alias': value})
        put(tree, path, value)
        tokens = index(tree)

    def projection(value):
        if value['unit'] == 'rem' and root is None:
            raise ValueError('Informe root_px para dimensões rem existentes.')
        with localcontext() as ctx:
            ctx.prec = 40
            logical = number(value['value']) * (number(root, True) if value['unit'] == 'rem' else Decimal(1))
        return {'web': f"{value['value']}{value['unit']}", 'flutter_logical_px': exported(logical)}

    for key, step in plan['steps'].items():
        name(key)
        raw = None
        if alias(step):
            value = step  # Não arredonde ou converta um token já existente.
        else:
            if progression['type'] == 'linear':
                if isinstance(step, bool) or not isinstance(step, int) or step < 0:
                    raise ValueError('Índice linear deve ser inteiro não negativo.')
                with localcontext() as ctx:
                    ctx.prec = 40
                    multiplier = start + increment * number(step)
                raw, size = _calculate(number(base['value'], True), multiplier, plan['rounding'])
            else:
                raw, size = calculate(base['value'], step, plan['rounding'])
            value = {'value': size, 'unit': base['unit']}
        path = f'primitive.spacing.{key}'
        emit(path, value, deduplicate=True)
        final_value = resolve(tokens, path)
        scale.append({'token': path, 'raw_value': raw, 'dimension': final_value, **projection(final_value)})
    for category, roles in plan['semantics'].items():
        if not isinstance(roles, dict):
            raise ValueError('Cada uso deve conter papéis por nome.')
        for role, reference in roles.items():
            name(role)
            if not alias(reference):
                raise ValueError('Papéis semânticos exigem aliases {caminho}.')
            path = f'semantic.spacing.{category}.{role}'
            emit(path, reference)
            final_value = resolve(tokens, path)
            usages.append({'token': path, 'dimension': final_value, **projection(final_value)})
    if not usages:
        raise ValueError('Informe pelo menos um papel semântico explícito.')
    return {'status': 'preview', 'tokens': tree, 'scale': scale, 'usages': usages, 'reused': reused,
            'validation': 'Dimensões e aliases emitidos resolvidos; não é validador DTCG completo ou teste de layout.'}


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
