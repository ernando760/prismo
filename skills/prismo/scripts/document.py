#!/usr/bin/env python3
"""Inventário limitado em leitura para document; não configura portal nem aprova alterações."""
import argparse
import json
import strict_json
import os
from pathlib import Path
import sys

SKIP = {'.git', '.agents', '.codex', 'node_modules', '.venv', 'venv', '__pycache__',
        'build', 'dist', '.docusaurus', 'coverage', '.dart_tool', 'vendor'}
CONFIGS = {'docusaurus.config.' + ext for ext in ('js', 'ts', 'mjs', 'cjs', 'mts', 'cts')}
LIMIT = 5000
DISPLAY = 50


def relative(root, value):
    if not value or '\\' in value or ':' in value or any(p in ('', '.', '..') for p in value.split('/')):
        raise ValueError('Caminho relativo inválido: ' + value)
    path = root / value
    if not path.resolve().is_relative_to(root):
        raise ValueError('Fonte fora do projeto: ' + value)
    return path


def read_object(path):
    data = strict_json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Objeto JSON esperado: ' + str(path))
    return data


def inventory(project, decisions='design-system/decisions.json', limit=LIMIT):
    root = Path(project).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Projeto deve ser um diretório.')
    record_path = relative(root, decisions)
    record = read_object(record_path) if record_path.is_file() else None
    settings = record.get('decisions', record) if record is not None else {}
    if not isinstance(settings, dict) or not isinstance(settings.get('paths', {}), dict):
        raise ValueError('Registro de decisões/paths deve ser objeto.')
    source = settings.get('paths', {}).get('tokens')
    if source is not None and not isinstance(source, str):
        raise ValueError('Caminho de tokens deve ser texto.')
    token_path = relative(root, source) if source is not None else None
    documentation = settings.get('paths', {}).get('documentation', {})
    if not isinstance(documentation, dict):
        raise ValueError('paths.documentation deve ser objeto.')
    declared_docs = {}
    for tool, location in documentation.items():
        if tool not in {'docusaurus', 'storybook', 'widgetbook'} or not isinstance(location, str):
            raise ValueError('Ferramenta ou caminho de documentação inválido.')
        path = root if location == '.' else relative(root, location)
        declared_docs[tool] = {'path': location, 'exists': path.is_dir()}
    groups = {k: [] for k in ('portal_configs', 'portal_packages', 'docs', 'token_candidates',
                              'component_candidates', 'catalogs', 'identity_assets')}
    scanned, truncated, skipped_links = 0, False, 0
    def fail(error):
        raise error
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=fail):
        base = Path(directory)
        skipped_links += sum((base / d).is_symlink() for d in dirs)
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not (base / d).is_symlink())
        for filename in sorted(files):
            path = base / filename
            if path.is_symlink():
                skipped_links += 1
                continue
            if scanned >= limit:
                truncated = True
                break
            scanned += 1
            rel = path.relative_to(root).as_posix()
            lower = filename.lower()
            if filename in CONFIGS:
                groups['portal_configs'].append(rel)
            if filename == 'package.json':
                package = read_object(path)
                deps = {**package.get('dependencies', {}), **package.get('devDependencies', {})}
                if '@docusaurus/core' in deps:
                    groups['portal_packages'].append({'manifest': rel, 'version': deps['@docusaurus/core']})
            if path.suffix.lower() in ('.md', '.mdx'):
                groups['docs'].append(rel)
            if lower == 'tokens.json' or lower.endswith('.tokens.json') or (source and rel == source):
                groups['token_candidates'].append(rel)
            if path.suffix.lower() in ('.tsx', '.jsx', '.vue', '.svelte', '.dart') and not any(s in lower for s in ('.test.', '.spec.', '.stories.', '.g.')):
                groups['component_candidates'].append(rel)
            if (base.name == '.storybook' and filename.startswith('main.')) or '.stories.' in filename or 'widgetbook' in lower or 'use_case' in lower:
                groups['catalogs'].append(rel)
            if path.suffix.lower() in ('.svg', '.png', '.jpg', '.webp', '.pdf') and any(s in rel.lower() for s in ('brand', 'logo', 'identity', 'marca')):
                groups['identity_assets'].append(rel)
        if truncated:
            break
    notes = []
    if record is None:
        notes.append('Registro não encontrado no caminho informado; investigar outras fontes aprovadas.')
    if token_path is None or not token_path.is_file():
        notes.append('Fonte DTCG declarada não localizada; investigar candidatos conforme o assunto.')
    if not groups['portal_configs'] or not groups['portal_packages']:
        notes.append('Portal não confirmado: investigar configuração/dependências; propor setup se ausente.')
    if len(groups['portal_configs']) > 1:
        notes.append('Múltiplos portais candidatos; selecionar pacote antes da proposta.')
    if truncated or skipped_links:
        notes.append('Inventário parcial; limites/symlinks não comprovam ausência de fontes.')
    return {
        'phase': 'investigation', 'decisions': decisions if record is not None else None,
        'declared_documentation': declared_docs,
        'declared_token_source': source,
        'declared_token_source_exists': bool(token_path and token_path.is_file()),
        'sources': {key: values[:DISPLAY] for key, values in groups.items()},
        'counts': {key: len(values) for key, values in groups.items()},
        'scan': {'files': scanned, 'limit': limit, 'truncated': truncated,
                 'symlinks_skipped': skipped_links, 'display_limit': DISPLAY},
        'attention': notes,
        'approval_required': ['documentation_proposal', 'portal_setup_if_needed'],
        'limitations': 'Candidatos, não análise de API/DTCG, configuração executada, links publicados ou portal validado. Nenhuma escrita, instalação ou aprovação.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project')
    parser.add_argument('--decisions', default='design-system/decisions.json')
    args = parser.parse_args()
    try:
        print(json.dumps(inventory(args.project, args.decisions), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as error:
        print('Erro: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
