from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import baseline
import optimized


class TreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'a').mkdir()
        (self.root / 'a' / 'deep').mkdir()
        (self.root / 'a' / 'deep' / 'x.txt').touch()
        (self.root / 'a' / 'note.txt').touch()
        (self.root / 'b').mkdir()
        (self.root / 'z.py').touch()

    def check_both(self, expected, folders_only=False, include=None,
                   exclude=None, pretty=False, max_depth=None):
        expected = [str(self.root)] + expected
        for module in (baseline, optimized):
            result = module.build_tree(self.root, folders_only, include,
                                       exclude, pretty, max_depth)
            self.assertEqual(result, expected)

    def test_default(self):
        self.check_both(['    a', '        deep', '            x.txt',
                         '        note.txt', '    b', '    z.py'])

    def test_folders_only(self):
        self.check_both(['    a', '        deep', '    b'], folders_only=True)

    def test_include(self):
        self.check_both(['    z.py'], include='.py')

    def test_exclude(self):
        self.check_both(['    b', '    z.py'], exclude='a')

    def test_pretty(self):
        self.check_both(['├── a', '│   ├── deep', '│   │   └── x.txt',
                         '│   └── note.txt', '├── b', '└── z.py'], pretty=True)

    def test_max_depth(self):
        self.check_both(['    a', '    b', '    z.py'], max_depth=1)

    def test_zero_depth(self):
        self.check_both([], max_depth=0)

    def test_empty_directory(self):
        for module in (baseline, optimized):
            self.assertEqual(module.build_tree(self.root / 'b'), [str(self.root / 'b')])

    def test_no_matches(self):
        self.check_both([], include='not_found')

    def test_pretty_after_filter(self):
        self.check_both(['├── a', '│   └── note.txt', '├── b', '└── z.py'],
                        pretty=True, exclude='deep')

    def test_unicode_and_spaces(self):
        (self.root / 'папка с пробелом').mkdir()
        self.check_both(['    папка с пробелом'], include='папка')

    def test_invalid_paths(self):
        for module in (baseline, optimized):
            for path in (self.root / 'absent', self.root / 'z.py'):
                with self.assertRaises(ValueError):
                    module.build_tree(path)

    def test_symlink_cycle(self):
        link = self.root / 'loop'
        try:
            link.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('Создание символических ссылок недоступно')
        self.check_both(['    a', '        deep', '            x.txt',
                         '        note.txt', '    b', '    loop', '    z.py'])

    def test_cli(self):
        script = Path(__file__).with_name('tree.py')
        result = subprocess.run([sys.executable, '-X', 'utf8', str(script), str(self.root),
                                 '--pretty', '--max-depth=1'], capture_output=True,
                                encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [str(self.root), '├── a', '├── b', '└── z.py'])
        invalid = subprocess.run([sys.executable, str(script), str(self.root), '--max-depth=-1'],
                                 capture_output=True)
        self.assertNotEqual(invalid.returncode, 0)


if __name__ == '__main__':
    unittest.main()