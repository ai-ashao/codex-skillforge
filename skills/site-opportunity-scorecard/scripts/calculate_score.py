#!/usr/bin/env python3
"""Calculate opportunity and site-separation risk scores.

Input is a JSON object using the keys in assets/assessment-input-template.json.
The script validates every raw score as an integer or float from 0 to 5 and
prints a deterministic JSON result.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

OPPORTUNITY_WEIGHTS: dict[str, int] = {
    "independent_primary_keyword": 12,
    "serp_breakability": 15,
    "long_tail_expansion": 12,
    "user_use_case_difference": 12,
    "homepage_workflow_difference": 10,
    "independent_brand_reason": 10,
    "link_distribution_potential": 10,
    "independent_content_system": 9,
    "development_maintenance_economics": 5,
    "monetization_fit": 5,
}

RISK_WEIGHTS: dict[str, int] = {
    "keyword_overlap": 20,
    "search_intent_overlap": 20,
    "product_workflow_overlap": 15,
    "content_template_overlap": 15,
    "brand_positioning_ambiguity": 10,
    "link_authority_fragmentation": 10,
    "development_maintenance_fragmentation": 10,
}

SEARCH_KEYS = {
    "independent_primary_keyword",
    "serp_breakability",
    "long_tail_expansion",
}

PRODUCT_KEYS = {
    "user_use_case_difference",
    "homepage_workflow_difference",
    "independent_brand_reason",
}

VALID_CONFIDENCE = {"LOW", "MEDIUM", "HIGH"}
VALID_HARD_GATE_SCOPES = {"SITE_ONLY", "BLOCK_PRODUCT"}


class InputError(ValueError):
    """Raised when the assessment input is invalid."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise InputError("Top-level JSON value must be an object.")
    return data


def validate_scores(section: Any, weights: dict[str, int], section_name: str) -> dict[str, float]:
    if not isinstance(section, dict):
        raise InputError(f"'{section_name}' must be an object.")

    missing = [key for key in weights if key not in section]
    extra = [key for key in section if key not in weights]
    if missing:
        raise InputError(f"Missing {section_name} keys: {', '.join(missing)}")
    if extra:
        raise InputError(f"Unknown {section_name} keys: {', '.join(extra)}")

    validated: dict[str, float] = {}
    for key in weights:
        value = section[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError(f"'{section_name}.{key}' must be a number from 0 to 5.")
        value = float(value)
        if not 0 <= value <= 5:
            raise InputError(f"'{section_name}.{key}' must be between 0 and 5; got {value}.")
        validated[key] = value
    return validated


def weighted_breakdown(scores: dict[str, float], weights: dict[str, int]) -> dict[str, float]:
    return {key: round(scores[key] / 5.0 * weight, 1) for key, weight in weights.items()}


def exact_total(scores: dict[str, float], weights: dict[str, int]) -> float:
    return sum(scores[key] / 5.0 * weight for key, weight in weights.items())


def validate_hard_gates(value: Any) -> list[dict[str, str]]:
    """Normalize hard gates while keeping legacy string input usable.

    SITE_ONLY blocks a new domain but permits an existing-site recommendation.
    BLOCK_PRODUCT means the product itself cannot be recommended until resolved.
    """
    if not isinstance(value, list):
        raise InputError("'hard_gates' must be an array of strings or objects.")

    gates: list[dict[str, str]] = []
    for item in value:
        if isinstance(item, str):
            reason = item.strip()
            if reason:
                gates.append({"reason": reason, "scope": "SITE_ONLY"})
            continue

        if not isinstance(item, dict):
            raise InputError("Each hard gate must be a string or an object.")
        reason = item.get("reason")
        scope = item.get("scope")
        if not isinstance(reason, str) or not reason.strip():
            raise InputError("Each hard-gate object needs a non-empty 'reason'.")
        if not isinstance(scope, str) or scope.upper() not in VALID_HARD_GATE_SCOPES:
            valid = ", ".join(sorted(VALID_HARD_GATE_SCOPES))
            raise InputError(f"Each hard-gate object needs scope: {valid}.")
        gates.append({"reason": reason.strip(), "scope": scope.upper()})

    return gates


def choose_recommendation(
    opportunity_total: float,
    risk_total: float,
    opportunity_scores: dict[str, float],
    hard_gates: list[dict[str, str]],
    confidence: str,
) -> tuple[str, list[str]]:
    search_subtotal = sum(
        opportunity_scores[key] / 5.0 * OPPORTUNITY_WEIGHTS[key]
        for key in SEARCH_KEYS
    )
    product_subtotal = sum(
        opportunity_scores[key] / 5.0 * OPPORTUNITY_WEIGHTS[key]
        for key in PRODUCT_KEYS
    )

    reasons: list[str] = []

    product_blockers = [gate["reason"] for gate in hard_gates if gate["scope"] == "BLOCK_PRODUCT"]
    if product_blockers:
        reasons.append("A product-blocking hard gate is active.")
        reasons.append("Resolve the blocker before recommending any site architecture.")
        return "OBSERVE_OR_REJECT", reasons

    if hard_gates:
        reasons.append("One or more new-site hard gates are active.")
        if opportunity_total >= 60:
            reasons.append("Keep authority on the existing domain until the gate is resolved.")
            return "EXISTING_SITE_SECTION", reasons
        if opportunity_total >= 40:
            reasons.append("Validate with one focused existing-site page until the gate is resolved.")
            return "EXISTING_SITE_PAGE", reasons
        return "OBSERVE_OR_REJECT", reasons

    independent_conditions = {
        "opportunity_total": opportunity_total >= 75,
        "risk_total": risk_total <= 40,
        "search_subtotal": search_subtotal >= 26,
        "product_subtotal": product_subtotal >= 22,
        "primary_keyword": opportunity_scores["independent_primary_keyword"] >= 3,
        "workflow_difference": opportunity_scores["homepage_workflow_difference"] >= 3,
        "confidence": confidence in {"MEDIUM", "HIGH"},
    }

    if all(independent_conditions.values()):
        reasons.append("Opportunity, differentiation, and separation-risk gates support a new domain.")
        return "INDEPENDENT_SITE", reasons

    if opportunity_total >= 60:
        reasons.append("The opportunity is substantial but does not clear every independent-site gate.")
        if confidence == "LOW":
            reasons.append("Low confidence favors validation on the existing domain.")
        if risk_total > 40:
            reasons.append("Separation risk favors authority concentration.")
        return "EXISTING_SITE_SECTION", reasons

    if opportunity_total >= 40:
        reasons.append("The opportunity supports a focused page but not a durable independent site system.")
        return "EXISTING_SITE_PAGE", reasons

    reasons.append("The opportunity score is below the default build threshold.")
    return "OBSERVE_OR_REJECT", reasons


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    opportunity_scores = validate_scores(
        data.get("opportunity_scores"), OPPORTUNITY_WEIGHTS, "opportunity_scores"
    )
    risk_scores = validate_scores(data.get("risk_scores"), RISK_WEIGHTS, "risk_scores")

    hard_gates = validate_hard_gates(data.get("hard_gates", []))

    confidence = str(data.get("overall_confidence", "LOW")).upper()
    if confidence not in VALID_CONFIDENCE:
        raise InputError("'overall_confidence' must be LOW, MEDIUM, or HIGH.")

    opportunity_breakdown = weighted_breakdown(opportunity_scores, OPPORTUNITY_WEIGHTS)
    risk_breakdown = weighted_breakdown(risk_scores, RISK_WEIGHTS)
    opportunity_total = round(exact_total(opportunity_scores, OPPORTUNITY_WEIGHTS), 1)
    risk_total = round(exact_total(risk_scores, RISK_WEIGHTS), 1)

    search_subtotal = round(sum(opportunity_breakdown[key] for key in SEARCH_KEYS), 1)
    product_subtotal = round(sum(opportunity_breakdown[key] for key in PRODUCT_KEYS), 1)
    growth_subtotal = round(
        opportunity_breakdown["link_distribution_potential"]
        + opportunity_breakdown["independent_content_system"],
        1,
    )
    economics_subtotal = round(
        opportunity_breakdown["development_maintenance_economics"]
        + opportunity_breakdown["monetization_fit"],
        1,
    )

    recommendation, reasons = choose_recommendation(
        opportunity_total,
        risk_total,
        opportunity_scores,
        hard_gates,
        confidence,
    )

    return {
        "opportunity_score": opportunity_total,
        "separation_risk": risk_total,
        "overall_confidence": confidence,
        "recommendation": recommendation,
        "recommendation_reasons": reasons,
        "hard_gates": [gate["reason"] for gate in hard_gates],
        "hard_gate_scopes": hard_gates,
        "subtotals": {
            "search_opportunity": search_subtotal,
            "product_differentiation": product_subtotal,
            "independent_growth": growth_subtotal,
            "site_economics": economics_subtotal,
        },
        "opportunity_breakdown": opportunity_breakdown,
        "risk_breakdown": risk_breakdown,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate Site Opportunity Scorecard totals from JSON input."
    )
    parser.add_argument("input", type=Path, help="Path to assessment JSON.")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (enabled by default for terminals).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = calculate(load_json(args.input))
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    indent = 2 if args.pretty or sys.stdout.isatty() else None
    print(json.dumps(result, ensure_ascii=False, indent=indent, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
