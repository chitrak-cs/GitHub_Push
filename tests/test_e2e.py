"""End-to-end run of the real CLI against a fake `gh` (no network, no GitHub)."""
import os, stat, subprocess, sys, tempfile, textwrap, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FAKE_GH = textwrap.dedent('''\
    #!/usr/bin/env python3
    import sys, os
    a = sys.argv[1:]
    with open(os.environ["FAKE_GH_LOG"], "a") as f:
        f.write(" ".join(a) + "\\n")
    if a[:2] == ["auth", "status"]: sys.exit(0)
    if a[:2] == ["api", "user"]: print("tester"); sys.exit(0)
    if a[0] == "api" and a[1].startswith("gitignore/"): print("*.o"); sys.exit(0)
    if a[0] == "api" and a[1].startswith("licenses/"): print("MIT [year] [fullname]"); sys.exit(0)
    if a[:2] == ["repo", "view"]:
        if "--json" in a: print("https://github.com/tester/demo"); sys.exit(0)
        sys.exit(1)  # name is free
    if a[:2] == ["repo", "create"]: sys.exit(0)
    if a[:2] == ["repo", "edit"]: sys.exit(0)
    sys.exit(0)
''')


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        (t / "bin").mkdir()
        gh = t / "bin" / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
        (t / "gitconfig").write_text("[user]\n\tname = Test\n\temail = t@example.com\n")
        self.log = t / "gh.log"
        self.env = dict(os.environ, PATH=f"{t/'bin'}:{os.environ['PATH']}",
                        GIT_CONFIG_GLOBAL=str(t / "gitconfig"), FAKE_GH_LOG=str(self.log))
        self.proj = t / "my project"
        self.proj.mkdir()
        (self.proj / "main.c").write_text("int main(){return 0;}")
        (self.proj / ".env").write_text("SECRET=123")
        (self.proj / ".env.example").write_text("SECRET=")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *extra):
        return subprocess.run([sys.executable, str(ROOT / "ghpush.py"), str(self.proj), "-y", *extra],
                              env=self.env, capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def tracked(self):
        return subprocess.run(["git", "ls-files"], cwd=self.proj, env=self.env,
                              capture_output=True, text=True).stdout.split()

    def test_full_run(self):
        r = self.run_cli("--license", "mit", "--topics", "c,demo")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        files = self.tracked()
        self.assertIn("main.c", files)
        self.assertIn(".gitignore", files)
        self.assertIn("README.md", files)
        self.assertIn("LICENSE", files)
        self.assertIn(".env.example", files)
        self.assertNotIn(".env", files)
        log = self.log.read_text()
        self.assertIn("repo create my-project --public", log)
        self.assertIn("--add-topic c --add-topic demo", log)
        self.assertIn("github.com/tester/demo", r.stdout)

    def test_non_interactive_flags(self):
        r = self.run_cli("-n", "Cool App!", "-d", "hello world", "--private")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        log = self.log.read_text()
        self.assertIn("repo create Cool-App --private --description hello world", log)

    def test_dry_run_creates_nothing(self):
        r = self.run_cli("--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("repo create", self.log.read_text())
        self.assertIn("Dry run complete", r.stdout)

    def test_existing_remote_aborts_with_yes(self):
        subprocess.run(["git", "init", "-b", "main"], cwd=self.proj, env=self.env, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", "https://example.com/x.git"],
                       cwd=self.proj, env=self.env, capture_output=True)
        r = self.run_cli()
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("repo create", self.log.read_text())

    def test_not_logged_in_stops(self):
        gh = Path(self.tmp.name) / "bin" / "gh"
        gh.write_text(FAKE_GH.replace('["auth", "status"]: sys.exit(0)', '["auth", "status"]: sys.exit(1)'))
        r = self.run_cli()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("gh auth login", r.stderr)


if __name__ == "__main__":
    unittest.main()
