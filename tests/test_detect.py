import os, sys, tempfile, unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ghpush


def touch(root, *names):
    for n in names:
        p = Path(root) / n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x")


class DetectTests(unittest.TestCase):
    def test_marker_file(self):
        with tempfile.TemporaryDirectory() as d:
            touch(d, "package.json")
            self.assertEqual(ghpush.detect_language(Path(d)), "Node")

    def test_extension_majority(self):
        with tempfile.TemporaryDirectory() as d:
            touch(d, *[f"f{i}.c" for i in range(5)], "tool.py")
            self.assertEqual(ghpush.detect_language(Path(d)), "C")

    def test_skips_node_modules(self):
        with tempfile.TemporaryDirectory() as d:
            touch(d, "main.py", *[f"node_modules/x{i}.js" for i in range(10)])
            self.assertEqual(ghpush.detect_language(Path(d)), "Python")

    def test_empty_folder(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(ghpush.detect_language(Path(d)))


if __name__ == "__main__":
    unittest.main()
