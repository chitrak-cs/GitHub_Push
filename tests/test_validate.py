import os, sys, tempfile, unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ghpush


class SanitizeTests(unittest.TestCase):
    def test_spaces_and_symbols(self):
        self.assertEqual(ghpush.sanitize_repo_name("My Cool Project!"), "My-Cool-Project")

    def test_rejects_empty_and_dots(self):
        for bad in ["", "   ", ".", "..", "!!!"]:
            with self.assertRaises(ValueError):
                ghpush.sanitize_repo_name(bad)

    def test_truncates_to_100(self):
        self.assertEqual(len(ghpush.sanitize_repo_name("a" * 150)), 100)


class FolderTests(unittest.TestCase):
    def test_missing_path(self):
        with self.assertRaises(ValueError):
            ghpush.validate_folder("/definitely/not/here")

    def test_file_not_folder(self):
        with tempfile.NamedTemporaryFile() as f:
            with self.assertRaises(ValueError):
                ghpush.validate_folder(f.name)

    def test_refuses_home_and_root(self):
        for bad in ["~", "/"]:
            with self.assertRaises(ValueError):
                ghpush.validate_folder(bad)

    def test_path_with_spaces(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "my project"
            p.mkdir()
            self.assertEqual(ghpush.validate_folder(str(p)), p.resolve())


if __name__ == "__main__":
    unittest.main()
