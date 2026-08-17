"""Static, non-executing Skill package validator."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

from skillforge.models import ValidationResult

from .metadata import load_skillforge_metadata
from .parser import (
    PackageParseError,
    destination_path,
    extract_markdown_destinations,
    is_absolute_local_destination,
    is_external_destination,
    load_yaml_mapping,
    parse_skill_document,
)


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
SCRIPT_SUFFIXES = {".bash", ".js", ".mjs", ".py", ".sh", ".ts", ".zsh"}
SCRIPT_PATTERNS: Tuple[Tuple[str, str, re.Pattern[str], str], ...] = (
    (
        "script.remote_pipe",
        "error",
        re.compile(
            r"(?:curl|wget)\b[^\n|]*\|\s*(?:(?:/[\w.-]+)*/)?(?:ba|z)?sh\b",
            re.IGNORECASE,
        ),
        "Script downloads content and pipes it directly to a shell.",
    ),
    (
        "script.destructive_root",
        "error",
        re.compile(
            r"\brm\s+"
            r"(?=[^\n]*-[^\s\n]*r[^\s\n]*)"
            r"(?=[^\n]*-[^\s\n]*f[^\s\n]*)"
            r"[^\n]*\s/(?:\s|$)"
        ),
        "Script appears to recursively delete from the filesystem root.",
    ),
    (
        "script.privileged",
        "warning",
        re.compile(r"(^|\s)sudo(?:\s|$)", re.MULTILINE),
        "Script requests privileged execution.",
    ),
    (
        "script.installs_dependencies",
        "warning",
        re.compile(
            r"\b(?:pip3?|npm|pnpm|yarn|brew|apt(?:-get)?)\s+(?:install|add)\b",
            re.IGNORECASE,
        ),
        "Script installs dependencies; execution must remain an explicit action.",
    ),
)


def _unknown_keys(mapping: Dict[Any, Any], allowed: set) -> list:
    return sorted(
        (key for key in mapping if not isinstance(key, str) or key not in allowed),
        key=repr,
    )


def _display_keys(keys: list) -> str:
    return ", ".join(key if isinstance(key, str) else repr(key) for key in keys)


def _relative_display(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _validate_frontmatter(
    result: ValidationResult, frontmatter: Dict[str, Any], folder_name: str
) -> None:
    unknown = _unknown_keys(frontmatter, ALLOWED_FRONTMATTER_KEYS)
    if unknown:
        result.add(
            "frontmatter.unknown_fields",
            "error",
            "SKILL.md",
            "Unsupported frontmatter fields are present.",
            _display_keys(unknown),
        )

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        result.add(
            "frontmatter.name.missing",
            "error",
            "SKILL.md",
            "Frontmatter name must be a non-empty string.",
        )
    else:
        name = name.strip()
        result.name = name
        if len(name) > 64 or not NAME_RE.fullmatch(name):
            result.add(
                "frontmatter.name.invalid",
                "error",
                "SKILL.md",
                "Skill name must be at most 64 characters using lowercase letters, digits, and single hyphens.",
                name,
            )
        if name != folder_name:
            result.add(
                "package.folder_name_mismatch",
                "error",
                "SKILL.md",
                "Skill folder name must match frontmatter name.",
                "{} != {}".format(folder_name, name),
            )

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        result.add(
            "frontmatter.description.missing",
            "error",
            "SKILL.md",
            "Frontmatter description must be a non-empty string.",
        )
    else:
        description = description.strip()
        result.description = description
        if len(description) > 1024:
            result.add(
                "frontmatter.description.too_long",
                "error",
                "SKILL.md",
                "Description must not exceed 1024 characters.",
                "{} characters".format(len(description)),
            )
        elif len(description) < 20:
            result.add(
                "frontmatter.description.short",
                "warning",
                "SKILL.md",
                "Description may be too short to route the Skill reliably.",
                "{} characters".format(len(description)),
            )
        if "<" in description or ">" in description:
            result.add(
                "frontmatter.description.angle_brackets",
                "error",
                "SKILL.md",
                "Description must not contain angle brackets.",
            )


def _validate_markdown_links(
    result: ValidationResult, markdown: str, source: Path, skill_root: Path
) -> None:
    root = skill_root.resolve()
    for destination in extract_markdown_destinations(markdown):
        if is_external_destination(destination):
            continue
        local_text = destination_path(destination)
        if not local_text:
            continue
        raw_path = Path(local_text)
        resolved = (source.parent / raw_path).resolve()
        evidence = "{} -> {}".format(destination, resolved)
        if is_absolute_local_destination(local_text) or not _is_within(resolved, root):
            result.add(
                "link.path_escape",
                "error",
                _relative_display(source, skill_root),
                "Local Markdown links must remain inside the Skill root.",
                evidence,
            )
        elif not resolved.exists():
            result.add(
                "link.missing",
                "error",
                _relative_display(source, skill_root),
                "Referenced local file does not exist.",
                evidence,
            )


def _validate_agents_metadata(result: ValidationResult, path: Path) -> None:
    if not path.exists():
        return
    result.has_agents_metadata = True
    try:
        data = load_yaml_mapping(path, "agents")
    except PackageParseError as exc:
        result.add(exc.code, "error", "agents/openai.yaml", exc.message)
        return

    interface = data.get("interface")
    if not isinstance(interface, dict):
        result.add(
            "agents.interface",
            "error",
            "agents/openai.yaml",
            "agents/openai.yaml must contain an interface mapping.",
        )
        return
    for key in ("display_name", "short_description", "default_prompt"):
        value = interface.get(key)
        if value is not None and not isinstance(value, str):
            result.add(
                "agents.interface.{}".format(key),
                "error",
                "agents/openai.yaml",
                "interface.{} must be a string when present.".format(key),
            )
    prompt = interface.get("default_prompt")
    if isinstance(prompt, str) and result.name and "$" + result.name not in prompt:
        result.add(
            "agents.default_prompt.skill_reference",
            "warning",
            "agents/openai.yaml",
            "default_prompt should explicitly reference the Skill with a leading dollar sign.",
            result.name,
        )


def _iter_symlinks(root: Path) -> Iterable[Path]:
    for directory, dirnames, filenames in os.walk(str(root), followlinks=False):
        directory_path = Path(directory)
        for name in dirnames + filenames:
            candidate = directory_path / name
            if candidate.is_symlink():
                yield candidate


def _validate_symlinks(result: ValidationResult, skill_root: Path) -> None:
    root = skill_root.resolve()
    for link in _iter_symlinks(skill_root):
        resolved = link.resolve()
        display = _relative_display(link, skill_root)
        if not _is_within(resolved, root):
            result.add(
                "package.symlink_escape",
                "error",
                display,
                "Symbolic link resolves outside the Skill root.",
                str(resolved),
            )
        else:
            result.add(
                "package.symlink",
                "warning",
                display,
                "Symbolic links reduce package portability and require review.",
                str(resolved),
            )


def _scan_scripts(result: ValidationResult, skill_root: Path) -> None:
    scripts_root = skill_root / "scripts"
    if scripts_root.is_symlink() or not scripts_root.is_dir():
        return
    for path in _iter_package_files(scripts_root):
        if path.suffix and path.suffix.lower() not in SCRIPT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            result.add(
                "script.unreadable",
                "warning",
                _relative_display(path, skill_root),
                "Could not inspect script as UTF-8 text.",
                str(exc),
            )
            continue
        for code, severity, pattern, message in SCRIPT_PATTERNS:
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                result.add(
                    code,
                    severity,
                    _relative_display(path, skill_root),
                    message,
                    "line {}".format(line),
                )


def _iter_package_files(skill_root: Path) -> Iterable[Path]:
    """Yield stable package files while ignoring local OS and bytecode artifacts."""

    files = []
    for directory, dirnames, filenames in os.walk(str(skill_root), followlinks=False):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name != "__pycache__" and not (Path(directory) / name).is_symlink()
        )
        for name in sorted(filenames):
            path = Path(directory) / name
            if path.is_symlink() or name == ".DS_Store" or path.suffix == ".pyc":
                continue
            files.append(path)
    yield from sorted(files)


def validate_skill_package(skill_path: Path) -> ValidationResult:
    """Validate one Skill package statically and never execute its scripts."""

    supplied_path = Path(skill_path).expanduser()
    result = ValidationResult(skill_path=supplied_path.resolve())
    if not supplied_path.exists():
        result.add(
            "package.missing",
            "error",
            str(supplied_path),
            "Skill path does not exist.",
        )
        return result
    if not supplied_path.is_dir():
        result.add(
            "package.not_directory",
            "error",
            str(supplied_path),
            "Skill path must be a directory.",
        )
        return result

    skill_root = supplied_path.resolve()
    package_files = list(_iter_package_files(skill_root))
    result.files_checked = len(package_files)
    _validate_symlinks(result, skill_root)
    skill_md = skill_root / "SKILL.md"
    if not skill_md.is_file():
        result.add(
            "skill.missing", "error", "SKILL.md", "Skill package must contain SKILL.md."
        )
        return result

    if skill_md.is_symlink() and not _is_within(skill_md.resolve(), skill_root):
        return result

    try:
        document = parse_skill_document(skill_md)
    except PackageParseError as exc:
        result.add(exc.code, "error", "SKILL.md", exc.message)
        return result

    _validate_frontmatter(result, document.frontmatter, skill_root.name)
    if not document.body.strip():
        result.add(
            "skill.body.empty",
            "error",
            "SKILL.md",
            "SKILL.md must contain instructions after frontmatter.",
        )
    if document.line_count > 500:
        result.add(
            "skill.size.lines",
            "warning",
            "SKILL.md",
            "SKILL.md exceeds the recommended 500-line context budget.",
            "{} lines".format(document.line_count),
        )

    for markdown_path in (path for path in package_files if path.suffix.lower() == ".md"):
        if markdown_path == skill_md:
            markdown = document.body
        else:
            try:
                markdown = markdown_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                result.add(
                    "markdown.unreadable",
                    "warning",
                    _relative_display(markdown_path, skill_root),
                    "Could not inspect Markdown file as UTF-8 text.",
                    str(exc),
                )
                continue
        _validate_markdown_links(result, markdown, markdown_path, skill_root)

    agents_path = skill_root / "agents" / "openai.yaml"
    if _is_within(agents_path.resolve(), skill_root):
        _validate_agents_metadata(result, agents_path)

    config_path = skill_root / "skillforge.yaml"
    if config_path.exists() and _is_within(config_path.resolve(), skill_root):
        result.has_skillforge_metadata = True
        _, findings = load_skillforge_metadata(config_path, skill_root, result.name)
        result.findings.extend(findings)

    _scan_scripts(result, skill_root)
    result.findings.sort(key=lambda item: (item.severity, item.path, item.code))
    return result
