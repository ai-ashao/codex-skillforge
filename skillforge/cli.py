"""Minimal SkillForge command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from . import __version__
from .models import ValidationResult
from .package import validate_skill_package


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python3 -m skillforge")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="statically validate a Skill package")
    validate.add_argument("skill_path", type=Path)
    validate.add_argument(
        "--format", choices=("text", "json"), default="text", dest="output_format"
    )
    return parser


def _render_text(result: ValidationResult) -> str:
    status = "PASS" if result.valid else "FAIL"
    lines = ["{} {}".format(status, result.skill_path)]
    for finding in result.findings:
        line = "[{}] {} {}: {}".format(
            finding.severity.upper(), finding.code, finding.path, finding.message
        )
        if finding.evidence:
            line += " Evidence: {}".format(finding.evidence)
        lines.append(line)
    summary = result.summary()
    lines.append(
        "Summary: {errors} error(s), {warnings} warning(s), {infos} info finding(s); {files} file(s) checked.".format(
            files=result.files_checked, **summary
        )
    )
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command != "validate":
        parser.error("unsupported command")

    try:
        result = validate_skill_package(args.skill_path)
        if args.output_format == "json":
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(_render_text(result))
        return 0 if result.valid else 1
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print("SkillForge internal error: {}".format(exc), file=sys.stderr)
        return 3

