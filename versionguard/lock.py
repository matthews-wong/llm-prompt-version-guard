"""Lockfile of approved prompt hashes, and the comparison against it."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, Iterable, List

from .promptfile import Prompt, parse_version

LOCK_INDENT = 2


@dataclass(frozen=True)
class Finding:
    name: str
    message: str


def body_hash(body: str) -> str:
    # Line endings and trailing whitespace are not behaviour; a CRLF checkout
    # or an editor strip must not read as a prompt change.
    normalized = "\n".join(line.rstrip() for line in body.replace("\r\n", "\n").split("\n"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def build_lock(prompts: Iterable[Prompt]) -> Dict[str, Dict[str, str]]:
    return {p.name: {"version": p.version, "sha256": body_hash(p.body)} for p in sorted(prompts, key=lambda p: p.name)}


def dump_lock(lock: Dict[str, Dict[str, str]]) -> str:
    return json.dumps(lock, indent=LOCK_INDENT) + "\n"


def compare(prompts: Iterable[Prompt], lock: Dict[str, Dict[str, str]]) -> List[Finding]:
    findings: List[Finding] = []
    current = {p.name: p for p in prompts}
    for name, prompt in sorted(current.items()):
        locked = lock.get(name)
        if locked is None:
            findings.append(Finding(name, "not in the lockfile; run `lock` to record it"))
            continue
        changed = body_hash(prompt.body) != locked["sha256"]
        old = parse_version(locked["version"], f"lockfile entry {name!r}")
        new = parse_version(prompt.version, name)
        if new < old:
            findings.append(Finding(name, f"version went backwards: {locked['version']} -> {prompt.version}"))
        elif changed and new == old:
            findings.append(Finding(name, f"text changed but version is still {prompt.version}; bump it"))
        elif changed or new > old:
            findings.append(Finding(name, f"version is {prompt.version} but the lockfile has {locked['version']}; run `lock`"))
    for name in sorted(set(lock) - set(current)):
        findings.append(Finding(name, "is in the lockfile but its prompt file is gone; run `lock` to drop it"))
    return findings
