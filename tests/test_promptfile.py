import tempfile
import unittest
from pathlib import Path

from versionguard.promptfile import PromptFileError, load_prompts, parse_prompt, parse_version

SAMPLE = "name: summarize\nversion: 1.2.0\n---\nSummarize: {{text}}\n"


class ParsePromptTest(unittest.TestCase):
    def test_parses_header_and_body(self) -> None:
        prompt = parse_prompt(SAMPLE, "s.prompt")
        self.assertEqual((prompt.name, prompt.version), ("summarize", "1.2.0"))
        self.assertEqual(prompt.body, "Summarize: {{text}}\n")

    def test_missing_separator_names_the_file(self) -> None:
        with self.assertRaisesRegex(PromptFileError, "s.prompt: missing"):
            parse_prompt("name: a\nversion: 1.0.0\n", "s.prompt")

    def test_missing_version_is_rejected(self) -> None:
        with self.assertRaisesRegex(PromptFileError, "missing 'version'"):
            parse_prompt("name: a\n---\nbody\n", "s.prompt")

    def test_malformed_header_line_is_rejected(self) -> None:
        with self.assertRaisesRegex(PromptFileError, "line 2"):
            parse_prompt("name: a\noops\n---\nbody\n", "s.prompt")

    def test_version_must_be_semver(self) -> None:
        with self.assertRaisesRegex(PromptFileError, "'1.2'"):
            parse_prompt("name: a\nversion: 1.2\n---\nbody\n", "s.prompt")

    def test_parse_version_orders_numerically(self) -> None:
        self.assertGreater(parse_version("1.10.0", "x"), parse_version("1.9.0", "x"))


class LoadPromptsTest(unittest.TestCase):
    def test_duplicate_names_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for file in ("a.prompt", "b.prompt"):
                Path(tmp, file).write_text(SAMPLE, encoding="utf-8")
            with self.assertRaisesRegex(PromptFileError, "duplicate prompt name 'summarize'"):
                load_prompts(Path(tmp))

    def test_ignores_other_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "a.prompt").write_text(SAMPLE, encoding="utf-8")
            Path(tmp, "notes.md").write_text("not a prompt", encoding="utf-8")
            self.assertEqual([p.name for p in load_prompts(Path(tmp))], ["summarize"])
