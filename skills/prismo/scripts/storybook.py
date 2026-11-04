#!/usr/bin/env python3
"""Inspeção somente leitura para integração Storybook; não instala ou configura."""
import argparse
import json
import strict_json
from pathlib import Path
import sys


def inspect(project, config_dir=None, decisions='design-system/decisions.json', package_dir=None):
    root = Path(project).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Projeto deve ser um diretório existente.')
    def read(relative):
        path = root / relative
        if not path.is_file():
            return {}
        data = strict_json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('Objeto JSON esperado: ' + relative)
        return data
    def local(value):
        if (not isinstance(value, str) or not value or value.startswith('/') or '\\' in value or ':' in value
                or (value != '.' and any(part in {'', '.', '..'} for part in value.split('/')))):
            raise ValueError('Caminho relativo inválido: ' + str(value))
        path = root / value
        if not path.resolve().is_relative_to(root):
            raise ValueError('Caminho fora do projeto: ' + value)
        return path
    local(decisions)
    record = read(decisions)
    settings = record.get('decisions', record)
    if not isinstance(settings, dict) or not isinstance(settings.get('paths', {}), dict):
        raise ValueError('Registro de decisões/paths deve ser objeto.')
    docs = settings.get('paths', {}).get('documentation', {})
    if not isinstance(docs, dict):
        raise ValueError('paths.documentation deve ser objeto.')
    registered = docs.get('storybook')
    if registered is not None:
        local(registered)
    package_dir = package_dir if package_dir is not None else (registered or '.')
    config_dir = config_dir if config_dir is not None else str(Path(package_dir) / '.storybook') if package_dir != '.' else '.storybook'
    local(config_dir); package_root = local(package_dir)
    package = read(str(Path(package_dir) / 'package.json'))
    dependencies = {**package.get('dependencies', {}), **package.get('devDependencies', {})}
    frameworks = sorted(k for k in dependencies if k in {'react', 'vue', 'next', '@angular/core', 'svelte', 'astro', 'lit', 'vite'})
    declared = 'web' in settings.get('platforms', [])
    configs = [str(p.relative_to(root)) for p in sorted((root / config_dir).glob('main.*'))
               if p.suffix in {'.js', '.ts', '.mjs', '.cjs', '.mts'} and p.is_file()]
    tokens = settings.get('paths', {}).get('tokens')
    return {'status': 'inspection', 'web_declared': declared,
            'web_evidence': frameworks + (['index.html'] if (package_root / 'index.html').is_file() else []),
            'storybook_packages': {k: v for k, v in dependencies.items() if k == 'storybook' or k.startswith('@storybook/')},
            'storybook_configs': configs, 'configured': bool(configs),
            'token_source': tokens, 'decisions_found': (root / decisions).is_file(),
            'next': ('review_existing_config_and_renderer' if configs else
                     'approval_required_before_install_or_configuration') if (declared or frameworks or (package_root / 'index.html').is_file()) else
                    ('not_applicable_to_declared_platforms' if settings.get('platforms') else 'clarify_web_scope_before_integration'),
            'package_dir': package_dir, 'config_dir': config_dir, 'registered_storybook': registered, 'limitations': 'Inspeção do manifesto selecionado; configuração não executada.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project')
    parser.add_argument('--config-dir', help='Configuração relativa ao projeto; padrão no diretório Storybook registrado.')
    parser.add_argument('--decisions', default='design-system/decisions.json')
    parser.add_argument('--package-dir', help='Diretório do manifesto do catálogo relativo ao projeto.')
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.project, args.config_dir, args.decisions, args.package_dir), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print(f'Erro: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
