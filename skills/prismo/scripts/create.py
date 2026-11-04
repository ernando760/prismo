#!/usr/bin/env python3
"""Revisa proposta create em leitura. Não gera componentes, executa checks ou aprova mudanças."""
import argparse
import copy
import json
import strict_json
from pathlib import Path
import re
import sys

from token_source import token_source as find_token_source
from spacing import alias, index, name
from borders import insert

ROLES = {'component', 'catalog', 'test', 'documentation', 'tokens', 'exports'}
KINDS = {'functional', 'accessibility', 'build', 'pack', 'exports', 'types', 'css', 'nodenext', 'bundler'}
ATOMIC = {'atom', 'molecule', 'organism', 'template', 'page'}


def text(value):
    return isinstance(value, str) and bool(value.strip())


def relative(root, value, writing=False):
    if not text(value) or '\\' in value or ':' in value or value.startswith('/') or any(p in ('', '.', '..') for p in value.split('/')):
        raise ValueError('Caminho relativo inválido: ' + str(value))
    path = root / value
    if writing:
        for part in (path, *path.parents):
            if part == root:
                break
            if part.is_symlink():
                raise ValueError('Symlink em caminho de escrita: ' + value)
            if part != path and part.exists() and not part.is_dir():
                raise ValueError('Pai não é diretório: ' + value)
    return path


def read_json(path):
    result = strict_json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(result, dict):
        raise ValueError('Objeto JSON esperado: ' + str(path))
    return result


def references(value):
    if alias(value):
        yield value[1:-1]
    elif isinstance(value, dict):
        for child in value.values():
            yield from references(child)
    elif isinstance(value, list):
        for child in value:
            yield from references(child)


def review(project, plan, decisions='design-system/decisions.json', package_dir=None):
    root = Path(project).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Projeto deve ser um diretório existente.')
    fields = {'name', 'platform', 'atomic', 'tokens', 'new_tokens', 'files', 'states', 'cases', 'checks', 'catalog', 'questions'}
    if not isinstance(plan, dict) or set(plan) - {'distribution'} != fields or not text(plan['name']):
        raise ValueError('Plano exige nome e campos: ' + ', '.join(sorted(fields)))
    for field in ('new_tokens', 'files', 'states', 'cases', 'checks', 'questions'):
        if not isinstance(plan[field], list):
            raise ValueError(field + ' deve ser lista.')
    if not isinstance(plan['tokens'], dict) or not isinstance(plan['catalog'], dict):
        raise ValueError('tokens e catalog devem ser objetos.')
    if not all(text(item) for item in plan['questions']):
        raise ValueError('questions deve conter perguntas textuais.')
    json.dumps(plan, allow_nan=False)  # Recusa NaN/Infinity em propostas JSON.
    issues = list(plan['questions'])
    approvals = ['component_proposal']
    warnings = []
    record_path = relative(root, decisions)
    record = read_json(record_path) if record_path.is_file() else {}
    if not record:
        issues.append('Registro de decisões ausente; localizar antes de implementar.')
    settings = record.get('decisions', record)
    packages = settings.get('paths', {}).get('packages', {}).get(plan['platform'], [])
    if package_dir is None and len(packages) == 1:
        package_dir = packages[0]
    elif package_dir is None and len(packages) > 1:
        issues.append('Selecionar pacote explicitamente; há múltiplos candidatos.')
        package_dir = '.'
    package_dir = package_dir or '.'
    package_root = root if package_dir == '.' else relative(root, package_dir)
    if not package_root.resolve().is_relative_to(root):
        raise ValueError('Pacote fora do projeto.')
    package_path = package_root / 'package.json'
    package = read_json(package_path) if package_path.is_file() else {}
    deps = {**package.get('dependencies', {}), **package.get('devDependencies', {})}
    web = sorted(k for k in deps if k in {'react', 'vue', 'next', '@angular/core', 'svelte', 'astro', 'lit', '@storybook/html-vite', '@storybook/web-components-vite'})
    if (package_root / 'index.html').is_file():
        web.append('html')
    pubspec = package_root / 'pubspec.yaml'
    flutter = pubspec.is_file() and bool(re.search(r'^\s*sdk:\s*flutter\s*(?:#.*)?$', pubspec.read_text(encoding='utf-8'), re.M))
    observed = (['web'] if web else []) + (['flutter'] if flutter else [])
    platform = plan['platform']
    if platform is None and len(observed) == 1:
        platform = observed[0]
    if platform not in ('web', 'flutter'):
        issues.append('Selecionar uma plataforma Web ou Flutter para esta implementação.')
    elif platform not in observed:
        issues.append('Tecnologia da plataforma não identificada no pacote selecionado; investigar pacote/framework sem escolher automaticamente.')
    declared = settings.get('platforms', [])
    if declared and platform in ('web', 'flutter') and platform not in declared:
        issues.append('Plataforma diverge das decisões existentes; esclarecer o escopo.')
    if plan['atomic'] not in ATOMIC:
        issues.append('Definir classificação Atomic Design e justificar na proposta.')

    token_source = find_token_source(settings, root)
    tree = {}
    if token_source:
        token_path = relative(root, token_source)
        if token_path.is_file():
            tree = read_json(token_path)
        else:
            issues.append('Fonte de tokens declarada não encontrada: ' + token_source)
    else:
        issues.append('Localizar a fonte DTCG e seu binding Web/Dart antes de implementar.')
    working = copy.deepcopy(tree)
    tokens = index(working)
    for proposal in plan['new_tokens']:
        if not isinstance(proposal, dict) or set(proposal) != {'path', 'token', 'reason'} or not text(proposal['reason']):
            raise ValueError('Novo token exige path, token DTCG e reason explícito.')
        path, token = proposal['path'], proposal['token']
        if not text(path):
            raise ValueError('Caminho do token inválido.')
        for part in path.split('.'):
            if part != '$root':
                name(part)
        if not isinstance(token, dict) or not text(token.get('$type')) or '$value' not in token:
            raise ValueError('Token proposto exige $type e $value; helper não é validador DTCG completo.')
        try:
            insert(working, path, token['$type'], token['$value'])
        except ValueError as error:
            issues.append(str(error))
    tokens = index(working)
    if plan['new_tokens']:
        approvals.append('token_changes')
    seen = set()
    def walk(path, stack=()):
        if path in stack:
            raise ValueError('Alias circular: ' + path)
        if path not in tokens:
            raise ValueError('Token não encontrado: ' + path)
        if path in seen:
            return
        kind, value = tokens[path]
        if not text(kind):
            raise ValueError('Token sem tipo efetivo: ' + path)
        if alias(value) and value[1:-1] in tokens and tokens[value[1:-1]][0] != kind:
            raise ValueError('Tipos incompatíveis no alias: ' + path)
        for target in references(value):
            walk(target, (*stack, path))
        seen.add(path)
    used = []
    for role, binding in plan['tokens'].items():
        if not text(role) or not isinstance(binding, dict) or set(binding) != {'path', 'binding'} or not all(text(v) for v in binding.values()):
            raise ValueError('Binding exige path DTCG e binding de código não vazios.')
        used.append(binding['path'])
    for path in used:
        try:
            walk(path)
        except ValueError as error:
            issues.append(str(error))

    bound = set(seen)
    for proposal in plan['new_tokens']:
        if proposal['path'] not in bound:
            issues.append('Novo token sem binding/uso no componente: ' + proposal['path'])
        try:
            walk(proposal['path'])
        except ValueError as error:
            issues.append(str(error))

    files, roles = [], set()
    for item in plan['files']:
        if not isinstance(item, dict) or set(item) != {'path', 'action', 'role'} or item['action'] not in ('create', 'modify') or item['role'] not in ROLES:
            raise ValueError('Arquivo exige path, action create/modify e role suportado.')
        path = relative(root, item['path'], writing=True)
        if item['role'] in {'component', 'exports'} and package_dir != '.' and not path.is_relative_to(package_root):
            issues.append('Componente ou export fora do pacote selecionado: ' + item['path'])
        if item['path'] in files:
            issues.append('Arquivo repetido: ' + item['path'])
        files.append(item['path']); roles.add(item['role'])
        if item['action'] == 'create' and path.exists():
            issues.append('Destino já existe; reutilizar ou propor diff: ' + item['path'])
        elif item['action'] == 'modify':
            approvals.append('modify:' + item['path'])
            if not path.is_file():
                issues.append('Arquivo a modificar não existe: ' + item['path'])
        if path.is_dir():
            issues.append('Destino é diretório: ' + item['path'])
    for i, path in enumerate(files):
        for other in files[i + 1:]:
            if path in (str(p) for p in Path(other).parents) or other in (str(p) for p in Path(path).parents):
                issues.append('Destinos sobrepostos no plano: ' + path + ' / ' + other)
    for role in ('component', 'catalog', 'test', 'documentation'):
        if role not in roles:
            issues.append('Planejar arquivo com finalidade: ' + role)
    if plan['new_tokens'] and 'tokens' not in roles:
        issues.append('Novos tokens exigem diff de arquivo de tokens na proposta.')

    states = plan['states']
    if not states or not all(text(v) for v in states) or len(set(states)) != len(states):
        issues.append('Estados devem ser explícitos, não vazios e únicos.')
    covered = set()
    for case in plan['cases']:
        if not isinstance(case, dict) or set(case) != {'name', 'states', 'assertions'} or not text(case['name']) or not isinstance(case['states'], list) or not isinstance(case['assertions'], list) or not case['assertions'] or not all(text(v) for v in case['assertions']):
            raise ValueError('Caso exige name, states e assertions verificáveis.')
        if not case['states'] or any(v not in states for v in case['states']):
            issues.append('Caso sem estado válido ou com estado não declarado: ' + case['name'])
        covered.update(case['states'])
    if any(state not in covered for state in states):
        issues.append('Faltam casos para estados: ' + ', '.join(s for s in states if s not in covered))
    kinds = set()
    for check in plan['checks']:
        if not isinstance(check, dict) or set(check) != {'kind', 'command'} or check['kind'] not in KINDS or not text(check['command']):
            raise ValueError('Check exige kind suportado (' + ', '.join(sorted(KINDS)) + ') e command.')
        kinds.add(check['kind'])
    if not {'functional', 'accessibility'} <= kinds:
        issues.append('Planejar verificações funcionais e de acessibilidade.')
    distribution = plan.get('distribution')
    required_checks = set()
    if 'distribution' in plan:
        if (not isinstance(distribution, dict) or set(distribution) != {'typescript', 'css', 'resolutions'}
                or not isinstance(distribution['typescript'], bool) or not isinstance(distribution['css'], bool)
                or not isinstance(distribution['resolutions'], list)
                or any(v not in ('NodeNext', 'Bundler') for v in distribution['resolutions'])
                or len(set(distribution['resolutions'])) != len(distribution['resolutions'])):
            raise ValueError('distribution exige typescript/css booleanos e resolutions únicas NodeNext/Bundler.')
        if platform != 'web':
            raise ValueError('distribution descreve somente pacotes Web.')
        if distribution['resolutions'] and not distribution['typescript']:
            raise ValueError('Resoluções TypeScript exigem typescript: true.')
        required_checks = {'build', 'pack', 'exports'}
        if distribution['typescript']:
            required_checks.add('types')
        if distribution['css']:
            required_checks.add('css')
        required_checks.update(v.lower() for v in distribution['resolutions'])
        missing = required_checks - kinds
        if missing:
            issues.append('Planejar validação do pacote distribuível: ' + ', '.join(sorted(missing)))
    elif platform == 'web' and any(k in package for k in ('exports', 'main', 'module', 'types', 'typings')):
        warnings.append('Pacote com entradas públicas: declarar distribution e planejar consumo do tarball; build do catálogo não valida distribuição.')
    catalog = plan['catalog']
    if set(catalog) != {'tool', 'config'}:
        raise ValueError('catalog exige tool e config (caminho ou null).')
    docs = settings.get('paths', {}).get('documentation', {})
    if not isinstance(docs, dict):
        raise ValueError('paths.documentation deve ser objeto.')
    expected = {'web': 'storybook', 'flutter': 'widgetbook'}.get(platform)
    catalog_root = docs.get(expected) if expected else None
    if catalog_root is not None:
        if not (root if catalog_root == '.' else relative(root, catalog_root)).resolve().is_relative_to(root):
            raise ValueError('Catálogo fora do projeto.')
    if expected and catalog['tool'] != expected:
        issues.append('Catálogo incompatível com a plataforma: esperado ' + expected)
    config = relative(root, catalog['config']) if catalog['config'] is not None else None
    found = bool(config and config.is_file())
    if catalog_root and config and not config.is_relative_to(root / catalog_root):
        message = 'Configuração fora do diretório de catálogo registrado; investigar divergência antes de propor instalação.'
        (warnings if found else issues).append(message)
    if not found:
        approvals.append('catalog_setup')
        warnings.append('Configuração de catálogo ausente; apresentar dependências/arquivos e obter aprovação antes de instalar/configurar.')
    return {'status': 'proposal_ready' if not issues else 'needs_input', 'phase': 'proposal',
            'platform': platform, 'package_dir': package_dir, 'architecture_evidence': {'web': web, 'flutter': flutter},
            'atomic': plan['atomic'], 'token_source': token_source, 'checked_token_paths': sorted(seen),
            'distribution': {'contract': distribution, 'required_checks': sorted(required_checks), 'validation': 'not_run'},
            'files': plan['files'], 'catalog_directory': catalog_root, 'catalog_configuration_found': found,
            'approval_required': approvals, 'issues': issues, 'warnings': warnings,
            'limitations': 'Somente revisão de plano: não aprova, escreve, executa comandos ou comprova API, comportamento, acessibilidade ou validade DTCG completa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project')
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--decisions', default='design-system/decisions.json')
    parser.add_argument('--package-dir', help='Raiz do pacote relativa ao projeto; . para a raiz.')
    args = parser.parse_args()
    try:
        result = review(args.project, read_json(args.plan), args.decisions, args.package_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0 if result['status'] == 'proposal_ready' else 2
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print(f'Erro: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
