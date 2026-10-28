import unittest
from pathlib import Path

from versionguard.__main__ import DEFAULT_LOCKFILE, DEFAULT_PROMPTS_DIR, read_lock
from versionguard.lock import compare
from versionguard.promptfile import load_prompts

ROOT = Path(__file__).resolve().parent.parent


class CommittedLockTest(unittest.TestCase):
    def test_example_prompts_match_the_lockfile(self) -> None:
        findings = compare(load_prompts(ROOT / DEFAULT_PROMPTS_DIR), read_lock(ROOT / DEFAULT_LOCKFILE))
        self.assertEqual(findings, [])
