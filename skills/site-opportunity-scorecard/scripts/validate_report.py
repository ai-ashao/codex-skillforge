#!/usr/bin/env python3
"""Validate the structural completeness of a scorecard Markdown report."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LANGUAGE_PROFILES = {
    "zh": {
        "headings": [
            "执行结论", "决策依据", "评分明细", "拆站风险", "关键词簇", "SERP突破口",
            "推荐首页切入点", "页面矩阵", "外链与分发路径", "商业化与维护", "最小验证方案", "最终决策",
        ],
        "terms": ["机会评分", "拆站风险", "数据置信度", "推荐架构"],
        "score_patterns": {
            "opportunity score": r"机会评分[^\n]{0,20}(?:\d{1,3}(?:\.\d+)?)\s*/\s*100",
            "separation risk": r"拆站风险[^\n]{0,20}(?:\d{1,3}(?:\.\d+)?)\s*/\s*100",
        },
    },
    "en": {
        "headings": [
            "Executive conclusion", "Decision basis", "Score details", "Separation risk", "Keyword cluster", "SERP entry point",
            "Recommended homepage entry point", "Page matrix", "Link and distribution paths", "Monetization and maintenance",
            "Minimum validation plan", "Final decision",
        ],
        "terms": ["Opportunity score", "Separation risk", "Evidence confidence", "Recommended architecture"],
        "score_patterns": {
            "opportunity score": r"opportunity score[^\n]{0,20}(?:\d{1,3}(?:\.\d+)?)\s*/\s*100",
            "separation risk": r"separation risk[^\n]{0,20}(?:\d{1,3}(?:\.\d+)?)\s*/\s*100",
        },
    },
}

VALID_RECOMMENDATIONS = {
    "zh": ["独立网站", "现有站专区", "现有站单页面", "观察或放弃"],
    "en": ["INDEPENDENT_SITE", "EXISTING_SITE_SECTION", "EXISTING_SITE_PAGE", "OBSERVE_OR_REJECT"],
}


def normalize_heading(text: str) -> str:
    return re.sub(r"^[#\s\d.、-]+", "", text).strip()


def detect_language(text: str) -> str:
    chinese_matches = sum(term in text for term in LANGUAGE_PROFILES["zh"]["terms"])
    english_matches = sum(term.lower() in text.lower() for term in LANGUAGE_PROFILES["en"]["terms"])
    return "zh" if chinese_matches >= english_matches else "en"


def validate(text: str, language: str = "auto") -> list[str]:
    errors: list[str] = []
    if language == "auto":
        language = detect_language(text)
    profile = LANGUAGE_PROFILES[language]
    headings = [
        normalize_heading(line)
        for line in text.splitlines()
        if line.lstrip().startswith("#")
    ]

    for required in profile["headings"]:
        if not any(required.lower() in heading.lower() for heading in headings):
            errors.append(f"Missing required heading: {required}")

    for term in profile["terms"]:
        if term.lower() not in text.lower():
            errors.append(f"Missing required field: {term}")

    if not any(term in text for term in VALID_RECOMMENDATIONS[language]):
        errors.append("No valid architecture recommendation found.")

    for label, pattern in profile["score_patterns"].items():
        if not re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"Missing or malformed {label} value (expected N/100).")

    if "|" not in text or text.count("|") < 20:
        errors.append("Expected score/risk tables appear to be missing or incomplete.")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a scorecard Markdown report.")
    parser.add_argument("report", type=Path, help="Path to the Markdown report.")
    parser.add_argument(
        "--lang",
        choices=("auto", "zh", "en"),
        default="auto",
        help="Report language; auto detects the template from required fields (default: auto).",
    )
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

    errors = validate(text, args.lang)
    if errors:
        print("Report validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Report validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
