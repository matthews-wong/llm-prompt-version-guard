"""Command line: `check` compares prompts with the lockfile, `lock` rewrites it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .lock import build_lock, compare, dump_lock
from .promptfile import PromptFileError, load_prompts

DEFAULT_PROMPTS_DIR = "prompts"
DEFAULT_LOCKFILE = "prompts.lock.json"


def read_lock(path: Path) -> dict:
    if not path.exists():
        raise PromptFileError(f"{path}: no lockfile; run `lock` first")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PromptFileError(f"{path}: not valid JSON ({error})") from error


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="versionguard")
    parser.add_argument("command", choices=("check", "lock"))
    parser.add_argument("--prompts", type=Path, default=Path(DEFAULT_PROMPTS_DIR))
    parser.add_argument("--lockfile", type=Path, default=Path(DEFAULT_LOCKFILE))
    args = parser.parse_args(argv)
    try:
        prompts = load_prompts(args.prompts)
        if args.command == "lock":
            args.lockfile.write_text(dump_lock(build_lock(prompts)), encoding="utf-8")
            print(f"locked {len(prompts)} prompt(s) in {args.lockfile}")
            return 0
        findings = compare(prompts, read_lock(args.lockfile))
    except PromptFileError as error:
        print(error, file=sys.stderr)
        return 1
    for finding in findings:
        print(f"{finding.name}: {finding.message}", file=sys.stderr)
    if findings:
        return 1
    print(f"{len(prompts)} prompt(s) match the lockfile")
    return 0


if __name__ == "__main__":
    sys.exit(main())
