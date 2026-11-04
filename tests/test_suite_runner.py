"""A suíte obrigatória não aprova resultados ignorados ou bloqueados."""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('suite', Path(__file__).resolve().parents[1] / 'scripts/test_suite.py')
suite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(suite)

class SuiteRunnerTests(unittest.TestCase):
    def test_real_node_reporter_preserves_pass_failure_and_skip_detection(self):
        with tempfile.TemporaryDirectory(prefix='prismo-reporter-') as directory:
            path = Path(directory) / 'probe.mjs'
            for body, expected, code in [
                    ("test('probe', () => {});", True, 0),
                    ("test('probe', () => { throw Error('expected failure'); });", False, 1),
                    ("test('probe', {skip: true}, () => {});", False, 0)]:
                with self.subTest(body=body):
                    path.write_text("import test from 'node:test';\n" + body)
                    result = subprocess.run(suite.js_command(path), capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                    self.assertEqual(suite.js_result(result.returncode, result.stdout + result.stderr), expected)

    def test_skipped_and_missing_results_fail(self):
        report = '# tests 2\n# pass 2\n# fail 0\n# skipped 0\n# cancelled 0\n'
        self.assertTrue(suite.js_result(0, report))
        self.assertFalse(suite.js_result(0, report.replace('# skipped 0', '# skipped 1')))
        self.assertFalse(suite.js_result(0, ''))
        self.assertFalse(suite.js_result(1, report))

    def test_python_skips_and_empty_output_fail(self):
        self.assertTrue(suite.python_result(0, 'Ran 2 tests in 0.1s\n\nOK\n'))
        self.assertFalse(suite.python_result(0, 'Ran 2 tests in 0.1s\n\nOK (skipped=1)\n'))
        self.assertFalse(suite.python_result(0, ''))
