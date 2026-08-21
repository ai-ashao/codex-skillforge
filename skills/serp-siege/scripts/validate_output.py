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
CLUSTER_TYPES = {
    "CORE",
    "FORMAT",
    "CONSTRAINT",
    "USE_CASE",
    "AUDIENCE",
    "PLATFORM",
    "ADJACENT_TOOL",
    "CONTENT_SUPPORT",
}
PRIORITIES = {"P0", "P1", "P2", "HOLD", "REJECT"}
FIRST_BATCH_GROUPS = {"CORE", "SUPPORTING", "ADJACENT"}
COMPETITOR_FEATURE_STATES = {"YES", "PARTIAL", "NO", "MISSING"}
CANDIDATE_FEATURE_STATES = {
    "EXISTING",
    "PLANNED",
    "OPTIONAL",
    "REJECTED",
    "MISSING",
}
SERP_STRENGTHS = {"LOW", "MEDIUM", "HIGH", "VERY_HIGH", "MISSING"}
GAPS = {"HIGH", "MEDIUM", "LOW", "MISSING"}
REUSE_POTENTIALS = {"HIGH", "MEDIUM", "LOW"}
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
    match = re.search(
        rf"\*\*{re.escape(label)}:\*\*\s*([^\n]+)", text, flags=re.MULTILINE
    )
    return match.group(1).strip().strip("`") if match else None


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


def evidence_labels(value: str) -> set[str]:
    label_text = value.split(":", 1)[0]
    return {part.strip().strip("`") for part in label_text.split("+")}


def validate_evidence_cell(
    value: str, context: str, errors: list[str], require_detail: bool = False
) -> None:
    labels = evidence_labels(value)
    invalid = labels - EVIDENCE_LABELS
    if invalid:
        errors.append(
            f"{context} has invalid evidence labels: "
            + ", ".join(sorted(invalid))
            + "."
        )
    if require_detail and labels and labels != {"MISSING"}:
        _, separator, detail = value.partition(":")
        if not separator or not detail.strip():
            errors.append(f"{context} requires a traceable source or observation.")


def validate_evidence(text: str, errors: list[str]) -> None:
    for deprecated in sorted(DEPRECATED_EVIDENCE_LABELS):
        if re.search(rf"(?<![A-Z_]){deprecated}(?![A-Z_])", text):
            errors.append(f"Deprecated evidence label found: {deprecated}.")

    for heading, evidence_index, minimum_columns, require_detail in (
        ("Assumptions", 1, 5, False),
        ("Competitor Map", 6, 7, True),
        ("Keyword Cluster Map", 7, 8, True),
        ("Feature Coverage Map", 6, 7, True),
        ("SERP Coverage Map", 3, 9, True),
        ("Execution Constraints & Missing Evidence", 3, 6, False),
    ):
        for index, row in enumerate(data_rows(text, heading), start=1):
            if len(row) < minimum_columns:
                errors.append(
                    f"{heading} row {index} has fewer than {minimum_columns} columns."
                )
                continue
            validate_evidence_cell(
                row[evidence_index],
                f"{heading} row {index}",
                errors,
                require_detail=require_detail,
            )


def validate_page_map(text: str, errors: list[str]) -> None:
    seen_clusters: set[str] = set()
    seen_urls: set[str] = set()
    for index, row in enumerate(data_rows(text, "SEO Page Map"), start=1):
        if len(row) < 9:
            errors.append(f"SEO Page Map row {index} has fewer than 9 columns.")
            continue
        decision, url, parent, cluster, _, _, shared_core, priority, reason = row[:9]
        if decision not in PAGE_DECISIONS:
            errors.append(f"SEO Page Map row {index} has invalid Page Decision.")
        if not cluster or cluster in {"-", "MISSING"}:
            errors.append(f"SEO Page Map row {index} is not bound to a target cluster.")
        elif cluster in seen_clusters:
            errors.append(f"SEO Page Map row {index} duplicates Target Cluster: {cluster}.")
        else:
            seen_clusters.add(cluster)
        if decision in NEW_PAGE_DECISIONS and (not url or url in {"-", "MISSING"}):
            errors.append(f"SEO Page Map row {index} requires Proposed URL.")
        if decision in NEW_PAGE_DECISIONS and parent not in {"", "-", "MISSING"}:
            errors.append(
                f"SEO Page Map new-page row {index} must not set Canonical Parent."
            )
        if url and url not in {"-", "MISSING"}:
            if url in seen_urls:
                errors.append(f"SEO Page Map row {index} duplicates Proposed URL: {url}.")
            else:
                seen_urls.add(url)
        if decision == "SAME_PAGE" and (not parent or parent in {"-", "MISSING"}):
            errors.append(f"SEO Page Map SAME_PAGE row {index} requires Canonical Parent.")
        if decision == "REJECT" and (not reason or reason in {"-", "MISSING"}):
            errors.append(f"SEO Page Map REJECT row {index} requires Reason.")
        if decision == "REJECT" and (not parent or parent in {"-", "MISSING"}):
            errors.append(
                f"SEO Page Map REJECT row {index} requires Canonical Parent."
            )
        if priority == "P0":
            if not shared_core or shared_core in {"-", "MISSING"}:
                errors.append(f"SEO Page Map P0 row {index} is missing Shared Core.")
            if not reason or reason in {"-", "MISSING"}:
                errors.append(f"SEO Page Map P0 row {index} is missing Reason.")
        if priority not in PRIORITIES:
            errors.append(f"SEO Page Map row {index} has invalid Priority.")


def validate_first_batch(text: str, errors: list[str]) -> None:
    groups: list[str] = []
    seen_clusters: set[str] = set()
    for index, row in enumerate(data_rows(text, "First Batch"), start=1):
        if len(row) < 6:
            errors.append(f"First Batch row {index} has fewer than 6 columns.")
            continue
        _, group, cluster, why_now, shared_capability, seo_role = row[:6]
        groups.append(group)
        if group not in FIRST_BATCH_GROUPS:
            errors.append(f"First Batch row {index} has invalid Group.")
        if not cluster or cluster in {"-", "MISSING"}:
            errors.append(f"First Batch row {index} is not bound to a target cluster.")
        elif cluster in seen_clusters:
            errors.append(f"First Batch row {index} duplicates Target Cluster: {cluster}.")
        else:
            seen_clusters.add(cluster)
        if not why_now or why_now in {"-", "MISSING"}:
            errors.append(f"First Batch row {index} is missing Why Now.")
        if not shared_capability or shared_capability in {"-", "MISSING"}:
            errors.append(f"First Batch row {index} is missing Shared Capability.")
        if not seo_role or seo_role in {"-", "MISSING"}:
            errors.append(f"First Batch row {index} is missing SEO Role.")

    if groups.count("CORE") != 1:
        errors.append("First Batch must contain exactly one CORE item.")

    total = len(groups)
    default_shape = (
        8 <= total <= 15
        and 3 <= groups.count("SUPPORTING") <= 5
        and 2 <= groups.count("ADJACENT") <= 5
    )
    deviation = extract_field(section_text(text, "First Batch"), "First Batch Deviation")
    if not default_shape and (not deviation or deviation.upper() == "NONE"):
        errors.append(
            "First Batch outside the default shape requires First Batch Deviation."
        )


def validate_keyword_map(text: str, errors: list[str]) -> None:
    seen_clusters: set[str] = set()
    for index, row in enumerate(data_rows(text, "Keyword Cluster Map"), start=1):
        if len(row) < 8:
            continue
        cluster, cluster_type, _, _, _, decision, priority, _ = row[:8]
        if not cluster or cluster in {"-", "MISSING"}:
            errors.append(f"Keyword Cluster Map row {index} requires Cluster.")
        elif cluster in seen_clusters:
            errors.append(
                f"Keyword Cluster Map row {index} duplicates Cluster: {cluster}."
            )
        else:
            seen_clusters.add(cluster)
        if cluster_type not in CLUSTER_TYPES:
            errors.append(f"Keyword Cluster Map row {index} has invalid Type.")
        if decision not in PAGE_DECISIONS:
            errors.append(f"Keyword Cluster Map row {index} has invalid Page Decision.")
        if priority not in PRIORITIES:
            errors.append(f"Keyword Cluster Map row {index} has invalid Priority.")


def validate_feature_map(text: str, errors: list[str]) -> None:
    for index, row in enumerate(data_rows(text, "Feature Coverage Map"), start=1):
        if len(row) < 7:
            continue
        competitor_states = row[1:4]
        candidate, priority, evidence = row[4:7]
        for state in competitor_states:
            if state not in COMPETITOR_FEATURE_STATES:
                errors.append(
                    f"Feature Coverage Map row {index} has invalid competitor state."
                )
                break
        if candidate not in CANDIDATE_FEATURE_STATES:
            errors.append(f"Feature Coverage Map row {index} has invalid Candidate state.")
        if priority not in PRIORITIES:
            errors.append(f"Feature Coverage Map row {index} has invalid Priority.")
        if candidate == "EXISTING" and not (
            evidence_labels(evidence) & {"FIRST_PARTY", "LIVE_PUBLIC_OBSERVATION"}
        ):
            errors.append(
                f"Feature Coverage Map row {index} marks Candidate EXISTING without first-party or live-public evidence."
            )


def validate_serp_map(text: str, errors: list[str]) -> None:
    seen_clusters: set[str] = set()
    for index, row in enumerate(data_rows(text, "SERP Coverage Map"), start=1):
        if len(row) < 9:
            continue
        cluster, _, _, _, strength, gap, reuse, _, priority = row[:9]
        if not cluster or cluster in {"-", "MISSING"}:
            errors.append(f"SERP Coverage Map row {index} requires Cluster.")
        elif cluster in seen_clusters:
            errors.append(f"SERP Coverage Map row {index} duplicates Cluster: {cluster}.")
        else:
            seen_clusters.add(cluster)
        if strength not in SERP_STRENGTHS:
            errors.append(f"SERP Coverage Map row {index} has invalid SERP Strength.")
        if gap not in GAPS:
            errors.append(f"SERP Coverage Map row {index} has invalid Gap.")
        if reuse not in REUSE_POTENTIALS:
            errors.append(f"SERP Coverage Map row {index} has invalid Reuse Potential.")
        if priority not in PRIORITIES:
            errors.append(f"SERP Coverage Map row {index} has invalid Priority.")


def rows_by_cluster(text: str, heading: str, cluster_index: int) -> dict[str, list[str]]:
    return {
        row[cluster_index]: row
        for row in data_rows(text, heading)
        if len(row) > cluster_index and row[cluster_index]
    }


def validate_cross_map_consistency(text: str, errors: list[str]) -> None:
    keyword = rows_by_cluster(text, "Keyword Cluster Map", 0)
    serp = rows_by_cluster(text, "SERP Coverage Map", 0)
    seo = rows_by_cluster(text, "SEO Page Map", 3)
    first_batch = rows_by_cluster(text, "First Batch", 2)

    for cluster, row in keyword.items():
        seo_row = seo.get(cluster)
        if not seo_row:
            errors.append(f"Keyword cluster {cluster} is missing from SEO Page Map.")
            continue
        if len(row) >= 7 and len(seo_row) >= 8:
            if row[5] != seo_row[0]:
                errors.append(f"Cluster {cluster} has inconsistent Page Decision.")
            if row[6] != seo_row[7]:
                errors.append(f"Cluster {cluster} has inconsistent Priority.")

    for cluster, row in serp.items():
        if cluster not in keyword:
            errors.append(f"SERP cluster {cluster} is missing from Keyword Cluster Map.")
        seo_row = seo.get(cluster)
        if not seo_row:
            errors.append(f"SERP cluster {cluster} is missing from SEO Page Map.")
            continue
        if len(row) >= 9 and len(seo_row) >= 8 and row[8] != seo_row[7]:
            errors.append(f"Cluster {cluster} has inconsistent SERP/SEO Priority.")
        if len(row) >= 8 and len(seo_row) >= 2:
            serp_url, seo_url = row[7], seo_row[1]
            if serp_url and seo_url and serp_url != seo_url:
                errors.append(f"Cluster {cluster} has inconsistent Proposed Page.")

    for cluster, row in seo.items():
        if row and row[0] != "REJECT" and cluster not in keyword:
            errors.append(f"SEO cluster {cluster} is missing from Keyword Cluster Map.")

    for cluster, row in first_batch.items():
        seo_row = seo.get(cluster)
        if not seo_row:
            errors.append(f"First Batch cluster {cluster} is missing from SEO Page Map.")
            continue
        if seo_row[7] != "P0":
            errors.append(f"First Batch cluster {cluster} must be P0 in SEO Page Map.")
        item = row[0]
        if item.startswith("/") and seo_row[1] and item != seo_row[1]:
            errors.append(f"First Batch cluster {cluster} has inconsistent URL.")

    for cluster, row in seo.items():
        if len(row) >= 8 and row[7] == "P0" and row[0] in NEW_PAGE_DECISIONS:
            if cluster not in first_batch:
                errors.append(f"SEO P0 cluster {cluster} is missing from First Batch.")

    for cluster, row in serp.items():
        if len(row) < 9 or row[8] != "P0":
            continue
        if row[4] == "MISSING" and row[5] == "MISSING":
            batch_row = first_batch.get(cluster)
            if batch_row and batch_row[1] != "CORE":
                errors.append(
                    f"SERP-missing P0 cluster {cluster} must be the First Batch CORE or move to HOLD."
                )


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

    for label in (
        "Selected direction",
        "Primary job",
        "Target scope",
        "Destination",
        "Destination Basis",
    ):
        if not extract_field(text, label):
            errors.append(f"Missing Execution Frame field: {label}.")

    destination = extract_field(text, "Destination")
    destination_basis = extract_field(text, "Destination Basis")
    if destination_basis:
        validate_evidence_cell(
            destination_basis,
            "Destination Basis",
            errors,
            require_detail=destination != "NOT_SUPPLIED",
        )
        basis_labels = evidence_labels(destination_basis)
        if destination == "NOT_SUPPLIED" and basis_labels != {"MISSING"}:
            errors.append("NOT_SUPPLIED Destination requires MISSING Destination Basis.")
        if destination != "NOT_SUPPLIED" and not (
            basis_labels & {"FIRST_PARTY", "USER_SUPPLIED_THIRD_PARTY"}
        ):
            errors.append(
                "Supplied Destination requires FIRST_PARTY or USER_SUPPLIED_THIRD_PARTY basis."
            )

    validate_evidence(text, errors)
    validate_keyword_map(text, errors)
    validate_feature_map(text, errors)
    validate_serp_map(text, errors)
    validate_page_map(text, errors)
    validate_first_batch(text, errors)
    validate_cross_map_consistency(text, errors)

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
