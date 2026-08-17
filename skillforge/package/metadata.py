"""Parser and validation rules for optional ``skillforge.yaml`` metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from skillforge.models import Finding

from .parser import PackageParseError, load_yaml_mapping


ALLOWED_TOP_LEVEL_KEYS = {
    "schema_version",
    "skill",
    "validation",
    "evals",
    "baseline",
    "review",
}
SKILL_TYPES = {"deterministic", "procedural", "hybrid"}
EVAL_KEYS = {"triggers", "behavior", "rubric"}
SKILL_KEYS = {"name", "type"}
VALIDATION_KEYS = {"commands"}
COMMAND_KEYS = {"id", "argv", "timeout_seconds"}
BASELINE_KEYS = {"mode", "ref"}
BASELINE_MODES = {"git-parent", "explicit"}
REVIEW_KEYS = {"checks"}
REVIEW_CHECKS = {
    "package",
    "resources",
    "scripts",
    "safety",
    "evidence",
    "triggers",
}


def _unknown_keys(mapping: Dict[Any, Any], allowed: set) -> List[Any]:
    return sorted(
        (key for key in mapping if not isinstance(key, str) or key not in allowed),
        key=repr,
    )


def _display_keys(keys: List[Any]) -> str:
    return ", ".join(key if isinstance(key, str) else repr(key) for key in keys)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _finding(
    code: str, path: Path, message: str, evidence: Optional[str] = None
) -> Finding:
    return Finding(code, "error", path.name, message, evidence)


def load_skillforge_metadata(
    config_path: Path, skill_root: Path, expected_name: Optional[str]
) -> Tuple[Optional[Dict[str, Any]], List[Finding]]:
    """Load and validate v1 SkillForge metadata without executing commands."""

    findings: List[Finding] = []
    try:
        data = load_yaml_mapping(config_path, "config")
    except PackageParseError as exc:
        return None, [_finding(exc.code, exc.path, exc.message)]

    unknown = _unknown_keys(data, ALLOWED_TOP_LEVEL_KEYS)
    if unknown:
        findings.append(
            _finding(
                "config.unknown_fields",
                config_path,
                "Unknown top-level fields are not valid for schema version 1.",
                _display_keys(unknown),
            )
        )

    schema_version = data.get("schema_version")
    if (
        not isinstance(schema_version, int)
        or isinstance(schema_version, bool)
        or schema_version != 1
    ):
        findings.append(
            _finding(
                "config.schema_version",
                config_path,
                "schema_version must be the integer 1.",
                repr(data.get("schema_version")),
            )
        )

    skill = data.get("skill")
    if not isinstance(skill, dict):
        findings.append(
            _finding("config.skill", config_path, "skill must be a mapping.")
        )
    else:
        unknown_skill = _unknown_keys(skill, SKILL_KEYS)
        if unknown_skill:
            findings.append(
                _finding(
                    "config.skill.unknown_fields",
                    config_path,
                    "Unknown skill fields are not valid for schema version 1.",
                    _display_keys(unknown_skill),
                )
            )
        config_name = skill.get("name")
        if not isinstance(config_name, str) or not config_name.strip():
            findings.append(
                _finding(
                    "config.skill.name", config_path, "skill.name must be a non-empty string."
                )
            )
        elif expected_name and config_name != expected_name:
            findings.append(
                _finding(
                    "config.skill.name_mismatch",
                    config_path,
                    "skill.name must match SKILL.md frontmatter.",
                    "{} != {}".format(config_name, expected_name),
                )
            )
        skill_type = skill.get("type")
        if skill_type is not None and (
            not isinstance(skill_type, str) or skill_type not in SKILL_TYPES
        ):
            findings.append(
                _finding(
                    "config.skill.type",
                    config_path,
                    "skill.type must be deterministic, procedural, or hybrid.",
                    repr(skill_type),
                )
            )

    validation = data.get("validation")
    if validation is not None:
        if not isinstance(validation, dict):
            findings.append(
                _finding(
                    "config.validation", config_path, "validation must be a mapping."
                )
            )
        else:
            unknown_validation = _unknown_keys(validation, VALIDATION_KEYS)
            if unknown_validation:
                findings.append(
                    _finding(
                        "config.validation.unknown_fields",
                        config_path,
                        "Unknown validation fields are not valid for schema version 1.",
                        _display_keys(unknown_validation),
                    )
                )
            commands = validation.get("commands", [])
            if not isinstance(commands, list):
                findings.append(
                    _finding(
                        "config.validation.commands",
                        config_path,
                        "validation.commands must be a list.",
                    )
                )
            else:
                for index, command in enumerate(commands):
                    if not isinstance(command, dict):
                        findings.append(
                            _finding(
                                "config.validation.command",
                                config_path,
                                "Each validation command must be a mapping with an argv list; shell strings are not accepted.",
                                "index {}".format(index),
                            )
                        )
                        continue
                    unknown_command = _unknown_keys(command, COMMAND_KEYS)
                    if unknown_command:
                        findings.append(
                            _finding(
                                "config.validation.command.unknown_fields",
                                config_path,
                                "Unknown validation command fields are not valid for schema version 1.",
                                "index {}: {}".format(index, _display_keys(unknown_command)),
                            )
                        )
                    command_id = command.get("id")
                    if command_id is not None and (
                        not isinstance(command_id, str) or not command_id
                    ):
                        findings.append(
                            _finding(
                                "config.validation.id",
                                config_path,
                                "validation command id must be a non-empty string when present.",
                                "index {}".format(index),
                            )
                        )
                    argv = command.get("argv")
                    if (
                        not isinstance(argv, list)
                        or not argv
                        or not all(isinstance(item, str) and item for item in argv)
                    ):
                        findings.append(
                            _finding(
                                "config.validation.argv",
                                config_path,
                                "validation command argv must be a non-empty list of strings.",
                                "index {}".format(index),
                            )
                        )
                    timeout = command.get("timeout_seconds")
                    if timeout is not None and (
                        not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0
                    ):
                        findings.append(
                            _finding(
                                "config.validation.timeout",
                                config_path,
                                "timeout_seconds must be a positive integer.",
                                "index {}".format(index),
                            )
                        )

    evals = data.get("evals")
    if evals is not None:
        if not isinstance(evals, dict):
            findings.append(
                _finding("config.evals", config_path, "evals must be a mapping.")
            )
        else:
            unknown_evals = _unknown_keys(evals, EVAL_KEYS)
            if unknown_evals:
                findings.append(
                    _finding(
                        "config.evals.unknown_fields",
                        config_path,
                        "Unknown eval fields are not valid for schema version 1.",
                        _display_keys(unknown_evals),
                    )
                )
            root = skill_root.resolve()
            for key in EVAL_KEYS:
                value = evals.get(key)
                if value is None:
                    continue
                if not isinstance(value, str) or not value:
                    findings.append(
                        _finding(
                            "config.evals.path", config_path, "eval paths must be strings.", key
                        )
                    )
                    continue
                raw_path = Path(value)
                resolved = (skill_root / raw_path).resolve()
                if "://" in value or raw_path.is_absolute() or not _is_within(resolved, root):
                    findings.append(
                        _finding(
                            "config.evals.path_escape",
                            config_path,
                            "eval paths must remain inside the Skill root.",
                            "{}={}".format(key, value),
                        )
                    )
                elif not resolved.is_file():
                    findings.append(
                        _finding(
                            "config.evals.missing",
                            config_path,
                            "Configured eval file does not exist.",
                            "{}={}".format(key, value),
                        )
                    )

    baseline = data.get("baseline")
    if baseline is not None:
        if not isinstance(baseline, dict):
            findings.append(
                _finding("config.baseline", config_path, "baseline must be a mapping.")
            )
        else:
            unknown_baseline = _unknown_keys(baseline, BASELINE_KEYS)
            if unknown_baseline:
                findings.append(
                    _finding(
                        "config.baseline.unknown_fields",
                        config_path,
                        "Unknown baseline fields are not valid for schema version 1.",
                        _display_keys(unknown_baseline),
                    )
                )
            mode = baseline.get("mode")
            if not isinstance(mode, str) or mode not in BASELINE_MODES:
                findings.append(
                    _finding(
                        "config.baseline.mode",
                        config_path,
                        "baseline.mode must be git-parent or explicit.",
                        repr(mode),
                    )
                )
            ref = baseline.get("ref")
            if mode == "explicit" and (not isinstance(ref, str) or not ref):
                findings.append(
                    _finding(
                        "config.baseline.ref",
                        config_path,
                        "An explicit baseline requires a non-empty ref string.",
                    )
                )
            elif ref is not None and (not isinstance(ref, str) or not ref):
                findings.append(
                    _finding(
                        "config.baseline.ref",
                        config_path,
                        "baseline.ref must be a non-empty string when present.",
                    )
                )

    review = data.get("review")
    if review is not None:
        if not isinstance(review, dict):
            findings.append(
                _finding("config.review", config_path, "review must be a mapping.")
            )
        else:
            unknown_review = _unknown_keys(review, REVIEW_KEYS)
            if unknown_review:
                findings.append(
                    _finding(
                        "config.review.unknown_fields",
                        config_path,
                        "Unknown review fields are not valid for schema version 1.",
                        _display_keys(unknown_review),
                    )
                )
            checks = review.get("checks", [])
            if not isinstance(checks, list) or not all(
                isinstance(check, str) and check in REVIEW_CHECKS for check in checks
            ):
                findings.append(
                    _finding(
                        "config.review.checks",
                        config_path,
                        "review.checks must contain only supported check names.",
                    )
                )

    return data, findings
