#!/usr/bin/env python3
"""Executa os testes obrigatórios; testes ignorados ou bloqueados falham a suíte."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ['tests/storybook/catalog.test.mjs', 'tests/storybook/render.test.mjs',
      'tests/storybook/adapters.test.mjs', 'tests/document/render.test.mjs']


def js_command(script):
    # O formato padrão do Node varia entre versões; js_result exige TAP.
    return ['node', '--test-reporter=tap', str(script)]


def js_result(code, output):
    counts = {key: int(value) for key, value in re.findall(r'^# (tests|pass|fail|skipped|cancelled) (\d+)$', output, re.M)}
    complete = set(counts) == {'tests', 'pass', 'fail', 'skipped', 'cancelled'}
    return complete and code == 0 and counts['tests'] > 0 and counts['pass'] == counts['tests'] and not any(counts[k] for k in ('fail', 'skipped', 'cancelled'))


def python_result(code, output):
    count = re.search(r'^Ran (\d+) tests? in ', output, re.M)
    return code == 0 and bool(count) and int(count.group(1)) > 0 and bool(re.search(r'^OK$', output, re.M))


def main():
    failed = False
    commands = [[sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q']] + [js_command(script) for script in JS]
    for command in commands:
        try:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        except OSError as error:
            print(f'BLOQUEADO: {command[0]}: {error}', flush=True); failed = True; continue
        output = result.stdout + result.stderr
        ok = python_result(result.returncode, output) if command[0] == sys.executable else js_result(result.returncode, output)
        print(('APROVADO' if ok else 'FALHOU OU INCOMPLETO') + ': ' + ' '.join(command), flush=True)
        print(output, end='', flush=True)
        failed |= not ok
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
