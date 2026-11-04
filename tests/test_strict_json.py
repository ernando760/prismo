"""Contratos de leitura de JSON dos comandos públicos."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/prismo/scripts'

class StrictJsonTests(unittest.TestCase):
    def test_duplicate_keys_rejected_by_foundation_and_token_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            duplicate = root / 'bad.json'
            duplicate.write_text('{"x": 1, "x": 2}')
            for command in ([sys.executable, str(SCRIPTS / 'spacing.py'), '--plan', str(duplicate)],
                            [sys.executable, str(SCRIPTS / 'tokens.py'), 'validate', str(root), '--source', 'bad.json']):
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Chave JSON duplicada', result.stderr)
