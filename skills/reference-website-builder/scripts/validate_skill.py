#!/usr/bin/env python3
from __future__ import annotations

import re
import stat
import sys
from pathlib import Path

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "AGENTS_SNIPPET.md",
    "CODEX_REVIEW_PROMPT.md",
    "CHANGELOG.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "references/inspection-guide.md",
    "references/integration-guide.md",
    "references/qa-guide.md",
    "references/rights-and-provenance.md",
    "references/temporary-assets-guide.md",
    "templates/project-context.md",
    "templates/reference-matrix.md",
    "templates/page-topology.md",
    "templates/behaviors.md",
    "templates/original-design-brief.md",
    "templates/implementation-plan.md",
    "templates/component-spec.md",
    "templates/asset-manifest.json",
    "templates/asset-provenance.md",
    "templates/reference-assets.ts",
    "templates/replacement-checklist.md",
    "templates/qa-report.md",
    "scripts/install.sh",
    "scripts/check-reference-assets.mjs",
]


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def main() -> int:
    root = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            fail(f"Missing required file: {rel}", errors)

    skill_path = root / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        meta = parse_frontmatter(text)
        name = meta.get("name", "")
        description = meta.get("description", "")

        if not name:
            fail("SKILL.md frontmatter is missing name", errors)
        if not description:
            fail("SKILL.md frontmatter is missing description", errors)
        if name and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            fail("Skill name must use lowercase letters, digits, and single hyphens", errors)
        if name and root.name != name:
            fail(f"Folder name '{root.name}' does not match skill name '{name}'", errors)
        if len(name) > 64:
            fail("Skill name exceeds 64 characters", errors)
        if len(description) > 1024:
            fail("Skill description exceeds 1024 characters", errors)
        if "<" in name or ">" in name:
            fail("Skill name contains angle brackets", errors)

        line_count = len(text.splitlines())
        if line_count > 500:
            warnings.append(f"SKILL.md has {line_count} lines; consider moving more detail to references")

        linked = set(re.findall(r"`((?:references|templates|examples|scripts)/[^`\n]+)`", text))
        for rel in sorted(linked):
            if any(ch in rel for ch in "*<>"):
                continue
            if not (root / rel).exists():
                fail(f"SKILL.md references a missing resource: {rel}", errors)

        required_phrases = [
            "PRODUCTION_READY=false",
            "public/__reference__/",
            "asset-manifest.json",
            "check-reference-assets.mjs",
            "Do not crawl the sitemap",
        ]
        for phrase in required_phrases:
            if phrase not in text:
                fail(f"SKILL.md is missing required workflow phrase: {phrase}", errors)

    installer = root / "scripts/install.sh"
    if installer.is_file():
        mode = installer.stat().st_mode
        if not (mode & stat.S_IXUSR):
            warnings.append("scripts/install.sh is not executable; it can still be run with bash")
        shell = installer.read_text(encoding="utf-8")
        dangerous = [
            r"curl\s+[^\n|]+\|\s*(?:sh|bash)",
            r"wget\s+[^\n|]+\|\s*(?:sh|bash)",
            r"rm\s+-rf\s+[/$~]",
            r"git\s+reset\s+--hard",
            r"git\s+clean\s+-[a-zA-Z]*f",
        ]
        for pattern in dangerous:
            if re.search(pattern, shell):
                fail(f"Potentially dangerous installer pattern: {pattern}", errors)

    gate = root / "scripts/check-reference-assets.mjs"
    if gate.is_file():
        gate_text = gate.read_text(encoding="utf-8")
        if "process.exit(1)" not in gate_text:
            fail("Production gate script does not appear to fail on blockers", errors)
        dangerous_gate = [
            r"rmSync\(",
            r"unlinkSync\(",
            r"writeFileSync\(",
            r"fetch\(",
            r"https?\.request\(",
            r"child_process",
        ]
        for pattern in dangerous_gate:
            if re.search(pattern, gate_text):
                fail(f"Production gate must be read-only; found pattern: {pattern}", errors)

    print(f"Validating: {root}")
    if warnings:
        print("Warnings:")
        for item in warnings:
            print(f"  - {item}")
    if errors:
        print("Errors:")
        for item in errors:
            print(f"  - {item}")
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
