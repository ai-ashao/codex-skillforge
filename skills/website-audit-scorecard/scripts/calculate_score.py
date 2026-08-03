#!/usr/bin/env python3
"""Calculate a reproducible website audit score from rubric ratings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

CRITERIA: dict[str, tuple[str, float]] = {
    "PV1": ("Product and value proposition", 4),
    "PV2": ("Product and value proposition", 4),
    "PV3": ("Product and value proposition", 3),
    "PV4": ("Product and value proposition", 2),
    "PV5": ("Product and value proposition", 2),
    "UX1": ("Core task and UX", 3),
    "UX2": ("Core task and UX", 3),
    "UX3": ("Core task and UX", 2),
    "UX4": ("Core task and UX", 4),
    "UX5": ("Core task and UX", 4),
    "UX6": ("Core task and UX", 2),
    "UX7": ("Core task and UX", 2),
    "TS1": ("Trust, safety, and compliance", 4),
    "TS2": ("Trust, safety, and compliance", 3),
    "TS3": ("Trust, safety, and compliance", 3),
    "TS4": ("Trust, safety, and compliance", 3),
    "TS5": ("Trust, safety, and compliance", 2),
    "SEO1": ("SEO and indexability", 3),
    "SEO2": ("SEO and indexability", 3),
    "SEO3": ("SEO and indexability", 3),
    "SEO4": ("SEO and indexability", 3),
    "SEO5": ("SEO and indexability", 3),
    "CO1": ("Content and originality", 4),
    "CO2": ("Content and originality", 2),
    "CO3": ("Content and originality", 2),
    "CO4": ("Content and originality", 2),
    "PA1": ("Performance and accessibility", 4),
    "PA2": ("Performance and accessibility", 3),
    "PA3": ("Performance and accessibility", 2),
    "PA4": ("Performance and accessibility", 1),
    "TR1": ("Technical reliability", 2),
    "TR2": ("Technical reliability", 3),
    "TR3": ("Technical reliability", 2),
    "TR4": ("Technical reliability", 2),
    "TR5": ("Technical reliability", 1),
    "MR1": ("Monetization readiness", 2),
    "MR2": ("Monetization readiness", 1),
    "MR3": ("Monetization readiness", 1),
    "MR4": ("Monetization readiness", 1),
}

CATEGORY_MAX: dict[str, float] = {}
for _, (category, max_points) in CRITERIA.items():
    CATEGORY_MAX[category] = CATEGORY_MAX.get(category, 0) + max_points

EVIDENCE_MULTIPLIERS = {"A": 1.0, "B": 0.85, "C": 0.60}
GATE_CAPS = {"G1": 49.0, "G2": 39.0, "G3": 29.0, "G4": 59.0}
KNOWN_GATES = {"G0", "G1", "G2", "G3", "G4", "G5"}


def fail(message: str) -> None:
    raise ValueError(message)


def round1(value: float) -> float:
    return round(value + 1e-12, 1)


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    ratings = payload.get("ratings")
    if not isinstance(ratings, dict):
        fail("'ratings' must be an object")

    unknown = sorted(set(ratings) - set(CRITERIA))
    if unknown:
        fail(f"Unknown criterion IDs: {', '.join(unknown)}")

    earned = 0.0
    assessed_max = 0.0
    confidence_points = 0.0
    category_data: dict[str, dict[str, float]] = {
        category: {"earned": 0.0, "assessed_max": 0.0, "max": max_points}
        for category, max_points in CATEGORY_MAX.items()
    }
    criterion_results: dict[str, Any] = {}

    for criterion_id, (category, max_points) in CRITERIA.items():
        item = ratings.get(criterion_id, {"status": "unassessed"})
        if not isinstance(item, dict):
            fail(f"{criterion_id} must be an object")

        status = item.get("status")
        if status == "unassessed":
            if "rating" in item or "evidence" in item:
                fail(f"{criterion_id} cannot include rating or evidence when unassessed")
            criterion_results[criterion_id] = {
                "status": "unassessed",
                "max_points": max_points,
                "note": item.get("note", ""),
            }
            continue

        if status not in (None, "assessed"):
            fail(f"{criterion_id}.status must be 'assessed' or 'unassessed'")
        if "rating" not in item:
            fail(f"{criterion_id} must include rating or status 'unassessed'")

        rating = item["rating"]
        if isinstance(rating, bool) or not isinstance(rating, int) or not 0 <= rating <= 4:
            fail(f"{criterion_id}.rating must be an integer from 0 to 4")

        evidence = item.get("evidence")
        if evidence not in EVIDENCE_MULTIPLIERS:
            fail(f"{criterion_id}.evidence must be A, B, or C")

        points = max_points * rating / 4
        assessed_max += max_points
        earned += points
        confidence_points += max_points * EVIDENCE_MULTIPLIERS[evidence]

        category_data[category]["earned"] += points
        category_data[category]["assessed_max"] += max_points

        criterion_results[criterion_id] = {
            "status": "assessed",
            "rating": rating,
            "evidence": evidence,
            "points": round1(points),
            "max_points": max_points,
            "note": item.get("note", ""),
        }

    coverage = assessed_max
    confidence = confidence_points

    gates = payload.get("gates", [])
    if not isinstance(gates, list):
        fail("'gates' must be an array")

    triggered: list[dict[str, Any]] = []
    not_scorable = assessed_max < 40

    seen_gates: set[str] = set()
    for gate in gates:
        if not isinstance(gate, dict):
            fail("Each gate must be an object")
        gate_id = gate.get("id")
        if not isinstance(gate_id, str) or gate_id not in KNOWN_GATES:
            fail(f"Unknown gate ID: {gate_id}")
        if gate_id in seen_gates:
            fail(f"Duplicate gate ID: {gate_id}")
        seen_gates.add(gate_id)
        if not isinstance(gate.get("triggered"), bool):
            fail(f"{gate_id}.triggered must be true or false")
        if gate["triggered"] is not True:
            continue
        if gate_id == "G0":
            not_scorable = True
        triggered.append(
            {
                "id": gate_id,
                "cap": GATE_CAPS.get(gate_id),
                "note": gate.get("note", ""),
            }
        )

    if assessed_max == 0:
        raw_score = None
        final_score = None
        not_scorable = True
    else:
        raw_score_value = earned / assessed_max * 100
        raw_score = round1(raw_score_value)
        caps = [g["cap"] for g in triggered if g.get("cap") is not None]
        final_value = min([raw_score_value, *caps]) if caps else raw_score_value
        final_score = None if not_scorable else round1(final_value)

    category_results: dict[str, Any] = {}
    for category, values in category_data.items():
        category_assessed = values["assessed_max"]
        category_results[category] = {
            "earned_points": round1(values["earned"]),
            "assessed_max_points": round1(category_assessed),
            "category_max_points": round1(values["max"]),
            "normalized_score": (
                round1(values["earned"] / category_assessed * 100)
                if category_assessed
                else None
            ),
            "coverage": round1(category_assessed / values["max"] * 100),
        }

    label = (
        "not scorable"
        if not_scorable
        else "provisional"
        if coverage < 70
        else "final"
    )

    monetization_assessed = category_data["Monetization readiness"]["assessed_max"] > 0
    monetization_status = (
        "not ready"
        if any(g["id"] == "G5" for g in triggered)
        else "assessed"
        if monetization_assessed
        else "unassessed"
    )

    return {
        "audit": payload.get("audit", {}),
        "raw_score": raw_score,
        "final_score": final_score,
        "coverage": round1(coverage),
        "confidence": round1(confidence),
        "label": label,
        "monetization_status": monetization_status,
        "earned_points": round1(earned),
        "assessed_max_points": round1(assessed_max),
        "triggered_gates": triggered,
        "categories": category_results,
        "criteria": criterion_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Path to audit JSON")
    parser.add_argument(
        "-o", "--output", type=Path, help="Optional output JSON path"
    )
    args = parser.parse_args()

    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = calculate(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
