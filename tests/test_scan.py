import os, sys, tempfile, unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ghpush


class ScanTests(unittest.TestCase):
    def test_env_detected(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".env").write_text("SECRET=1")
            (Path(d) / "main.c").write_text("int main(){}")
            secrets, big = ghpush.scan_folder(Path(d))
            self.assertEqual(secrets, [".env"])
            self.assertEqual(big, [])

    def test_large_file_detected(self):
        with tempfile.TemporaryDirectory() as d:
            with open(Path(d) / "huge.bin", "wb") as f:
                f.truncate(101 * 1024 * 1024)
            _, big = ghpush.scan_folder(Path(d))
            self.assertEqual(big, ["huge.bin"])

    def test_skipped_dirs_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            nm = Path(d) / "node_modules"
            nm.mkdir()
            (nm / "server.pem").write_text("x")
            self.assertEqual(ghpush.scan_folder(Path(d))[0], [])


if __name__ == "__main__":
    unittest.main()


class TemplateTests(unittest.TestCase):
    def test_templates_allowed(self):
        for name in [".env.example", ".env.sample", "key.pem.template", ".env.dist"]:
            self.assertFalse(ghpush.is_secret(name), name)

    def test_real_secrets_still_flagged(self):
        for name in [".env", ".env.local", ".env.example.local", "id_rsa", "x.pem", "credentials.json"]:
            self.assertTrue(ghpush.is_secret(name), name)
