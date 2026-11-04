#!/usr/bin/env python3
"""Valida tokens e calcula mudanças/impactos em leitura. Não persiste ou aprova planos."""
import argparse
import copy
import json
import os
from pathlib import Path
import sys

import strict_json
from token_errors import UnsupportedTokenFormat, InvalidTokenType
from token_source import token_source as find_token_source
from spacing import index, name, alias, number
from typography import checked as typography_checked, numeric
from elevation import checked as elevation_checked

TYPES = {'color', 'dimension', 'fontFamily', 'fontWeight', 'number', 'typography',
         'shadow', 'duration', 'cubicBezier', 'strokeStyle', 'border', 'transition', 'gradient'}
SKIP = {'.git', '.agents', '.codex', 'node_modules', '.venv', '__pycache__', 'build',
        'dist', '.docusaurus', '.dart_tool', 'coverage', 'vendor', '.next'}
TEXT = {'.css', '.scss', '.sass', '.less', '.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx',
        '.dart', '.json', '.md', '.mdx', '.yaml', '.yml', '.html', '.svg'}


def read(path):
    result = strict_json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(result, dict):
        raise ValueError('Objeto JSON esperado: ' + str(path))
    return result


def relative(root, value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or any(p in ('', '.', '..') for p in value.split('/')):
        raise ValueError('Caminho relativo inválido: ' + str(value))
    path = root / value
    if not path.resolve().is_relative_to(root):
        raise ValueError('Caminho fora do projeto: ' + value)
    if any(p.is_symlink() for p in (path, *path.parents) if p != root and root in p.parents):
        raise ValueError('Fonte/escopo com symlink: ' + value)
    return path


def parts(path):
    if not isinstance(path, str) or not path:
        raise ValueError('Caminho de token não vazio esperado.')
    result = path.split('.')
    for item in result:
        if item != '$root':
            name(item)
    return result


def node(tree, path):
    for part in parts(path):
        tree = tree[part]
    return tree


def put(tree, path, token):
    keys = parts(path)
    for key in keys[:-1]:
        if '$value' in tree:
            raise ValueError('Token usado como grupo: ' + path)
        tree = tree.setdefault(key, {})
        if not isinstance(tree, dict):
            raise ValueError('Grupo inválido: ' + path)
    if '$value' in tree or keys[-1] in tree:
        raise ValueError('Destino ocupado por token/grupo: ' + path)
    tree[keys[-1]] = copy.deepcopy(token)


def remove(tree, path):
    keys = parts(path)
    for key in keys[:-1]:
        tree = tree[key]
    del tree[keys[-1]]  # Grupos/metadados, mesmo vazios, são preservados.


def refs(value):
    if alias(value):
        target = value[1:-1]
        parts(target)
        yield target
    elif isinstance(value, dict):
        if '$ref' in value:
            raise UnsupportedTokenFormat('$ref não suportado; usar pipeline compatível, sem converter a fonte.')
        for child in value.values():
            yield from refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from refs(child)


def rewrite(value, old, new):
    if isinstance(value, str):
        return '{' + new + '}' if value == '{' + old + '}' else value
    if isinstance(value, dict):
        return {key: rewrite(child, old, new) for key, child in value.items()}
    if isinstance(value, list):
        return [rewrite(child, old, new) for child in value]
    return value


def collect(sources):
    tokens, owners = {}, {}
    for filename, tree in sources.items():
        for path, token in index(tree).items():
            parts(path)
            if path in tokens:
                raise ValueError('Token duplicado entre fontes: ' + path)
            tokens[path], owners[path] = token, filename
    for path in tokens:
        keys = path.split('.')
        if any('.'.join(keys[:i]) in tokens for i in range(1, len(keys))):
            raise ValueError('Token usado como grupo entre fontes: ' + path)
    return tokens, owners


def validate(sources):
    json.dumps(sources, allow_nan=False)
    tokens, owners = collect(sources)
    def metadata(tree):
        if '$type' in tree and tree['$type'] not in TYPES:
            raise InvalidTokenType('Tipo inválido: ' + str(tree['$type']))
        for key, types in (('$description', (str,)), ('$deprecated', (bool, str)), ('$extensions', (dict,))):
            if key in tree and not isinstance(tree[key], types):
                raise ValueError('Metadado inválido: ' + key)
        for key, value in tree.items():
            if key == '$root' or not key.startswith('$'):
                metadata(value)
    for tree in sources.values():
        metadata(tree)
    graph = {path: set(refs(value)) for path, (_, value) in tokens.items()}
    resolved = {}
    def resolve(path, expected=None, stack=()):
        if path not in tokens:
            raise ValueError('Referência inexistente: ' + path)
        if path in stack:
            raise ValueError('Ciclo: ' + ' -> '.join((*stack, path)))
        kind, value = tokens[path]
        if kind not in TYPES:
            raise InvalidTokenType('Tipo ausente ou inválido: ' + path + ': ' + str(kind))
        if expected and kind != expected:
            raise ValueError('Tipo incompatível: ' + path + ', esperado ' + expected)
        if path in resolved:
            return resolved[path]
        # Verifica todo grafo, inclusive aliases em valores compostos.
        for target in sorted(graph[path]):
            resolve(target, stack=(*stack, path))
        if path not in resolved:
            resolved[path] = check(value, kind, (*stack, path))
        return resolved[path]
    def fields(value, required, optional=()):
        if not isinstance(value, dict) or not set(required) <= set(value) or set(value) - set(required) - set(optional):
            raise ValueError('Campos inválidos: esperado ' + ', '.join(required))
    def check(value, kind, stack):
        if alias(value):
            return resolve(value[1:-1], kind, stack)
        if kind == 'color':
            if not isinstance(value, dict):
                raise ValueError('Color DTCG deve ser objeto sRGB ou alias, não HEX.')
            return elevation_checked(value, kind, tokens, stack)
        if kind in {'dimension', 'fontFamily', 'fontWeight', 'number', 'typography'}:
            return typography_checked(value, kind, tokens, stack)
        if kind == 'shadow':
            return elevation_checked(value, kind, tokens, stack)
        if kind == 'duration':
            fields(value, ('value', 'unit'))
            number(value['value'])
            if value['unit'] not in ('ms', 's'):
                raise ValueError('Duration exige ms ou s.')
        elif kind == 'cubicBezier':
            if not isinstance(value, list) or len(value) != 4:
                raise ValueError('CubicBezier exige quatro números.')
            for v in value:
                numeric(v)
            if not all(0 <= value[i] <= 1 for i in (0, 2)):
                raise ValueError('CubicBezier: x1/x2 devem estar entre 0 e 1.')
        elif kind == 'strokeStyle':
            if isinstance(value, str):
                if value not in ('solid', 'dashed', 'dotted', 'double', 'groove', 'ridge', 'outset', 'inset'):
                    raise ValueError('StrokeStyle desconhecido.')
            else:
                fields(value, ('dashArray', 'lineCap'))
                if value['lineCap'] not in ('round', 'butt', 'square') or not isinstance(value['dashArray'], list):
                    raise ValueError('StrokeStyle exige dashArray e lineCap válido.')
                dimensions = [check(item, 'dimension', stack) for item in value['dashArray']]
                for item in dimensions:
                    number(item['value'])
                return {'dashArray': dimensions, 'lineCap': value['lineCap']}
        elif kind in ('border', 'transition'):
            schema = {'color': 'color', 'width': 'dimension', 'style': 'strokeStyle'} if kind == 'border' else {'duration': 'duration', 'delay': 'duration', 'timingFunction': 'cubicBezier'}
            fields(value, schema)
            return {key: check(value[key], sub, stack) for key, sub in schema.items()}
        elif kind == 'gradient':
            if not isinstance(value, list):
                raise ValueError('Gradient exige array de paradas.')
            result = []
            for stop in value:
                if alias(stop):
                    raise UnsupportedTokenFormat('Alias de parada gradient não suportado neste helper.')
                fields(stop, ('color', 'position'))
                position = check(stop['position'], 'number', stack)
                result.append({'color': check(stop['color'], 'color', stack), 'position': min(1, max(0, position))})
            return result
        return copy.deepcopy(value)
    for path in tokens:
        resolve(path)
    # Valores iguais são candidatos, não duplicações semânticas comprovadas.
    values, duplicates = {}, []
    for path, (kind, raw) in tokens.items():
        if alias(raw):
            continue
        key = (kind, json.dumps(resolved[path], sort_keys=True, ensure_ascii=False))
        if key in values:
            duplicates.append([values[key], path])
        else:
            values[key] = path
    return tokens, owners, graph, resolved, duplicates


def preview(sources, plan):
    if not isinstance(plan, dict) or set(plan) != {'changes', 'bindings'} or not isinstance(plan['changes'], list) or not isinstance(plan['bindings'], dict):
        raise ValueError('Plano exige changes (lista) e bindings (mapa de nomes de código).')
    before, owners = collect(sources)
    baseline_error = None
    try:
        _, _, graph_before, values_before, _ = validate(sources)
    except ValueError as error:
        # Permite propor reparo de aliases/tipos, mas nunca aprova resultado inválido.
        baseline_error, values_before, graph_before = str(error), None, {}
        for path, (_, value) in before.items():
            try:
                graph_before[path] = set(refs(value))
            except ValueError:
                graph_before[path] = set()
    for path, bindings in plan['bindings'].items():
        parts(path)
        if path not in before or not isinstance(bindings, list) or not all(isinstance(b, str) and b.strip() for b in bindings):
            raise ValueError('Binding exige token existente e lista de nomes textuais.')
    working = copy.deepcopy(sources)
    moves = []
    for change in plan['changes']:
        if not isinstance(change, dict):
            raise ValueError('Mudança deve ser objeto.')
        op = change.get('op')
        required = {'create': {'op', 'file', 'path', 'token'}, 'edit': {'op', 'path', 'patch'},
                    'move': {'op', 'path', 'file', 'to'}, 'remove': {'op', 'path'}}
        if op not in required or set(change) != required[op]:
            raise ValueError('Operação/campos inválidos: ' + str(op))
        path = change['path']; parts(path)
        current, owner = collect(working)
        if op == 'create':
            if path in current:
                raise ValueError('Token já existe: ' + path)
        elif path not in current:
            raise ValueError('Token não encontrado para ' + op + ': ' + path)
        if op in ('create', 'move'):
            filename = change['file']
            if filename not in working:
                raise ValueError('Destino deve ser uma fonte fornecida: ' + str(filename))
        if op == 'create':
            token = change['token']
            if not isinstance(token, dict) or '$value' not in token:
                raise ValueError('create exige token DTCG com $value.')
            put(working[filename], path, token)
        elif op == 'edit':
            patch = change['patch']
            if not isinstance(patch, dict) or not patch or not all(isinstance(k, str) and k.startswith('$') for k in patch):
                raise ValueError('edit exige patch de propriedades DTCG não vazio.')
            node(working[owner[path]], path).update(copy.deepcopy(patch))
        elif op == 'remove':
            remove(working[owner[path]], path)
        else:
            target = change['to']; parts(target)
            if target in current and (target != path or filename == owner[path]):
                raise ValueError('Destino já existe/sem mudança: ' + target)
            token = copy.deepcopy(node(working[owner[path]], path))
            token.setdefault('$type', current[path][0])  # Preserva tipo herdado no destino.
            remove(working[owner[path]], path)
            put(working[filename], target, token)
            # Só aliases de $value, nunca descrições/metadata ou código consumidor.
            for tree in working.values():
                for token_path in index(tree):
                    leaf = node(tree, token_path)
                    leaf['$value'] = rewrite(leaf['$value'], path, target)
            moves.append({'from': path, 'to': target, 'file': filename})
    after, after_owners, graph_after, values_after, duplicates = validate(working)
    changes = []
    for path in sorted(set(before) | set(after)):
        old = node(sources[owners[path]], path) if path in before else None
        new = node(working[after_owners[path]], path) if path in after else None
        if old != new or owners.get(path) != after_owners.get(path) or before.get(path) != after.get(path):
            changes.append({'path': path, 'before_file': owners.get(path), 'after_file': after_owners.get(path),
                            'before': old, 'after': new})
    affected = {c['path'] for c in changes}
    while True:
        dependents = {path for graph in (graph_before, graph_after) for path, targets in graph.items() if affected & targets}
        if dependents <= affected:
            break
        affected |= dependents
    return {'phase': 'proposal', 'approval_required': True, 'files': working, 'changes': changes,
            'moves': moves, 'affected_tokens': sorted(affected),
            'baseline_validation': {'passed': baseline_error is None, 'error': baseline_error},
            'resolved_value_diffs': None if values_before is None else {path: {'before': values_before.get(path), 'after': values_after.get(path)} for path in sorted(set(values_before) | set(values_after)) if values_before.get(path) != values_after.get(path)},
            'resolved_value_changes': None if values_before is None else sorted(path for path in set(values_before) | set(values_after) if values_before.get(path) != values_after.get(path)),
            'equivalent_value_candidates': duplicates,
            'validation': 'passed_supported_subset',
            'limitations': 'Não persiste/aprova; valida subconjunto DTCG documentado. Impactos em consumidores são candidatos textuais, não análise de AST/runtime.'}


def impact(root, sources, affected, bindings, scopes):
    if not affected:
        return {'candidates': [], 'files_scanned': 0, 'skipped_files': 0, 'truncated': False, 'coverage': 'Nenhuma mudança de token proposta; busca não executada.'}
    terms = set(affected)
    for path in affected:
        terms.update(bindings.get(path, []))
    hits, scanned, skipped, truncated = [], 0, 0, False
    seen = set()
    def fail(error):
        raise error
    for scope in scopes or ['.']:
        base = root if scope == '.' else relative(root, scope)
        if not base.exists():
            raise ValueError('Escopo não encontrado: ' + scope)
        if base.is_file():
            files = iter([base])
        else:
            def walk():
                for directory, dirs, files in os.walk(base, followlinks=False, onerror=fail):
                    dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(directory) / d).is_symlink())
                    for filename in sorted(files):
                        yield Path(directory) / filename
            files = walk()
        for path in files:
            rel = path.relative_to(root).as_posix()
            if rel in seen or rel in sources or path.suffix not in TEXT or path.name.endswith(('lock.json', 'lock.yaml')):
                continue
            seen.add(rel)
            if path.is_symlink() or path.stat().st_size > 1024 * 1024:
                skipped += 1
                continue
            if scanned >= 5000 or len(hits) >= 200:
                truncated = True; break
            scanned += 1
            try:
                content = path.read_text(encoding='utf-8')
            except UnicodeError:
                skipped += 1; continue
            for line, value in enumerate(content.splitlines(), 1):
                found = sorted(term for term in terms if term in value)
                if found:
                    hits.append({'file': rel, 'line': line, 'terms': found})
                    if len(hits) >= 200:
                        truncated = True; break
        if truncated:
            break
    return {'candidates': hits, 'files_scanned': scanned, 'skipped_files': skipped, 'truncated': truncated,
            'coverage': 'Busca textual limitada; bindings gerados, acessos dinâmicos, symlinks e diretórios ignorados exigem investigação manual. Zero ocorrências não prova impacto zero.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['validate', 'preview'])
    parser.add_argument('project', type=Path)
    parser.add_argument('--source', action='append', help='Fonte JSON relativa ao projeto; repetível.')
    parser.add_argument('--decisions', default='design-system/decisions.json')
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--full', action='store_true', help='Incluir documentos completos na prévia.')
    parser.add_argument('--scan', action='append', help='Escopo de impacto relativo, repetível; padrão projeto.')
    args = parser.parse_args()
    try:
        root = args.project.resolve(strict=True)
        if not root.is_dir():
            raise ValueError('Projeto deve ser diretório.')
        filenames = args.source
        if not filenames:
            record = read(relative(root, args.decisions))
            filenames = [find_token_source(record.get('decisions', record), root)]
        if len(filenames) != len(set(filenames)):
            raise ValueError('Fonte repetida.')
        sources = {f: read(relative(root, f)) for f in filenames}
        if args.mode == 'validate':
            tokens, _, _, _, duplicates = validate(sources)
            result = {'validation': 'passed_supported_subset', 'token_count': len(tokens), 'equivalent_value_candidates': duplicates}
        else:
            if not args.plan:
                raise ValueError('preview exige --plan.')
            plan = read(args.plan)
            result = preview(sources, plan)
            result['consumer_impact'] = impact(root, sources, result['affected_tokens'], plan['bindings'], args.scan)
            if not args.full:
                del result['files']
                result['status'] = 'no_changes' if not result['changes'] else 'proposal_ready'
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError) as error:
        print('Erro: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
