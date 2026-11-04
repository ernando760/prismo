"""Testes isolados do instalador, usando apenas a biblioteca padrão."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='prismo tests ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo com espaços'
        shutil.copytree(REPO / 'skills', self.repo / 'skills')
        (self.repo / 'scripts').mkdir()
        shutil.copy2(REPO / 'scripts/install.sh', self.repo / 'scripts/install.sh')
        self.source = self.repo / 'skills/prismo'
        self.project = self.root / 'projeto com espaços'
        self.project.mkdir()
        self.dest = self.project / '.agents/skills/prismo'

    def run_install(self, mode='copy', update=False, project=None, ok=True):
        args = ['bash', str(self.repo / 'scripts/install.sh'), '--mode', mode]
        if update:
            args.append('--update')
        args.append(str(project if project is not None else self.project))
        result = subprocess.run(args, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def test_symlink_reflects_source(self):
        self.run_install('symlink')
        self.assertTrue(self.dest.is_symlink())
        self.assertEqual(self.dest.resolve(), self.source)
        (self.source / 'new.txt').write_text('novo')
        self.assertEqual((self.dest / 'new.txt').read_text(), 'novo')

    def test_copy_is_independent(self):
        self.run_install()
        self.assertFalse(self.dest.is_symlink())
        self.assertEqual((self.dest / 'SKILL.md').read_bytes(), (self.source / 'SKILL.md').read_bytes())
        (self.source / 'new.txt').write_text('novo')
        self.assertFalse((self.dest / 'new.txt').exists())
        visual = Path('references/visual-design.md')
        self.assertEqual((self.dest / visual).read_bytes(), (self.source / visual).read_bytes())

    def test_existing_install_requires_update(self):
        for mode in ['copy', 'symlink']:
            with self.subTest(mode=mode):
                if self.dest.exists():
                    shutil.rmtree(self.dest)
                self.run_install(mode)
                self.run_install(mode, ok=False)
                self.assertTrue((self.dest / 'SKILL.md').exists())

    def test_update_preserves_local_changes_in_backup(self):
        self.run_install()
        (self.dest / 'local.txt').write_text('preservar')
        (self.source / 'new.txt').write_text('atualizado')
        self.run_install(update=True)
        self.assertEqual((self.dest / 'new.txt').read_text(), 'atualizado')
        backups = list((self.project / '.agents').glob('.prismo-backup.*/prismo'))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / 'local.txt').read_text(), 'preservar')

    def test_modes_can_be_switched(self):
        self.run_install('symlink')
        self.run_install('symlink', update=True)
        self.run_install('copy', update=True)
        self.assertFalse(self.dest.is_symlink())
        self.run_install('symlink', update=True)
        self.assertTrue(self.dest.is_symlink())

    def test_refuses_unmanaged_directory_and_file(self):
        self.dest.mkdir(parents=True)
        sentinel = self.dest / 'keep'
        sentinel.write_text('preservar')
        self.run_install(update=True, ok=False)
        self.assertEqual(sentinel.read_text(), 'preservar')
        shutil.rmtree(self.dest)
        self.dest.write_text('arquivo')
        self.run_install(update=True, ok=False)
        self.assertEqual(self.dest.read_text(), 'arquivo')

    def test_refuses_foreign_and_broken_links(self):
        self.dest.parent.mkdir(parents=True)
        for target in [self.root, self.root / 'inexistente']:
            self.dest.symlink_to(target)
            self.run_install(update=True, ok=False)
            self.assertEqual(self.dest.readlink(), target)
            self.dest.unlink()

    def test_refuses_parent_links(self):
        external = self.root / 'externo'
        external.mkdir()
        (self.project / '.agents').symlink_to(external)
        self.run_install(ok=False)
        self.assertEqual(list(external.iterdir()), [])
        (self.project / '.agents').unlink()
        (self.project / '.agents').mkdir()
        (self.project / '.agents/skills').symlink_to(external)
        self.run_install(ok=False)
        self.assertEqual(list(external.iterdir()), [])

    def test_invalid_arguments_and_project(self):
        self.run_install(mode='invalid', ok=False)
        self.run_install(project=self.root / 'missing', ok=False)
        for args in [[], ['--mode'], ['--unknown'], ['--mode', 'copy', str(self.project), 'extra']]:
            result = subprocess.run(['bash', str(self.repo / 'scripts/install.sh'), *args], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.project / '.agents').exists())

    def test_separator_cannot_override_existing_destination(self):
        other = self.root / 'outro'; other.mkdir()
        result = subprocess.run(['bash', str(self.repo / 'scripts/install.sh'), '--mode', 'copy', str(self.project), '--', str(other)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.project / '.agents').exists())
        self.assertFalse((other / '.agents').exists())

    def test_relative_project(self):
        self.run_install(project=self.project.name)
        self.assertTrue((self.dest / 'SKILL.md').is_file())

    def test_lock_prevents_concurrent_install(self):
        lock = self.project / '.agents/.prismo-install.lock'
        lock.mkdir(parents=True)
        self.run_install(ok=False)
        self.assertFalse(self.dest.exists())
        self.assertTrue(lock.exists())

    def test_refuses_destination_inside_source(self):
        self.run_install(project=self.source, ok=False)
        self.assertFalse((self.source / '.agents').exists())

    def test_missing_source_preserves_install(self):
        self.run_install()
        (self.source / 'SKILL.md').unlink()
        self.run_install(update=True, ok=False)
        self.assertTrue((self.dest / 'SKILL.md').is_file())


if __name__ == '__main__':
    unittest.main()
