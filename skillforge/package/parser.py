"""Parsers for portable Skill package files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable
from urllib.parse import unquote, urlsplit

import yaml


WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


class PackageParseError(ValueError):
    """A parse error with a stable machine-readable code."""

    def __init__(self, code: str, path: Path, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.message = message


@dataclass(frozen=True)
class SkillDocument:
    path: Path
    frontmatter: Dict[str, Any]
    body: str
    line_count: int


def load_yaml_mapping(path: Path, code_prefix: str) -> Dict[str, Any]:
    """Load a UTF-8 YAML file and require a mapping at the root."""

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PackageParseError(
            code_prefix + ".encoding", path, "File must be UTF-8: {}".format(exc)
        ) from exc
    except OSError as exc:
        raise PackageParseError(
            code_prefix + ".read", path, "Could not read file: {}".format(exc)
        ) from exc

    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise PackageParseError(
            code_prefix + ".yaml", path, "Invalid YAML: {}".format(exc)
        ) from exc
    if not isinstance(value, dict):
        raise PackageParseError(
            code_prefix + ".type", path, "YAML root must be a mapping."
        )
    return value


def parse_skill_document(path: Path) -> SkillDocument:
    """Parse ``SKILL.md`` frontmatter without interpreting its body."""

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PackageParseError(
            "skill.encoding", path, "SKILL.md must be UTF-8: {}".format(exc)
        ) from exc
    except OSError as exc:
        raise PackageParseError(
            "skill.read", path, "Could not read SKILL.md: {}".format(exc)
        ) from exc

    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise PackageParseError(
            "frontmatter.missing", path, "SKILL.md must begin with YAML frontmatter."
        )

    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        raise PackageParseError(
            "frontmatter.unclosed", path, "YAML frontmatter has no closing delimiter."
        )

    frontmatter_text = "".join(lines[1:closing_index])
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        raise PackageParseError(
            "frontmatter.yaml", path, "Invalid YAML frontmatter: {}".format(exc)
        ) from exc
    if not isinstance(frontmatter, dict):
        raise PackageParseError(
            "frontmatter.type", path, "YAML frontmatter must be a mapping."
        )

    return SkillDocument(
        path=path,
        frontmatter=frontmatter,
        body="".join(lines[closing_index + 1 :]),
        line_count=len(lines),
    )


def extract_markdown_destinations(markdown: str) -> Iterable[str]:
    """Yield inline Markdown link destinations outside code spans and fences."""

    text = _markdown_without_code(markdown)
    cursor = 0
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text[cursor] != "[":
            cursor += 1
            continue

        label_depth = 1
        position = cursor + 1
        escaped_label = False
        while position < len(text) and label_depth:
            character = text[position]
            if escaped_label:
                escaped_label = False
            elif character == "\\":
                escaped_label = True
            elif character == "[":
                label_depth += 1
            elif character == "]":
                label_depth -= 1
            position += 1
        if label_depth or position >= len(text) or text[position] != "(":
            cursor += 1
            continue

        position += 1
        raw = []
        depth = 0
        escaped = False
        while position < len(text):
            character = text[position]
            if escaped:
                raw.append(character)
                escaped = False
            elif character == "\\":
                raw.append(character)
                escaped = True
            elif character == "(":
                depth += 1
                raw.append(character)
            elif character == ")":
                if depth == 0:
                    break
                depth -= 1
                raw.append(character)
            else:
                raw.append(character)
            position += 1
        if position >= len(text):
            return
        destination = _first_destination("".join(raw).strip())
        if destination:
            yield destination
        cursor = position + 1


def _markdown_without_code(markdown: str) -> str:
    """Mask fenced blocks and inline code while preserving ordinary Markdown."""

    visible = []
    fence_marker = None
    for line in markdown.splitlines(keepends=True):
        stripped = line.lstrip()
        marker = None
        if stripped.startswith("```"):
            marker = "`"
        elif stripped.startswith("~~~"):
            marker = "~"
        if marker:
            if fence_marker is None:
                fence_marker = marker
            elif fence_marker == marker:
                fence_marker = None
            visible.append("\n" if line.endswith("\n") else "")
            continue
        if fence_marker is not None:
            visible.append("\n" if line.endswith("\n") else "")
            continue
        visible.append(_remove_inline_code(line))
    return "".join(visible)


def _remove_inline_code(line: str) -> str:
    output = []
    index = 0
    while index < len(line):
        if line[index] != "`":
            output.append(line[index])
            index += 1
            continue
        end_of_marker = index
        while end_of_marker < len(line) and line[end_of_marker] == "`":
            end_of_marker += 1
        marker = line[index:end_of_marker]
        closing = line.find(marker, end_of_marker)
        if closing < 0:
            output.append(marker)
            index = end_of_marker
        else:
            output.append(" " * (closing + len(marker) - index))
            index = closing + len(marker)
    return "".join(output)


def _first_destination(raw: str) -> str:
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    destination = []
    escaped = False
    for character in raw:
        if escaped:
            destination.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character.isspace():
            break
        else:
            destination.append(character)
    if escaped:
        destination.append("\\")
    return "".join(destination)


def is_external_destination(destination: str) -> bool:
    """Return whether a Markdown destination is not a local file reference."""

    if destination.startswith("#") or destination.startswith("//"):
        return True
    if WINDOWS_ABSOLUTE_RE.match(destination):
        return False
    parsed = urlsplit(destination)
    return bool(parsed.scheme or parsed.netloc)


def is_absolute_local_destination(destination: str) -> bool:
    """Recognize POSIX and Windows absolute local paths on any host OS."""

    return Path(destination).is_absolute() or bool(WINDOWS_ABSOLUTE_RE.match(destination))


def destination_path(destination: str) -> str:
    """Remove query and fragment components from a local destination."""

    encoded_path = destination.split("#", 1)[0].split("?", 1)[0]
    return unquote(encoded_path)
