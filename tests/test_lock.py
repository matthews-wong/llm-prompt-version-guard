import unittest

from versionguard.lock import body_hash, build_lock, compare
from versionguard.promptfile import Prompt


def prompt(body: str = "Hello {{x}}\n", version: str = "1.0.0", name: str = "greet") -> Prompt:
    return Prompt(name, version, body)


class BodyHashTest(unittest.TestCase):
    def test_line_endings_and_trailing_space_are_ignored(self) -> None:
        self.assertEqual(body_hash("a  \r\nb\r\n"), body_hash("a\nb\n"))

    def test_text_change_changes_the_hash(self) -> None:
        self.assertNotEqual(body_hash("a\n"), body_hash("b\n"))


class CompareTest(unittest.TestCase):
    def setUp(self) -> None:
        self.lock = build_lock([prompt()])

    def messages(self, *prompts: Prompt) -> list:
        return [f"{f.name}: {f.message}" for f in compare(prompts, self.lock)]

    def test_unchanged_is_clean(self) -> None:
        self.assertEqual(self.messages(prompt()), [])

    def test_changed_text_without_bump_fails(self) -> None:
        (message,) = self.messages(prompt(body="Hi {{x}}\n"))
        self.assertIn("text changed but version is still 1.0.0", message)

    def test_changed_text_with_bump_asks_for_lock(self) -> None:
        (message,) = self.messages(prompt(body="Hi {{x}}\n", version="1.1.0"))
        self.assertIn("run `lock`", message)

    def test_downgrade_fails(self) -> None:
        (message,) = self.messages(prompt(version="0.9.0"))
        self.assertIn("backwards", message)

    def test_new_prompt_must_be_locked(self) -> None:
        (message,) = self.messages(prompt(), prompt(name="extra"))
        self.assertIn("extra: not in the lockfile", message)

    def test_removed_prompt_is_reported(self) -> None:
        (message,) = self.messages()
        self.assertIn("greet: is in the lockfile but its prompt file is gone", message)

    def test_lock_then_compare_is_clean(self) -> None:
        edited = prompt(body="Hi {{x}}\n", version="1.1.0")
        self.assertEqual(compare([edited], build_lock([edited])), [])
