"""Smoke obrigatório do pacote sintético; sem publicar ou alterar consumidores reais."""
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DistributionTests(unittest.TestCase):
    def test_tarball_public_contract_and_broken_variants(self):
        manifest = Path(os.environ.get('PRISMO_DISTRIBUTION_TEST_PACKAGE', ROOT / 'package.json')).resolve()
        # Resolve somente ferramentas declaradas, sem procurar instalações dos POCs.
        tools = subprocess.run(['node', '-e', """
const requireFrom = require('node:module').createRequire(process.argv[1]);
console.log(JSON.stringify({tsc: requireFrom.resolve('typescript/bin/tsc'),
                           esbuild: requireFrom.resolve('esbuild')}));
""", str(manifest)], capture_output=True, text=True, timeout=30)
        self.assertEqual(tools.returncode, 0, 'Dependências de distribuição ausentes; execute npm ci.\n' + tools.stderr)
        tools = json.loads(tools.stdout)
        with tempfile.TemporaryDirectory(prefix='prismo-distribution-') as temporary:
            root = Path(temporary)
            library, consumer = root / 'library', root / 'consumer'
            (library / 'dist').mkdir(parents=True)
            consumer.mkdir()
            env = {**os.environ, 'npm_config_cache': str(root / 'npm-cache'),
                   'npm_config_audit': 'false', 'npm_config_fund': 'false',
                   'npm_config_update_notifier': 'false'}

            def write(path, value):
                path.write_text(value if isinstance(value, str) else json.dumps(value), encoding='utf-8')

            def run(args, cwd=consumer, expected=0, diagnostic=None):
                result = subprocess.run([str(a) for a in args], cwd=cwd, env=env,
                                        capture_output=True, text=True, timeout=60)
                output = result.stdout + result.stderr
                if expected == 0:
                    self.assertEqual(result.returncode, 0, output)
                else:
                    self.assertNotEqual(result.returncode, 0, output)
                if diagnostic:
                    self.assertRegex(output, diagnostic)
                return result

            package = {'name': 'prismo-distribution-fixture', 'version': '1.0.0',
                       'type': 'module', 'files': ['dist'], 'sideEffects': ['**/*.css'],
                       'exports': {'.': {'types': './dist/index.d.ts', 'import': './dist/index.js'},
                                   './button': {'types': './dist/button.d.ts', 'import': './dist/button.js'},
                                   './styles.css': './dist/styles.css'}}
            files = {
                'index.js': "export {button} from './button.js';",
                'button.js': 'export const button = props => props.label;',
                'index.d.ts': "export {button, type ButtonProps} from './button.js';",
                'button.d.ts': 'export interface ButtonProps {label: string}\nexport declare const button: (props: ButtonProps) => string;',
                'styles.css': '.button { color: red; }',
            }
            write(library / 'package.json', package)
            for filename, content in files.items():
                write(library / 'dist' / filename, content)
            write(library / 'not-distributed.js', 'throw Error("workspace leak");')
            write(consumer / 'package.json', {'private': True, 'type': 'module'})

            packed = json.loads(run(['npm', 'pack', '--json', '--ignore-scripts', '--offline',
                                     '--pack-destination', root], cwd=library).stdout)[0]
            artifact = root / packed['filename']
            with tarfile.open(artifact, 'r:gz') as tar:
                names = set(tar.getnames())
                self.assertTrue({'package/dist/' + name for name in files} <= names)
                self.assertNotIn('package/not-distributed.js', names)
                self.assertEqual(json.load(tar.extractfile('package/package.json')), package)
            run(['npm', 'install', '--offline', '--ignore-scripts', '--no-audit', '--no-fund', artifact])
            installed = consumer / 'node_modules' / package['name']
            self.assertFalse(installed.is_symlink(), 'Consumidor deve usar o tarball, sem symlink de workspace.')
            write(consumer / 'index.mjs', """
import {button} from 'prismo-distribution-fixture';
import {button as subpath} from 'prismo-distribution-fixture/button';
if (button({label:'OK'}) !== 'OK' || button !== subpath) throw Error('public contract');
""")
            write(consumer / 'index.ts', """
import {button, type ButtonProps} from 'prismo-distribution-fixture';
import {button as subpath, type ButtonProps as SubpathProps} from 'prismo-distribution-fixture/button';
const props: ButtonProps & SubpathProps = {label: 'OK'};
const value: string = button(props) + subpath(props);
""")

            def typecheck(mode, expected=0, diagnostic=None):
                return run(['node', tools['tsc'], '--noEmit', '--skipLibCheck', 'false', '--strict',
                            '--target', 'ES2022', '--module', 'ESNext' if mode == 'Bundler' else 'NodeNext',
                            '--moduleResolution', mode, 'index.ts'], expected=expected, diagnostic=diagnostic)

            write(consumer / 'style-entry.js', "import 'prismo-distribution-fixture/styles.css';")
            bundle_script = """
require(process.argv[1]).build({entryPoints:['style-entry.js'], bundle:true,
  outdir:'bundle', logLevel:'silent', metafile:true}).then(result => {
    if (!Object.keys(result.metafile.outputs).some(path => path.endsWith('.css'))) throw Error('CSS not emitted');
}).catch(error => { console.error(error.message); process.exitCode=1; });
"""

            def bundle(expected=0, diagnostic=None):
                return run(['node', '-e', bundle_script, tools['esbuild']], expected=expected, diagnostic=diagnostic)

            with self.subTest(contract='tarball exports/runtime, types NodeNext/Bundler, CSS'):
                run(['node', 'index.mjs'])
                typecheck('NodeNext'); typecheck('Bundler')
                bundle()
                self.assertIn('color: red', (consumer / 'bundle/style-entry.css').read_text())

            with self.subTest(regression='extensionless ESM declaration'):
                write(installed / 'dist/index.d.ts', "export {button, type ButtonProps} from './button';")
                typecheck('NodeNext', expected=1, diagnostic='TS2835')
                typecheck('Bundler')
                write(installed / 'dist/index.d.ts', files['index.d.ts'])

            with self.subTest(regression='missing declaration'):
                (installed / 'dist/button.d.ts').unlink()
                for mode in ('NodeNext', 'Bundler'):
                    typecheck(mode, expected=1, diagnostic='TS7016|TS2307')
                write(installed / 'dist/button.d.ts', files['button.d.ts'])

            with self.subTest(regression='missing CSS'):
                (installed / 'dist/styles.css').unlink()
                bundle(expected=1, diagnostic='Could not resolve')
                write(installed / 'dist/styles.css', files['styles.css'])

            with self.subTest(regression='CSS subpath not exported'):
                without_css = json.loads(json.dumps(package))
                del without_css['exports']['./styles.css']
                write(installed / 'package.json', without_css)
                bundle(expected=1, diagnostic='not exported|Could not resolve')
                write(installed / 'package.json', package)

            with self.subTest(regression='broken runtime export'):
                write(installed / 'dist/index.js', "export {button} from './missing.js';")
                run(['node', 'index.mjs'], expected=1, diagnostic='ERR_MODULE_NOT_FOUND')


if __name__ == '__main__':
    unittest.main()
