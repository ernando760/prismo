#!/usr/bin/env python3
"""Auditoria em leitura: tokens, pares declarados e indícios textuais. Saída somente stdout."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
from itertools import islice
import os
from pathlib import Path
import re

from token_source import token_source as find_token_source
from token_errors import UnsupportedTokenFormat
from tokens import read, relative, validate, SKIP, TEXT
from colors import contrast, evaluate

STYLE = re.compile(r'(?:color|background(?:-color|Color)?|border(?:-radius|-width|-color|Radius|Width|Color)?|font(?:-size|Size)|line(?:-height|Height)|letter(?:-spacing|Spacing)|padding|margin|gap|box-shadow)\s*:\s*([^;{}\n]+)', re.I)
LITERAL = re.compile(r'#[0-9a-f]{3,8}\b|(?<![\w.-])(?:[1-9]\d*(?:\.\d+)?|0\.\d*[1-9]\d*)(?:px|rem)\b|\b(?:rgb|hsl)a?\(', re.I)
DART_LITERAL = re.compile(r'Color\(\s*0x[0-9a-f]{8}\s*\)|(?:EdgeInsets\.all|Radius\.circular|BorderRadius\.circular)\(\s*[1-9]\d*(?:\.\d+)?\s*\)', re.I)
SOURCE = {'.css', '.scss', '.sass', '.less', '.jsx', '.tsx', '.vue', '.svelte', '.js', '.ts', '.dart'}
AUDIT_SKIP = SKIP | {'.cache', '.turbo', '.nuxt', '.output', '.svelte-kit', '.vercel',
                     '.angular', '.pytest_cache', 'storybook-static'}
GENERATED_SUFFIXES = ('.min.js', '.min.css', '.g.dart', '.freezed.dart')


def scan(root, scopes, limit=5000, excludes=None):
    files, seen, skipped, truncated = {}, set(), 0, False
    if not isinstance(excludes, (list, type(None))) or (excludes and not all(isinstance(p, str) for p in excludes)):
        raise ValueError('Exclusões devem ser lista de caminhos relativos.')
    exclusions = []
    for value in excludes or []:
        if any(c in value for c in '*?[]'):
            raise ValueError('Exclusão exige caminho literal, sem glob: ' + value)
        exclusions.append(relative(root, value))
    def excluded(path):
        rel = path.relative_to(root)
        directories = rel.parts if path.is_dir() else rel.parts[:-1]
        return (any(part in AUDIT_SKIP for part in directories)
                or path.name.endswith(GENERATED_SUFFIXES)
                or any(path == base or path.is_relative_to(base) for base in exclusions))
    def fail(error):
        raise error
    for scope in scopes or ['.']:
        base = root if scope == '.' else relative(root, scope)
        if not base.exists():
            raise ValueError('Escopo não encontrado: ' + scope)
        if excluded(base):
            skipped += 1
            continue
        def walk():
            nonlocal skipped
            if base.is_file():
                yield base
                return
            for directory, dirs, names in os.walk(base, followlinks=False, onerror=fail):
                kept = []
                for d in sorted(dirs):
                    child = Path(directory) / d
                    if child.is_symlink() or excluded(child):
                        skipped += 1
                    else:
                        kept.append(d)
                dirs[:] = kept
                for name in sorted(names):
                    yield Path(directory) / name
        for path in walk():
            rel = path.relative_to(root).as_posix()
            if excluded(path):
                skipped += 1
                continue
            if rel in seen or path.suffix not in TEXT or path.name.endswith(('lock.json', 'lock.yaml')):
                continue
            seen.add(rel)
            if path.is_symlink() or path.stat().st_size > 1024 * 1024:
                skipped += 1; continue
            if len(files) >= limit:
                truncated = True; break
            try:
                files[rel] = path.read_text(encoding='utf-8')
            except UnicodeError:
                skipped += 1
        if truncated:
            break
    return files, {'files_read': len(files), 'limit': limit, 'skipped': skipped, 'truncated': truncated,
                   'scope': scopes or ['.'], 'exclusions': excludes or [],
                   'ignored_directories': sorted(AUDIT_SKIP), 'ignored_suffixes': list(GENERATED_SUFFIXES),
                   'limits': 'Texto UTF-8 até 1 MiB/arquivo; dependências, builds, gerados conhecidos e symlinks ignorados. skipped conta entradas/subárvores, não todos os descendentes. Sem AST/runtime.'}


def config_checked(config):
    if not isinstance(config, dict) or set(config) != {'contrast_pairs', 'bindings', 'components'}:
        raise ValueError('Config exige contrast_pairs, bindings e components.')
    if not isinstance(config['contrast_pairs'], list) or not isinstance(config['components'], list) or not isinstance(config['bindings'], dict):
        raise ValueError('Pares/componentes devem ser listas; bindings deve ser mapa.')
    for path, bindings in config['bindings'].items():
        if not isinstance(path, str) or not isinstance(bindings, list) or not all(isinstance(b, str) and b.strip() for b in bindings):
            raise ValueError('Binding exige caminho e lista textual.')
    for pair in config['contrast_pairs']:
        if not isinstance(pair, dict) or set(pair) != {'foreground', 'background', 'usage', 'evidence'} or pair['usage'] not in ('normal_text', 'large_text', 'non_text'):
            raise ValueError('Par exige foreground/background, usage e evidence.')
        if not all(isinstance(pair[k], str) and pair[k] for k in ('foreground', 'background')):
            raise ValueError('Caminhos de cor devem ser textuais.')
        ev = pair['evidence']
        if not isinstance(ev, dict) or set(ev) != {'file', 'line', 'text'} or isinstance(ev['line'], bool) or not isinstance(ev['line'], int) or ev['line'] < 1 or not isinstance(ev['text'], str) or not ev['text'].strip():
            raise ValueError('Evidence exige file, line positiva e text não vazio.')
    for component in config['components']:
        roles = {'implementation', 'documentation', 'catalog'}
        if not isinstance(component, dict) or set(component) != {'name', *roles, 'expectations'} or not isinstance(component['name'], str) or not component['name'].strip() or not isinstance(component['expectations'], list):
            raise ValueError('Componente exige name, implementation/documentation/catalog e expectations.')
        for role in roles:
            if component[role] is not None and not isinstance(component[role], str):
                raise ValueError('Artefato deve ser caminho ou null.')
        for item in component['expectations']:
            if not isinstance(item, dict) or set(item) != {'name', *roles} or not isinstance(item['name'], str) or not item['name'].strip() or any(item[r] is not None and (not isinstance(item[r], str) or not item[r].strip()) for r in roles):
                raise ValueError('Expectativa exige name e literais por papel ou null.')
    return config


def audit(project, config=None, sources=None, decisions='design-system/decisions.json', scopes=None, scan_limit=5000, excludes=None):
    root = Path(project).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Projeto deve ser diretório.')
    config = config_checked(config if config is not None else {'contrast_pairs': [], 'bindings': {}, 'components': []})
    # Valida todos os caminhos antes de processar evidências, sem seguir symlinks.
    for pair in config['contrast_pairs']:
        relative(root, pair['evidence']['file'])
    for component in config['components']:
        for role in ('implementation', 'documentation', 'catalog'):
            if component[role] is not None:
                relative(root, component[role])
    files, coverage = scan(root, scopes, scan_limit, excludes)
    findings, counts, omitted = [], {'confirmed': 0, 'risk': 0, 'manual': 0}, 0
    order = {'high': 0, 'medium': 1, 'low': 2}
    def rank(item):
        return (order[item['severity']], item['certainty'], item['code'])
    def add(code, severity, certainty, title, evidence, recommendation):
        nonlocal omitted
        counts[certainty] += 1
        item = {'code': code, 'severity': severity, 'certainty': certainty, 'title': title,
                'evidence': evidence, 'recommendation': recommendation}
        findings.append(item)
        if len(findings) > 100:
            findings.sort(key=rank); findings.pop(); omitted += 1
    record_path = relative(root, decisions)
    record = None
    if record_path.is_file():
        try:
            record = read(record_path)
        except (OSError, ValueError) as error:
            add('DECISIONS_JSON', 'medium', 'confirmed' if isinstance(error, ValueError) else 'manual', 'Registro não pôde ser lido', {'file': decisions, 'error': str(error)}, 'Corrigir o registro em tarefa separada; nenhuma correção executada.')
    else:
        add('DECISIONS_UNKNOWN', 'low', 'manual', 'Registro não localizado no caminho consultado', {'file': decisions}, 'Localizar decisões aprovadas; ausência aqui não prova ausência no projeto.')
    if sources is None:
        settings = record.get('decisions', record) if record else {}
        paths = settings.get('paths', {}) if isinstance(settings, dict) else {}
        source = find_token_source(settings, root) if isinstance(paths, dict) else None
        sources = [source] if source else []
    if not isinstance(sources, list) or len(set(sources)) != len(sources):
        raise ValueError('Fontes devem ser lista sem repetição.')
    trees, token_status, token_count, token_index, resolved = {}, 'not_run', None, {}, {}
    for filename in sources:
        path = relative(root, filename)
        try:
            trees[filename] = read(path)
        except (OSError, ValueError) as error:
            add('TOKEN_SOURCE', 'high', 'confirmed' if isinstance(error, ValueError) else 'manual', 'Fonte DTCG não pôde ser lida', {'file': filename, 'error': str(error)}, 'Revisar caminho/permissões/JSON da fonte; validação do conjunto ficou bloqueada.')
    if sources and len(trees) == len(sources):
        try:
            token_index, owners, _, resolved, duplicates = validate(trees)
            token_count, token_status = len(token_index), 'passed_supported_subset'
            if duplicates:
                add('TOKEN_EQUIVALENT', 'low', 'risk', 'Valores equivalentes para revisão de finalidade',
                    {'count': len(duplicates), 'examples': [{'tokens': pair, 'files': [owners[p] for p in pair]} for pair in duplicates[:5]]},
                    'Verificar papéis antes de consolidar; valores iguais não comprovam duplicação desnecessária.')
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            message = str(error)
            unsupported = isinstance(error, UnsupportedTokenFormat)
            token_status = 'blocked' if unsupported else 'failed'
            add('TOKEN_UNSUPPORTED' if unsupported else 'TOKEN_INVALID', 'medium' if unsupported else 'high', 'manual' if unsupported else 'confirmed',
                'Validação DTCG limitada pelo formato' if unsupported else 'Falha na validação DTCG do conjunto',
                {'files': sources, 'error': message}, 'Usar pipeline compatível para formatos não suportados.' if unsupported else 'Inspecionar o erro indicado e dependências; o validador interrompe no primeiro erro, sem corrigir fontes.')
    elif not sources:
        add('TOKENS_UNKNOWN', 'low', 'manual', 'Fonte DTCG não identificada', {'decisions': decisions}, 'Localizar fontes/agregação e fornecer --source; não gerar tokens durante audit.')
    else:
        token_status = 'blocked'
    contrast_results = []
    for pair in config['contrast_pairs']:
        ev, usage = pair['evidence'], pair['usage']
        lines = files.get(ev['file'], '').splitlines()
        evidence_matches = ev['line'] <= len(lines) and ev['text'] in lines[ev['line'] - 1]
        location = {**ev, 'foreground': pair['foreground'], 'background': pair['background'], 'usage': usage}
        result = {'foreground': pair['foreground'], 'background': pair['background'], 'usage': usage, 'evidence': ev}
        if not evidence_matches:
            result['status'] = 'manual'
            add('CONTRAST_EVIDENCE', 'low', 'manual', 'Evidência do par não conferida no escopo', location, 'Conferir fonte/linha e relação real de primeiro plano, fundo, estado e critério antes de calcular.')
        else:
            try:
                colors = []
                for path in (pair['foreground'], pair['background']):
                    if path not in resolved or token_index[path][0] != 'color':
                        raise ValueError('Cor não resolvida: ' + path)
                    value = resolved[path]
                    if value.get('alpha', 1) != 1:
                        raise ValueError('Transparência exige composição e superfícies reais; não calculada pelo helper.')
                    colors.append(value['components'])
                ratio = contrast(*colors)
                result.update(evaluate(ratio, usage)); result['status'] = 'calculated_declared_pair'
                if not result['AA']:
                    add('CONTRAST_AA', 'high', 'confirmed', 'Par declarado abaixo do limiar AA informado',
                        {**location, 'ratio': ratio, 'threshold': result['threshold_AA']},
                        'Rever o par para o uso declarado. A conta é comprovada; confirmar aplicação, exceções e estado no componente antes de concluir violação da interface.')
            except ValueError as error:
                result['status'] = 'manual'
                add('CONTRAST_BLOCKED', 'medium', 'manual', 'Contraste não calculado', {**location, 'error': str(error)}, 'Resolver fonte/formatos e composição real; não assumir aprovação de contraste.')
        contrast_results.append(result)
    if not config['contrast_pairs']:
        add('CONTRAST_UNKNOWN', 'low', 'manual', 'Nenhum par com uso/contexto declarado', {'pairs': 0}, 'Identificar pares no código/decisões e fornecer evidências. Nomes de tokens não bastam; não gerar produto cartesiano de paletas.')
    for filename, content in files.items():
        if filename in sources or Path(filename).suffix not in SOURCE or any(s in filename for s in ('.test.', '.spec.', '.stories.', '.g.dart')):
            continue
        literals = []
        for line, text in enumerate(content.splitlines(), 1):
            if text.lstrip().startswith(('//', '/*', '*')):
                continue
            if any(LITERAL.search(m.group(1)) for m in STYLE.finditer(text)) or (Path(filename).suffix == '.dart' and DART_LITERAL.search(text)):
                literals.append({'file': filename, 'line': line, 'text': text.strip()[:180]})
        if literals:
            add('STYLE_LITERAL', 'medium', 'risk', 'Literais de estilo para revisar no contexto', {'count': len(literals), 'examples': literals[:5]}, 'Conferir binding/token equivalente e justificativas (zero, hairline, full, assets, medidas estruturais); regex não comprova hardcode desnecessário.')
        for match in re.finditer(r'<img\b[^>]*>', content, re.I):
            if not re.search(r'\balt\s*=', match.group()) and not re.search(r'aria-hidden\s*=\s*[\'"]true', match.group()):
                add('IMAGE_NAME', 'medium', 'risk', 'Imagem sem alt explícito no trecho', {'file': filename, 'line': content.count('\n', 0, match.start()) + 1, 'text': match.group()[:180]}, 'Verificar nome acessível, decoração e props espalhadas no DOM renderizado; não inferir falha apenas pelo trecho.')
    for path, bindings in config['bindings'].items():
        if path in token_index or token_status != 'passed_supported_subset':
            continue
        occurrences = list(islice(({'file': f, 'line': i, 'binding': b} for f, text in files.items() for i, line in enumerate(text.splitlines(), 1) for b in bindings if b in line), 5))
        if occurrences:
            add('BINDING_UNKNOWN', 'medium', 'risk', 'Binding observado aponta para token não encontrado no conjunto', {'token': path, 'examples': occurrences[:5]}, 'Conferir mapa/geração e fontes efetivas antes de concluir uso incorreto; sem alteração automática.')
    for component in config['components']:
        for item in component['expectations']:
            observations = []
            for role in ('implementation', 'documentation', 'catalog'):
                term, filename = item[role], component[role]
                if term is None:
                    continue
                text = files.get(filename)
                if text is None:
                    observations.append({'role': role, 'file': filename, 'status': 'not_read'})
                elif term not in text:
                    observations.append({'role': role, 'file': filename, 'searched': term, 'status': 'literal_not_found'})
            if observations:
                certainty = 'manual' if all(o['status'] == 'not_read' for o in observations) else 'risk'
                add('CONTRACT_COVERAGE', 'medium', certainty, 'Cobertura textual a conferir: ' + component['name'] + ' / ' + item['name'], observations,
                    'Comparar contrato aprovado, API, casos parametrizados e testes reais. Ausência do literal não comprova estado/variante ausente.')
    findings.sort(key=rank)
    contrast_results.sort(key=lambda result: 0 if result.get('AA') is False else 1 if result['status'] == 'manual' else 2)
    return {'status': 'findings' if counts['confirmed'] else 'needs_review' if counts['risk'] else 'limited_checks_completed',
            'summary': counts, 'findings': findings, 'omitted_findings': omitted,
            'checks': {'tokens': {'status': token_status, 'count': token_count, 'sources': sources}, 'contrast': contrast_results[:10], 'contrast_total': len(contrast_results), 'contrast_omitted': max(0, len(contrast_results) - 10)},
            'coverage': coverage,
            'manual_checks': ['Conferir contrato/API, decisões, variantes e estados nos exemplos/testes reais.', 'Verificar teclado, foco, nome/semântica, leitor de tela, zoom, alvos e temas no runtime.'],
            'limitations': 'Somente leitura; validação DTCG parcial e busca textual. Cálculo do par declarado não prova aplicação nem conformidade WCAG completa. Sem execução de comandos/JS do projeto.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project')
    parser.add_argument('--source', action='append')
    parser.add_argument('--decisions', default='design-system/decisions.json')
    parser.add_argument('--scope', action='append')
    parser.add_argument('--exclude', action='append', help='Arquivo ou diretório relativo ao projeto, sem glob; repetível. Exclui só busca textual.')
    parser.add_argument('--config', type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.project, read(args.config) if args.config else None, args.source, args.decisions, args.scope, excludes=args.exclude)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 2 if result['summary']['confirmed'] else 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError) as error:
        print('Erro: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
