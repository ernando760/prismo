#!/usr/bin/env python3
"""Materializa um plano de init; preview por padrão, sem instalar dependências."""
import argparse
import json
import strict_json
from naming import policy
from pathlib import Path, PurePosixPath
import sys


PLATFORMS = {'web', 'flutter', 'marketing'}


def text(value):
    return isinstance(value, str) and bool(value.strip())


def validate(plan):
    if not isinstance(plan, dict):
        raise ValueError('Plano deve ser um objeto JSON.')
    required = {'name', 'platforms', 'identity', 'accessibility', 'documentation',
                'evidence', 'reuse', 'pending', 'paths'}
    if set(plan) - {'naming'} != required:
        raise ValueError('Campos esperados: ' + ', '.join(sorted(required)))
    if not all(text(plan[key]) for key in ('name', 'identity', 'accessibility')):
        raise ValueError('Nome, identidade e acessibilidade precisam de decisões explícitas.')
    platforms = plan['platforms']
    if (not isinstance(platforms, list) or not platforms
            or any(not isinstance(p, str) or p not in PLATFORMS for p in platforms)
            or len(set(platforms)) != len(platforms)):
        raise ValueError('Escolha plataformas únicas: web, flutter, marketing.')
    docs = plan['documentation']
    if (not isinstance(docs, dict) or 'central' not in docs
            or any(k not in {'central', *platforms} or not text(v) for k, v in docs.items())
            or any(p not in docs for p in platforms)):
        raise ValueError('Documentação exige central e cada plataforma (pode ser adiada).')
    for key in ('evidence', 'reuse', 'pending'):
        if not isinstance(plan[key], list) or not all(text(v) for v in plan[key]):
            raise ValueError(f'{key} deve ser lista de textos.')
    if 'naming' in plan:
        policy(plan['naming'])
    paths = plan['paths']
    if (not isinstance(paths, dict) or not {'decisions', 'tokens', 'components'} <= set(paths)
            or set(paths) - {'decisions', 'tokens', 'components', 'tokens_existing', 'packages', 'documentation'}):
        raise ValueError('paths exige decisions, tokens e components.')
    packages = paths.get('packages', {})
    docs_paths = paths.get('documentation', {})
    if (not isinstance(packages, dict) or any(k not in platforms or not isinstance(v, list) or not v or
            any(not text(p) for p in v) or len(set(v)) != len(v) for k, v in packages.items())):
        raise ValueError('packages exige listas de caminhos por plataforma selecionada.')
    if not isinstance(docs_paths, dict) or any(k not in {'docusaurus', 'storybook', 'widgetbook'} or not text(v) for k, v in docs_paths.items()):
        raise ValueError('documentation exige caminhos por ferramenta.')
    for value in [p for values in packages.values() for p in values] + list(docs_paths.values()):
        if value != '.' and (value.startswith('/') or '\\' in value or ':' in value or any(p in {'', '.', '..'} for p in value.split('/'))):
            raise ValueError(f'Caminho relativo inválido: {value!r}')
    if (not isinstance(paths['components'], dict) or any(p not in platforms or not text(v)
            for p, v in paths['components'].items())):
        raise ValueError('Raízes de componentes devem pertencer às plataformas escolhidas.')


def destination(root, relative, existing_directory=False):
    if (not text(relative) or '\\' in relative or ':' in relative
            or relative.startswith('/') or any(p in {'', '.', '..'} for p in relative.split('/'))):
        raise ValueError(f'Caminho relativo inválido: {relative!r}')
    path = root.joinpath(*PurePosixPath(relative).parts)
    for part in [path, *path.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise ValueError(f'Symlink no destino: {relative}')
        if part != path and part.exists() and not part.is_dir():
            raise ValueError(f'Pai não é diretório: {relative}')
    if path.exists() and not (existing_directory and path.is_dir()):
        raise ValueError(f'Destino já existe; reutilize ou escolha outro: {relative}')
    return path


def prepare(root, plan):
    validate(plan)
    paths = plan['paths']
    existing = paths.get('tokens_existing')
    if existing is not None:
        if paths['tokens'] is not None:
            raise ValueError('Escolha tokens ou tokens_existing, não ambos.')
        if (not text(existing) or Path(existing).is_absolute() or '..' in Path(existing).parts
                or not (root / existing).is_file() or not (root / existing).resolve().is_relative_to(root)
                or any(part.is_symlink() for part in (root / existing, *(root / existing).parents) if part != root and root in part.parents)):
            raise ValueError('tokens_existing deve ser arquivo relativo existente.')
    for value in [p for values in paths.get('packages', {}).values() for p in values] + list(paths.get('documentation', {}).values()):
        path = root if value == '.' else root / value
        if not path.resolve().is_relative_to(root):
            raise ValueError(f'Caminho fora do projeto: {value}')
    relatives = [paths['decisions'], *paths['components'].values()]
    if paths['tokens'] is not None:
        relatives.append(paths['tokens'])
    component_paths = set(paths['components'].values())
    targets = [destination(root, p, existing_directory=p in component_paths and p not in {paths['decisions'], paths['tokens']}) for p in relatives]
    for i, path in enumerate(targets):
        for other in targets[i + 1:]:
            if path == other or path in other.parents or other in path.parents:
                raise ValueError('Destinos sobrepostos no plano.')
    record_plan = strict_json.loads(json.dumps(plan))
    if existing is not None:
        record_plan['paths']['tokens'] = existing
        del record_plan['paths']['tokens_existing']
    record = {'prismo_version': 1, 'operation': 'init', 'decisions': record_plan}
    files = {}
    if paths['tokens'] is not None:
        files[paths['tokens']] = '{}\n'
    files[paths['decisions']] = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    directories = []
    return files, directories


def apply(root, files, directories):
    created_files, created_dirs = [], []

    def mkdir(path):
        if path == root:
            return
        # Revalide os pais; jamais atravesse links nem reutilize um arquivo como pasta.
        if path.is_symlink():
            raise ValueError(f'Symlink no destino: {path}')
        if path.exists():
            if not path.is_dir():
                raise ValueError(f'Pai inválido: {path}')
            return
        mkdir(path.parent)
        path.mkdir()
        created_dirs.append(path)

    try:
        for relative in directories:
            mkdir(root / relative)
        for relative, content in files.items():
            path = root / relative
            mkdir(path.parent)
            with path.open('x', encoding='utf-8') as stream:
                created_files.append(path)
                stream.write(content)
        for relative, content in files.items():
            if (root / relative).read_text(encoding='utf-8') != content:
                raise ValueError(f'Verificação falhou: {relative}')
    except Exception:
        for path in reversed(created_files):
            path.unlink()
        for path in reversed(created_dirs):
            path.rmdir()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--apply', action='store_true', help='Usar somente após aprovação do usuário.')
    args = parser.parse_args()
    try:
        root = args.project.resolve(strict=True)
        if not root.is_dir():
            raise ValueError('Projeto deve ser um diretório existente.')
        plan = strict_json.loads(args.plan.read_text(encoding='utf-8'))
        files, directories = prepare(root, plan)
        if args.apply:
            apply(root, files, directories)
        print(json.dumps({'status': 'created' if args.apply else 'preview',
                          'files': files, 'directories': directories}, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        print(f'Erro: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
