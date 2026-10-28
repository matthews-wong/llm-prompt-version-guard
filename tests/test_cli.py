import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from versionguard.__main__ import main

PROMPT = "name: greet\nversion: 1.0.0\n---\nHello {{name}}\n"


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.prompts = self.root / "prompts"
        self.prompts.mkdir()
        self.file = self.prompts / "greet.prompt"
        self.file.write_text(PROMPT, encoding="utf-8")
        self.args = ["--prompts", str(self.prompts), "--lockfile", str(self.root / "lock.json")]

    def run_cli(self, command: str):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main([command, *self.args])
        return code, out.getvalue(), err.getvalue()

    def test_check_without_lockfile_fails_with_hint(self) -> None:
        code, _, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("run `lock` first", err)

    def test_lock_then_check_passes(self) -> None:
        self.assertEqual(self.run_cli("lock")[0], 0)
        code, out, _ = self.run_cli("check")
        self.assertEqual(code, 0)
        self.assertIn("1 prompt(s) match", out)

    def test_edit_without_bump_fails(self) -> None:
        self.run_cli("lock")
        self.file.write_text(PROMPT.replace("Hello", "Hi"), encoding="utf-8")
        code, _, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("greet: text changed but version is still 1.0.0", err)

    def test_edit_with_bump_passes_after_lock(self) -> None:
        self.run_cli("lock")
        self.file.write_text(PROMPT.replace("Hello", "Hi").replace("1.0.0", "1.0.1"), encoding="utf-8")
        self.assertEqual(self.run_cli("check")[0], 1)
        self.run_cli("lock")
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_corrupt_lockfile_is_reported(self) -> None:
        (self.root / "lock.json").write_text("{", encoding="utf-8")
        code, _, err = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", err)
