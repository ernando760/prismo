#!/usr/bin/env python3
"""Typography: escala modular e preview DTCG; nenhuma escrita no consumidor."""
import argparse
from naming import path as naming_path
import copy
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
import json
import strict_json
from spacing import preview_summary
import math
from pathlib import Path
import sys

FIELDS = {'fontFamily': 'fontFamily', 'fontWeight': 'fontWeight', 'fontSize': 'dimension',
          'letterSpacing': 'dimension', 'lineHeight': 'number'}


def numeric(value, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'Número finito esperado: {value!r}')
    if positive and value <= 0:
        raise ValueError('Valor deve ser maior que zero.')
    return Decimal(str(value))


def label(value):
    if not isinstance(value, str) or not value.strip() or value.startswith('$') or any(c in value for c in '.{}'):
        raise ValueError(f'Nome de token inválido: {value!r}')
    return value


def alias(value):
    return isinstance(value, str) and value.startswith('{') and value.endswith('}')


def index(tree, prefix='', inherited=None):
    if not isinstance(tree, dict):
        raise ValueError('Documento DTCG deve conter objetos.')
    if '$extends' in tree or '$ref' in tree:
        raise ValueError('Expanda $extends/$ref em cópia temporária antes de usar este helper.')
    kind = tree.get('$type', inherited)
    if '$value' in tree:
        if any(not key.startswith('$') for key in tree):
            raise ValueError('Token não pode conter tokens filhos: ' + prefix)
        return {prefix: (kind, tree['$value'])}
    result = {}
    for key, child in tree.items():
        if key == '$root' or not key.startswith('$'):
            if key != '$root':
                label(key)
            result.update(index(child, f'{prefix}.{key}' if prefix else key, kind))
    return result


def resolved(tokens, path, kind, seen=()):
    if not isinstance(path, str) or path in seen:
        raise ValueError('Caminho inválido ou alias circular: ' + str(path))
    if path not in tokens or tokens[path][0] != kind:
        raise ValueError(f'Token ausente ou tipo diferente de {kind}: {path}')
    value = tokens[path][1]
    if alias(value):
        return resolved(tokens, value[1:-1], kind, (*seen, path))
    return checked(value, kind, tokens, (*seen, path))


def checked(value, kind, tokens, seen=()):
    if alias(value):
        return resolved(tokens, value[1:-1], kind, seen)
    if kind == 'fontFamily':
        if isinstance(value, str) and value.strip():
            return value
        if isinstance(value, list) and value and all(isinstance(v, str) and v.strip() and not alias(v) for v in value):
            return value
    elif kind == 'fontWeight':
        # Nomes DTCG normalizados para comparação e projeção numérica.
        groups = [('thin hairline', 100), ('extra-light ultra-light', 200), ('light', 300),
                  ('normal regular book', 400), ('medium', 500), ('semi-bold demi-bold', 600),
                  ('bold', 700), ('extra-bold ultra-bold', 800), ('black heavy', 900),
                  ('extra-black ultra-black', 950)]
        names = {name: weight for names, weight in groups for name in names.split()}
        if isinstance(value, str) and value in names:
            return names[value]
        if not isinstance(value, str) and 1 <= numeric(value) <= 1000:
            return value
    elif kind == 'dimension':
        if isinstance(value, dict) and set(value) == {'value', 'unit'} and value['unit'] in ('px', 'rem'):
            numeric(value['value'])
            return value
    elif kind == 'number':
        numeric(value)
        return value
    elif kind == 'typography' and isinstance(value, dict) and set(value) == set(FIELDS):
        result = {key: checked(value[key], child_kind, tokens, seen) for key, child_kind in FIELDS.items()}
        numeric(result['fontSize']['value'], positive=True)
        numeric(result['lineHeight'], positive=True)
        return result
    raise ValueError(f'Valor inválido para {kind}: {value!r}')


def put(tree, path, token):
    node = tree
    parts = path.split('.')
    for part in parts[:-1]:
        if '$value' in node:
            raise ValueError('Token usado como grupo: ' + path)
        node = node.setdefault(part, {})
        if not isinstance(node, dict):
            raise ValueError('Grupo inválido: ' + path)
    if '$value' in node or parts[-1] in node:
        raise ValueError('Colisão com destino existente: ' + path)
    node[parts[-1]] = token


def rounded(value, precision):
    try:
        with localcontext() as ctx:
            ctx.prec = 40
            result = value.quantize(Decimal(1).scaleb(-precision), rounding=ROUND_HALF_UP)
        result = float(result)
        if not math.isfinite(result):
            raise ValueError('Resultado fora do intervalo numérico suportado.')
        return 0.0 if result == 0 else result
    except InvalidOperation as error:
        raise ValueError('Resultado excede a precisão suportada.') from error


def modular(base, ratio, exponent, precision):
    if isinstance(exponent, bool) or not isinstance(exponent, int) or not -100 <= exponent <= 100:
        raise ValueError('Expoente deve ser inteiro entre -100 e 100 (limite de cálculo).')
    with localcontext() as ctx:
        ctx.prec = 40
        result = rounded(numeric(base, True) * numeric(ratio, True) ** exponent, precision)
    if result <= 0:
        raise ValueError('Tamanho arredondou para zero; ajuste escala ou precisão.')
    return result


def build(plan, existing=None, naming=None):
    required = {'base', 'ratio', 'precision', 'root_px', 'steps', 'families', 'weights', 'styles'}
    if not isinstance(plan, dict) or set(plan) != required:
        raise ValueError('Plano exige: ' + ', '.join(sorted(required)))
    base = checked(plan['base'], 'dimension', {})
    numeric(base['value'], True)
    if numeric(plan['ratio']) <= 1:
        raise ValueError('Razão modular deve ser maior que 1.')
    precision = plan['precision']
    if isinstance(precision, bool) or not isinstance(precision, int) or not 0 <= precision <= 8:
        raise ValueError('Precisão deve ser inteira entre 0 e 8 casas.')
    root = plan['root_px']
    if root is not None:
        numeric(root, True)
    if base['unit'] == 'rem' and root is None:
        raise ValueError('Informe root_px para projetar rem em pixels lógicos Flutter.')
    for field in ('steps', 'families', 'weights', 'styles'):
        if not isinstance(plan[field], dict):
            raise ValueError(field + ' deve ser um objeto.')
    if not plan['styles']:
        raise ValueError('Informe estilos explícitos ou aliases de estilos existentes.')
    tree = copy.deepcopy(existing if existing is not None else {})
    tokens = index(tree)
    reused = []

    def emit(path, kind, value):
        nonlocal tokens
        expected = checked(value, kind, tokens)
        if path in tokens:
            if resolved(tokens, path, kind) != expected:
                raise ValueError('Colisão com token existente: ' + path)
            reused.append(path)
            return '{' + path + '}'
        # Reutilize valores iguais de mesmo tipo; a comparação não mistura px/rem.
        if not alias(value):
            for candidate, (candidate_kind, _) in tokens.items():
                if candidate_kind == kind:
                    try:
                        equal = resolved(tokens, candidate, kind) == expected
                    except ValueError:
                        continue
                    if equal:
                        value = '{' + candidate + '}'
                        break
        if alias(value):
            reused.append({'token': path, 'alias': value})
        put(tree, path, {'$type': kind, '$value': copy.deepcopy(value)})
        tokens = index(tree)
        return '{' + path + '}'

    families = {label(key): emit(naming_path('primitive', f'typography.family.{key}', naming), 'fontFamily', value)
                for key, value in plan['families'].items()}
    weights = {label(key): emit(naming_path('primitive', f'typography.weight.{key}', naming), 'fontWeight', value)
               for key, value in plan['weights'].items()}
    sizes, scale = {}, []
    for key, exponent in plan['steps'].items():
        label(key)
        size = modular(base['value'], plan['ratio'], exponent, precision)
        sizes[key] = emit(naming_path('primitive', f'typography.size.{key}', naming), 'dimension', {'value': size, 'unit': base['unit']})
        scale.append({'step': key, 'exponent': exponent, 'fontSize': {'value': size, 'unit': base['unit']}})
    styles = []
    for key, config in plan['styles'].items():
        label(key)
        path = naming_path('semantic', f'typography.{key}', naming)
        if alias(config):
            style_alias = emit(path, 'typography', config)
        else:
            if not isinstance(config, dict) or set(config) != {'family', 'weight', 'step', 'line_height', 'letter_spacing_em'}:
                raise ValueError('Estilo exige family, weight, step, line_height e letter_spacing_em.')
            if config['family'] not in families or config['weight'] not in weights or config['step'] not in sizes:
                raise ValueError('Estilo referencia família, peso ou passo não declarado.')
            size = checked(sizes[config['step']], 'dimension', tokens)
            # Derivar as dimensões a partir do tamanho final arredondado/exportado.
            multiplier = rounded(numeric(config['line_height'], True), precision)
            if multiplier <= 0:
                raise ValueError('Line-height arredondou para zero.')
            tracking = rounded(numeric(size['value']) * numeric(config['letter_spacing_em']), precision)
            height_alias = emit(naming_path('primitive', f'typography.lineHeight.{key}', naming), 'number', multiplier)
            spacing_alias = emit(naming_path('primitive', f'typography.letterSpacing.{key}', naming), 'dimension', {'value': tracking, 'unit': size['unit']})
            style_alias = emit(path, 'typography', {'fontFamily': families[config['family']],
                               'fontWeight': weights[config['weight']], 'fontSize': sizes[config['step']],
                               'lineHeight': height_alias, 'letterSpacing': spacing_alias})
        value = checked(style_alias, 'typography', tokens)
        def logical(dimension):
            if dimension['unit'] == 'rem' and root is None:
                raise ValueError('Informe root_px para projetar dimensões rem existentes.')
            factor = numeric(root, True) if dimension['unit'] == 'rem' else Decimal(1)
            return rounded(numeric(dimension['value']) * factor, precision)
        family = value['fontFamily'] if isinstance(value['fontFamily'], list) else [value['fontFamily']]
        styles.append({'token': path, 'resolved': value,
                       'lineHeightDimension': {'value': rounded(numeric(value['fontSize']['value']) * numeric(value['lineHeight']), precision), 'unit': value['fontSize']['unit']},
                       'web': {'fontFamily': family, 'fontSize': value['fontSize'], 'lineHeight': value['lineHeight'], 'letterSpacing': value['letterSpacing'], 'fontWeight': value['fontWeight']},
                       'flutter': {'fontFamily': family[0], 'fontFamilyFallback': family[1:], 'fontSize': logical(value['fontSize']),
                                   'height': value['lineHeight'], 'letterSpacing': logical(value['letterSpacing']), 'fontWeight': value['fontWeight']}})
    return {'status': 'preview', 'tokens': tree, 'scale': scale, 'styles': styles, 'reused': reused,
            'validation': 'Tipos, dimensões e aliases emitidos resolvidos; não é auditoria WCAG ou validador DTCG completo.'}


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
