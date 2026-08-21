#!/usr/bin/env python3
"""Validate the structural contract of a SERP Siege execution report."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


EVIDENCE_LABELS = {
    "FIRST_PARTY",
    "USER_SUPPLIED_THIRD_PARTY",
    "LIVE_PUBLIC_OBSERVATION",
    "MODEL_INFERENCE",
    "MISSING",
}
DEPRECATED_EVIDENCE_LABELS = {
    "VERIFIED",
    "SUPPLIED_DATA",
    "PUBLIC_OBSERVATION",
    "INFERENCE",
}
PAGE_DECISIONS = {
    "SAME_PAGE",
    "NEW_LANDING_PAGE",
    "NEW_TOOL_PAGE",
    "CATEGORY_PAGE",
    "CONTENT_SUPPORT",
    "REJECT",
}
NEW_PAGE_DECISIONS = PAGE_DECISIONS - {"SAME_PAGE", "REJECT"}
REQUIRED_HEADINGS = {
    "Execution Frame",
    "Assumptions",
    "Search Landscape Summary",
    "Competitor Map",
    "Keyword Cluster Map",
    "Feature Coverage Map",
    "SERP Coverage Map",
    "SEO Page Map",
    "First Batch",
    "Product Roadmap",
    "MVP / P0",
    "P1",
    "P2",
    "Do Not Build Yet",
    "Execution Constraints & Missing Evidence",
    "Next Execution",
}
REQUIRED_NONEMPTY_TABLES = {
    "Assumptions",
    "Competitor Map",
    "Keyword Cluster Map",
    "Feature Coverage Map",
    "SERP Coverage Map",
    "SEO Page Map",
    "First Batch",
    "MVP / P0",
    "Execution Constraints & Missing Evidence",
}
FORBIDDEN_FIELDS = {
    "Decision",
    "Architecture",
    "Opportunity Score",
    "Separation Risk",
    "Hard Gates",
}


def normalize_heading(line: str) -> str:
    return re.sub(r"^#+\s*", "", line.strip()).strip()


def headings(text: str) -> set[str]:
    return {
        normalize_heading(line)
        for line in text.splitlines()
        if re.match(r"^#{2,3}\s+", line.strip())
    }


def extract_field(text: str, label: str) -> str | None:
    match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*`?([^\n`]+)", text)
    return match.group(1).strip() if match else None


def section_text(text: str, heading: str) -> str:
    match = re.search(
        rf"^#{{2,3}}\s+{re.escape(heading)}\s*$", text, flags=re.MULTILINE
    )
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^#{2,3}\s+", text[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def table_rows(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [cell.strip().strip("`") for cell in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def data_rows(text: str, heading: str) -> list[list[str]]:
    rows = table_rows(section_text(text, heading))
    return rows[1:] if rows else []


def validate_evidence_cell(value: str, context: str, errors: list[str]) -> None:
    labels = {part.strip() for part in value.split("+")}
    invalid = labels - EVIDENCE_LABELS
    if invalid:
        errors.append(
            f"{context} has invalid evidence labels: "
            + ", ".join(sorted(invalid))
            + "."
        )


def validate_evidence(text: str, errors: list[str]) -> None:
    for deprecated in sorted(DEPRECATED_EVIDENCE_LABELS):
        if re.search(rf"(?<![A-Z_]){deprecated}(?![A-Z_])", text):
            errors.append(f"Deprecated evidence label found: {deprecated}.")

    for heading, evidence_index, minimum_columns in (
        ("Assumptions", 1, 5),
        ("Execution Constraints & Missing Evidence", 3, 6),
    ):
        for index, row in enumerate(data_rows(text, heading), start=1):
            if len(row) < minimum_columns:
                errors.append(
                    f"{heading} row {index} has fewer than {minimum_columns} columns."
                )
                continue
            validate_evidence_cell(row[evidence_index], f"{heading} row {index}", errors)


def validate_page_map(text: str, errors: list[str]) -> None:
    for index, row in enumerate(data_rows(text, "SEO Page Map"), start=1):
        if len(row) < 9:
            errors.append(f"SEO Page Map row {index} has fewer than 9 columns.")
            continue
        decision, url, parent, cluster, _, _, shared_core, priority, reason = row[:9]
        if decision not in PAGE_DECISIONS:
            errors.append(f"SEO Page Map row {index} has invalid Page Decision.")
        if not cluster or cluster in {"-", "MISSING"}:
            errors.append(f"SEO Page Map row {index} is not bound to a target cluster.")
        if decision in NEW_PAGE_DECISIONS and (not url or url in {"-", "MISSING"}):
            errors.append(f"SEO Page Map row {index} requires Proposed URL.")
        if decision == "SAME_PAGE" and (not parent or parent in {"-", "MISSING"}):
            errors.append(f"SEO Page Map SAME_PAGE row {index} requires Canonical Parent.")
        if decision == "REJECT" and (not reason or reason in {"-", "MISSING"}):
            errors.append(f"SEO Page Map REJECT row {index} requires Reason.")
        if priority == "P0":
            if not shared_core or shared_core in {"-", "MISSING"}:
                errors.append(f"SEO Page Map P0 row {index} is missing Shared Core.")
            if not reason or reason in {"-", "MISSING"}:
                errors.append(f"SEO Page Map P0 row {index} is missing Reason.")


def validate_first_batch(text: str, errors: list[str]) -> None:
    for index, row in enumerate(data_rows(text, "First Batch"), start=1):
        if len(row) < 6:
            errors.append(f"First Batch row {index} has fewer than 6 columns.")
            continue
        _, _, cluster, why_now, shared_capability, seo_role = row[:6]
        if not cluster or cluster in {"-", "MISSING"}:
            errors.append(f"First Batch row {index} is not bound to a target cluster.")
        if not why_now or why_now in {"-", "MISSING"}:
            errors.append(f"First Batch row {index} is missing Why Now.")
        if not shared_capability or shared_capability in {"-", "MISSING"}:
            errors.append(f"First Batch row {index} is missing Shared Capability.")
        if not seo_role or seo_role in {"-", "MISSING"}:
            errors.append(f"First Batch row {index} is missing SEO Role.")


def validate_next_execution(text: str, errors: list[str]) -> None:
    section = section_text(text, "Next Execution").lower()
    fields = {
        "First action": ("first action", "第一项动作", "第一项开发前动作"),
        "Required evidence or prerequisite": ("required evidence", "prerequisite", "所需证据", "前置条件"),
        "Success condition": ("success condition", "成功条件"),
        "If it fails": ("if it fails", "失败时"),
        "First Batch re-evaluation trigger": ("re-evaluation trigger", "重新调整", "重新评估触发"),
    }
    for label, variants in fields.items():
        if not any(variant in section for variant in variants):
            errors.append(f"Next Execution is missing {label}.")


def validate(text: str) -> list[str]:
    errors: list[str] = []
    present = headings(text)

    for required in sorted(REQUIRED_HEADINGS - present):
        errors.append(f"Missing required heading: {required}.")

    for heading in sorted(REQUIRED_NONEMPTY_TABLES):
        if heading in present and not data_rows(text, heading):
            errors.append(f"{heading} must contain at least one data row.")

    for field in sorted(FORBIDDEN_FIELDS):
        if re.search(rf"\*\*{re.escape(field)}:\*\*", text):
            errors.append(f"Execution report must not contain field: {field}.")

    if re.search(r"(?<![A-Z_])(GO|CONDITIONAL_GO|NO_GO)(?![A-Z_])", text):
        errors.append("Execution report must not contain GO/NO_GO decisions.")

    confidence = extract_field(text, "Planning Confidence")
    if confidence not in {"HIGH", "MEDIUM", "LOW"}:
        errors.append("Missing or invalid Planning Confidence.")

    for label in ("Selected direction", "Primary job", "Target scope", "Destination"):
        if not extract_field(text, label):
            errors.append(f"Missing Execution Frame field: {label}.")

    validate_evidence(text, errors)
    validate_page_map(text, errors)
    validate_first_batch(text, errors)

    for index, row in enumerate(data_rows(text, "MVP / P0"), start=1):
        if len(row) < 4 or not row[3] or row[3] in {"-", "MISSING"}:
            errors.append(f"MVP / P0 row {index} is missing Reason.")

    validate_next_execution(text, errors)
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the structural contract of a SERP Siege execution report."
    )
    parser.add_argument("report", type=Path, help="Path to the Markdown report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.report.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: report not found: {args.report}", file=sys.stderr)
        return 2
    except UnicodeDecodeError as exc:
        print(f"error: report is not valid UTF-8: {exc}", file=sys.stderr)
        return 2

    errors = validate(text)
    if errors:
        print("SERP Siege execution report validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SERP Siege execution report validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
