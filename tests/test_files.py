import os, sys, tempfile, unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ghpush

FAILED = CompletedProcess([], 1, stdout="", stderr="offline")


class GitignoreTests(unittest.TestCase):
    def test_fallback_when_fetch_fails(self):
        with tempfile.TemporaryDirectory() as d, mock.patch("ghpush.run", return_value=FAILED):
            warnings = []
            ghpush.ensure_gitignore(Path(d), "C", warnings)
            self.assertIn(".env", (Path(d) / ".gitignore").read_text())
            self.assertTrue(warnings)

    def test_existing_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".gitignore").write_text("custom\n")
            ghpush.ensure_gitignore(Path(d), "C", [])
            self.assertEqual((Path(d) / ".gitignore").read_text(), "custom\n")

    def test_fetched_template_gets_secrets_block(self):
        fetched = CompletedProcess([], 0, stdout="*.o\n", stderr="")
        with tempfile.TemporaryDirectory() as d, mock.patch("ghpush.run", return_value=fetched):
            ghpush.ensure_gitignore(Path(d), "C", [])
            text = (Path(d) / ".gitignore").read_text()
            self.assertIn("*.o", text)
            self.assertIn(".env", text)


class ReadmeTests(unittest.TestCase):
    def test_created_with_name_and_warning(self):
        with tempfile.TemporaryDirectory() as d:
            warnings = []
            self.assertTrue(ghpush.ensure_readme(Path(d), "demo", "", "C", warnings))
            self.assertIn("# demo", (Path(d) / "README.md").read_text())
            self.assertEqual(len(warnings), 1)

    def test_lowercase_readme_counts(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "readme.md").write_text("hi")
            warnings = []
            self.assertFalse(ghpush.ensure_readme(Path(d), "demo", "", None, warnings))
            self.assertEqual(os.listdir(d), ["readme.md"])
            self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
