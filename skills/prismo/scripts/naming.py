"""Política opcional de nomes; diagnósticos independentes do validador DTCG."""
import re

LEVELS = ('primitive', 'semantic', 'component')
DEFAULT_PREFIXES = {level: level for level in LEVELS}
VOCABULARIES = ('categories', 'properties', 'intentions', 'variants', 'states')
SEGMENT = re.compile(r'^[A-Za-z0-9_-]+$')


def policy(value):
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) - {'version', 'mode', 'levels', 'vocabulary'}:
        raise ValueError('Política naming inválida: campos desconhecidos.')
    if value.get('version') != 1 or isinstance(value.get('version'), bool) or value.get('mode') not in ('recommended', 'custom'):
        raise ValueError('naming exige version 1 e mode recommended ou custom.')
    levels = value.get('levels', {})
    vocab = value.get('vocabulary', {})
    if not isinstance(levels, dict) or set(levels) - set(LEVELS) or not isinstance(vocab, dict) or set(vocab) - set(VOCABULARIES):
        raise ValueError('Níveis ou vocabulários de naming inválidos.')
    prefixes = dict(DEFAULT_PREFIXES)
    for level, config in levels.items():
        if not isinstance(config, dict) or set(config) != {'prefix'} or not isinstance(config['prefix'], str):
            raise ValueError('Cada nível exige prefix textual.')
        prefix = config['prefix']
        if prefix and any(not SEGMENT.fullmatch(part) for part in prefix.split('.')):
            raise ValueError('Prefixo naming inválido: ' + prefix)
        prefixes[level] = prefix
    values = list(prefixes.values())
    if len(set(values)) != len(values) or any(a and b and (a.startswith(b + '.') or b.startswith(a + '.')) for a in values for b in values if a != b):
        raise ValueError('Prefixos de níveis ambíguos; esclareça a convenção.')
    for key, words in vocab.items():
        if not isinstance(words, list) or not words or any(not isinstance(w, str) or not SEGMENT.fullmatch(w) for w in words) or len(set(words)) != len(words):
            raise ValueError('Vocabulário naming inválido: ' + key)
    return {'version': 1, 'mode': value['mode'], 'levels': {k: {'prefix': v} for k, v in prefixes.items()}, 'vocabulary': vocab}


def from_record(record):
    settings = record.get('decisions', record)
    if not isinstance(settings, dict):
        raise ValueError('Configuração de decisões inválida.')
    return policy(settings.get('naming'))


def path(level, suffix, naming=None):
    prefix = naming['levels'][level]['prefix'] if naming else level
    return '.'.join(part for part in (prefix, suffix) if part)


def diagnose(paths, naming):
    if naming is None:
        return {'status': 'not_configured', 'findings': []}
    prefixes = {k: v['prefix'] for k, v in naming['levels'].items()}
    findings = []
    for token in sorted(paths):
        matches = [level for level, prefix in prefixes.items() if prefix and (token == prefix or token.startswith(prefix + '.'))]
        if not matches:
            findings.append({'path': token, 'certainty': 'manual', 'reason': 'Nível não classificável com segurança; verificar intenção e convenção.'})
        elif token == prefixes[matches[0]]:
            findings.append({'path': token, 'certainty': 'confirmed', 'reason': 'Prefixo sem caminho específico do token.'})
        elif naming['vocabulary'].get('categories') and matches[0] in ('primitive', 'semantic'):
            remainder = token[len(prefixes[matches[0]]) + 1:].split('.')
            if remainder[0] not in naming['vocabulary']['categories']:
                findings.append({'path': token, 'certainty': 'manual', 'reason': 'Categoria não consta do vocabulário registrado; confirmar estrutura e intenção.'})
    return {'status': 'review' if findings else 'checked', 'findings': findings,
            'limitations': 'Vocabulário e intenção exigem revisão contextual; ausência de achados não comprova conformidade.'}


def alias_candidates(tokens):
    """Só aliases diretos exatos; alvos iguais não comprovam redundância."""
    groups = {}
    for token, (_, value) in tokens.items():
        if isinstance(value, str) and re.fullmatch(r'\{[^{}]+\}', value):
            groups.setdefault(value[1:-1], []).append(token)
    return [{'target': target, 'paths': sorted(paths), 'certainty': 'manual'}
            for target, paths in sorted(groups.items()) if len(paths) > 1]
