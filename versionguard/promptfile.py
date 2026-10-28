"""Parse `.prompt` files: a `key: value` header, a `---` line, then the body."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

HEADER_SEPARATOR = "---"
PROMPT_SUFFIX = ".prompt"
REQUIRED_KEYS = ("name", "version")
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

Version = Tuple[int, int, int]


class PromptFileError(ValueError):
    pass


@dataclass(frozen=True)
class Prompt:
    name: str
    version: str
    body: str


def parse_version(value: str, source: str) -> Version:
    match = SEMVER.match(value)
    if match is None:
        raise PromptFileError(f"{source}: version {value!r} is not MAJOR.MINOR.PATCH")
    return int(match[1]), int(match[2]), int(match[3])


def parse_prompt(text: str, source: str) -> Prompt:
    header_text, separator, body = text.partition(f"\n{HEADER_SEPARATOR}\n")
    if not separator:
        raise PromptFileError(f"{source}: missing a {HEADER_SEPARATOR!r} line after the header")
    header: Dict[str, str] = {}
    for number, line in enumerate(header_text.splitlines(), start=1):
        key, colon, value = line.partition(":")
        if not colon or not key.strip():
            raise PromptFileError(f"{source}: header line {number} is not 'key: value': {line!r}")
        header[key.strip()] = value.strip()
    for key in REQUIRED_KEYS:
        if not header.get(key):
            raise PromptFileError(f"{source}: header is missing {key!r}")
    parse_version(header["version"], source)
    return Prompt(header["name"], header["version"], body)


def load_prompts(directory: Path) -> List[Prompt]:
    prompts: Dict[str, Prompt] = {}
    for path in sorted(directory.glob(f"*{PROMPT_SUFFIX}")):
        prompt = parse_prompt(path.read_text(encoding="utf-8"), str(path))
        if prompt.name in prompts:
            raise PromptFileError(f"{path}: duplicate prompt name {prompt.name!r}")
        prompts[prompt.name] = prompt
    return list(prompts.values())
