#!/usr/bin/env python3
"""Executa planos de foundations em sequência, com checklist e retomada local."""
import argparse
import copy
import fcntl
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile

import strict_json
from naming import from_record
from token_source import token_source
from tokens import read, relative

ORDER = ('colors', 'typography', 'spacing', 'borders', 'elevation')
REFERENCES = Path(__file__).resolve().parents[1] / 'references'


def select(names=None):
    if names is None:
        return list(ORDER)
    if not names or any(name not in ORDER for name in names):
        raise ValueError('Selecione colors, typography, spacing, borders ou elevation.')
    return [name for name in ORDER if name in names]


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def atomic(path, content):
    """Substituição por arquivo; o journal permite retomar entre dois arquivos."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.' + path.name, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            temporary.chmod(path.stat().st_mode & 0o777)
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def specification(spec):
    if not isinstance(spec, dict) or set(spec) != {'plan', 'sources', 'pending'}:
        raise ValueError('Cada fundação exige plan, sources e pending.')
    plan, sources = spec['plan'], spec['sources']
    if not isinstance(plan, dict) or not isinstance(sources, dict) or set(sources) != set(plan):
        raise ValueError('Registre a origem de cada campo do plano em sources.')
    for source in sources.values():
        if (not isinstance(source, dict) or set(source) != {'origin', 'evidence'}
                or source['origin'] not in ('user', 'existing', 'default')
                or not isinstance(source['evidence'], str) or not source['evidence'].strip()):
            raise ValueError('Origem exige origin user/existing/default e evidence não vazia.')
    if not isinstance(spec['pending'], list) or not all(isinstance(p, str) and p.strip() for p in spec['pending']):
        raise ValueError('pending deve ser lista de pendências textuais.')
    return copy.deepcopy(spec)


def calculate(name, plan, tokens, naming=None):
    result = importlib.import_module(name).build(plan, tokens, naming) if naming else importlib.import_module(name).build(plan, tokens)
    if name == 'colors' and not all(pair['AA'] for pair in result['contrast']):
        raise ValueError('Contraste AA falhou; esclareça os pares sem alterar a marca.')
    return result


def report(result):
    return {key: value for key, value in result.items() if key not in ('tokens', 'status')}


def registered_source(record, root):
    settings = record.get('decisions', record)
    if not isinstance(settings, dict):
        raise ValueError('Configuração de decisões inválida; esclareça sem sobrescrever.')
    return token_source(settings, root)


def recover(root, step, allowed):
    """Só completa writes interrompidos quando cada arquivo ainda é before/after."""
    transaction = step.get('transaction', [])
    if not isinstance(transaction, list) or len(transaction) > 2:
        raise ValueError('Journal inválido; investigue sem sobrescrever.')
    for item in transaction:
        if not isinstance(item, dict) or set(item) != {'path', 'before', 'after'} or item['path'] not in allowed:
            raise ValueError('Destino inválido no journal de foundations.')
        path = relative(root, item['path'])
        if path.read_text(encoding='utf-8') not in (item['before'], item['after']):
            raise ValueError('Conflito durante retomada: ' + item['path'])
    for item in transaction:
        path = relative(root, item['path'])
        if path.read_text(encoding='utf-8') != item['after']:
            atomic(path, item['after'])


def execute(root, names=None, specs=None, decisions='design-system/decisions.json'):
    root = Path(root).resolve(strict=True)
    requested = select(names)
    specs = specs or {}
    if not isinstance(specs, dict) or set(specs) - set(requested):
        raise ValueError('Inclua somente especificações das fundações solicitadas.')
    decision_path = relative(root, decisions)
    # Não inicialize um DS silenciosamente nem crie uma segunda fonte de tokens.
    initial = read(decision_path)
    naming = from_record(initial)
    source = registered_source(initial, root)
    if not source:
        raise ValueError('Fonte única de tokens ausente/ambígua; esclareça ou execute init.')
    token_path = relative(root, source)
    read(token_path)
    plan_path = decision_path.with_name('foundations-plan.json')
    lock_path = decision_path.with_name('.foundations-plan.lock')
    for path in (plan_path, lock_path):
        relative(root, path.relative_to(root).as_posix())
    if len({decision_path, token_path, plan_path, lock_path}) != 4:
        raise ValueError('Destinos sobrepostos para tokens, decisões ou checklist.')
    with lock_path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('Outra execução de foundations está ativa.') from error
        state = read(plan_path) if plan_path.exists() else {
            'version': 1, 'decisions': decisions, 'tokens': source, 'steps': {}}
        if state.get('version') != 1 or state.get('decisions') != decisions or state.get('tokens') != source:
            raise ValueError('Checklist incompatível com os caminhos atuais; investigue sem sobrescrever.')
        if (not isinstance(state.get('steps'), dict) or set(state['steps']) - set(ORDER)
                or any(not isinstance(step, dict) or not isinstance(step.get('checks'), dict)
                       or step.get('status') not in ('pending', 'running', 'completed', 'failed')
                       for step in state['steps'].values())):
            raise ValueError('Etapas do checklist inválidas; investigue sem sobrescrever.')
        if 'naming' in state and state['naming'] != naming:
            raise ValueError('Política de nomenclatura mudou desde o checklist; esclareça a retomada.')
        if 'naming' not in state and naming and state['steps']:
            raise ValueError('Checklist anterior sem política de nomenclatura; esclareça a retomada.')
        # Um journal pode pertencer a uma etapa fora do escopo atual. Nenhuma
        # outra etapa deve gravar nos mesmos arquivos antes da sua recuperação.
        interrupted = [name for name in ORDER
                       if name in state['steps'] and 'transaction' in state['steps'][name]]
        if len(interrupted) > 1:
            raise ValueError('Múltiplas transações pendentes; investigue o checklist sem sobrescrever.')
        if interrupted and interrupted[0] not in requested:
            raise ValueError('Transação pendente em ' + interrupted[0] +
                             '; retome essa etapa antes de executar outras fundações.')
        execution_order = (interrupted + [name for name in requested if name not in interrupted]
                           if interrupted else requested)
        state['naming'] = naming
        state['requested'] = requested
        for name in requested:
            step = state['steps'].setdefault(name, {'status': 'pending', 'checks': {}, 'pending': []})
            # Salve também as escolhas das etapas ainda não alcançadas. A validação
            # específica continua sequencial, quando chegar a vez de cada uma.
            if name in specs and not step.get('completed_once') and 'transaction' not in step:
                step['spec'] = copy.deepcopy(specs[name])
        atomic(plan_path, encoded(state))
        for name in execution_order:
            step = state['steps'][name]
            was_completed = step.get('completed_once', False)
            step['checks'] = {}
            step.pop('validation', None)
            try:
                # A referência, tokens e decisões são relidos antes de CADA etapa.
                reference = (REFERENCES / (name + '.md')).read_text(encoding='utf-8')
                if not reference.strip():
                    raise ValueError('Referência vazia: ' + name)
                step['checks']['reference'] = name + '.md'
                recover(root, step, {source, decisions})
                decision_before = decision_path.read_text(encoding='utf-8')
                token_before = token_path.read_text(encoding='utf-8')
                record, tokens = strict_json.loads(decision_before), strict_json.loads(token_before)
                if not isinstance(record, dict) or not isinstance(tokens, dict):
                    raise ValueError('Tokens e decisões devem ser objetos JSON.')
                if from_record(record) != naming:
                    raise ValueError('Política de nomenclatura mudou durante a execução.')
                if registered_source(record, root) != source:
                    raise ValueError('Fonte de tokens mudou durante a execução.')
                foundations = record.get('foundations', {})
                if not isinstance(foundations, dict):
                    raise ValueError('Registro foundations inválido.')
                prior = foundations.get(name)
                if name in foundations and not isinstance(prior, dict):
                    raise ValueError('Registro existente inválido: foundations.' + name)
                candidate = specs[name] if name in specs else step.get('spec')
                if candidate is None and isinstance(prior, dict) and isinstance(prior.get('plan'), dict):
                    candidate = {'plan': prior['plan'], 'sources': {
                        key: {'origin': 'existing', 'evidence': decisions + '#foundations.' + name}
                        for key in prior['plan']}, 'pending': prior.get('pending', [])}
                if candidate is None:
                    raise ValueError('Informações essenciais ausentes: forneça o plano de ' + name)
                candidate = specification(candidate)
                if step.get('spec') and (was_completed or 'transaction' in step):
                    if step['spec']['plan'] != candidate['plan']:
                        raise ValueError('Conflito com etapa persistida: ' + name)
                    # Uma retomada não reatribui a origem das escolhas já utilizadas.
                    candidate = step['spec']
                if prior is not None and (not isinstance(prior, dict) or prior.get('plan') != candidate['plan']):
                    raise ValueError('Conflito com decisão existente: ' + name)
                step['spec'] = candidate
                step['status'] = 'running'
                step.pop('error', None)
                atomic(plan_path, encoded(state))
                result = calculate(name, candidate['plan'], tokens, naming) if naming else calculate(name, candidate['plan'], tokens)
                # Uma decisão já registrada nunca autoriza reconstruir tokens removidos.
                if (prior is not None or was_completed) and result['tokens'] != tokens:
                    raise ValueError('Tokens divergem da fundação registrada: ' + name)
                step['checks']['calculation'] = 'passed'
                step['validation'] = report(result)
                step['pending'] = candidate['pending']
                if not was_completed:
                    after = copy.deepcopy(record)
                    if prior is None:
                        after.setdefault('foundations', {})[name] = {
                            **candidate, 'validation': report(result),
                            'reference': 'references/' + name + '.md'}
                    step['transaction'] = [
                        {'path': path.relative_to(root).as_posix(), 'before': before, 'after': encoded(value)}
                        for path, before, value in ((token_path, token_before, result['tokens']),
                                                    (decision_path, decision_before, after))
                        if strict_json.loads(before) != value]
                    atomic(plan_path, encoded(state))
                    recover(root, step, {source, decisions})
                persisted = read(token_path)
                final = calculate(name, candidate['plan'], persisted, naming) if naming else calculate(name, candidate['plan'], persisted)
                if final['tokens'] != persisted or read(decision_path).get('foundations', {}).get(name, {}).get('plan') != candidate['plan']:
                    raise ValueError('Validação após persistência falhou: ' + name)
                step['checks']['persisted'] = 'passed'
                step['completed_once'] = True
                step['status'] = 'completed'
                step.pop('transaction', None)
                step.pop('error', None)
                atomic(plan_path, encoded(state))
            except (ValueError, OSError, TypeError, KeyError, ArithmeticError) as error:
                step['status'] = 'failed'
                step['error'] = str(error)
                atomic(plan_path, encoded(state))
                break
        return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--only', nargs='+', choices=ORDER)
    parser.add_argument('--plans', type=Path, help='Objeto por fundação com plan, sources e pending.')
    parser.add_argument('--decisions', default='design-system/decisions.json')
    args = parser.parse_args()
    try:
        state = execute(args.project, args.only, read(args.plans) if args.plans else None, args.decisions)
        print(encoded(state), end='')
        return 0 if all(state['steps'][name]['status'] == 'completed' for name in state['requested']) else 1
    except (ValueError, OSError, TypeError, KeyError, ArithmeticError) as error:
        print(f'Erro: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
