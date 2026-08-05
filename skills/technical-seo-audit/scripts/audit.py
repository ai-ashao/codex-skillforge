#!/usr/bin/env python3
"""Run the bounded site/page checks and save Markdown plus raw JSON evidence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from check_page import audit_page
from check_site import audit_site


def _safe_cell(value: object) -> str:
    return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")


def _display_origin(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlsplit(url if "://" in url else f"https://{url}")
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"


def _rows(evidence: dict[str, object]) -> list[tuple[str, str, str]]:
    rows = []
    site = evidence.get("site", {})
    if isinstance(site, dict) and site.get("status") != "error":
        for name in ("robots", "sitemap"):
            check = site.get(name, {})
            if isinstance(check, dict):
                rows.append((name, str(check.get("status", "unassessed")), str(check.get("detail", ""))))
    page = evidence.get("page", {})
    if isinstance(page, dict) and page.get("status") != "error":
        checks = page.get("checks", {})
        if isinstance(checks, dict):
            for name, check in checks.items():
                if isinstance(check, dict):
                    rows.append((name, str(check.get("status", "unassessed")), str(check.get("detail", ""))))
    return rows


def render_markdown(evidence: dict[str, object], evidence_path: Path) -> str:
    rows = _rows(evidence)
    lines = [
        f"# Technical SEO Audit: {evidence['target_url']}",
        "",
        "## Scope and evidence limits",
        "",
        f"- Expected indexable: `{str(evidence['expected_indexable']).lower()}`",
        f"- Expected multilingual: `{str(evidence['expected_multilingual']).lower()}`",
        f"- Target query supplied: `{evidence.get('keyword') or 'none'}`",
        f"- Requested origin: `{evidence.get('requested_origin') or 'unavailable'}`",
        f"- Final production origin: `{evidence.get('final_origin') or 'unavailable'}`",
        f"- Site signals checked at: `{evidence.get('site_audit_origin') or 'unavailable'}`",
        f"- Requested/final origin changed: `{str(evidence.get('origin_changed')).lower() if evidence.get('origin_changed') is not None else 'unassessed'}`",
        f"- Raw evidence: `{evidence_path.name}`",
        "- Unassessed by these scripts: GSC/index coverage, server logs, rendered DOM, field Core Web Vitals, rankings, and demand.",
        "",
        "## Deterministic evidence",
        "",
        "| Check | Status | Observation |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| `{_safe_cell(name)}` | `{_safe_cell(status)}` | {_safe_cell(detail)} |" for name, status, detail in rows)
    lines.extend([
        "",
        "## Interpretation required",
        "",
        "Convert material observations into `OBSERVED`, `REVIEW`, or `UNASSESSED` findings. Confirm intent before assigning P0/P1, especially for noindex, robots rules, canonical consolidation, hreflang topology, and schema truthfulness.",
        "",
        "## Next checks",
        "",
        "Inspect the rendered DOM for JavaScript-dependent content, review multilingual alternates in the browser/Search Console, and re-run this command against the deployed URL after fixes.",
    ])
    return "\n".join(lines) + "\n"


def default_report_path(url: str) -> Path:
    parsed = urlsplit(url if "://" in url else f"https://{url}")
    slug = re.sub(r"[^a-z0-9]+", "-", f"{parsed.netloc}{parsed.path}".lower()).strip("-") or "site"
    return Path("reports") / f"{slug}-technical-seo-audit.md"


def collect_evidence(
    url: str,
    keyword: str | None,
    expected_indexable: bool,
    expected_multilingual: bool,
    validate_hreflang: bool,
    max_hreflang: int,
    max_sitemaps: int,
    timeout: int,
) -> dict[str, object]:
    """Fetch the page first, then check site signals at its final origin."""
    page = audit_page(
        url,
        keyword,
        expected_indexable,
        expected_multilingual,
        validate_hreflang,
        max_hreflang,
        timeout,
    )
    final_url = page.get("final_url") if isinstance(page.get("final_url"), str) else None
    site_target = final_url or url
    site = audit_site(site_target, timeout, max_sitemaps)
    requested_origin = _display_origin(url)
    final_origin = _display_origin(final_url)
    site_audit_origin = site.get("origin") if isinstance(site.get("origin"), str) else _display_origin(site_target)
    if isinstance(site_audit_origin, str):
        site_audit_origin = site_audit_origin.rstrip("/")
    origin_changed = requested_origin != final_origin if requested_origin and final_origin else None
    return {
        "target_url": url,
        "requested_origin": requested_origin,
        "final_url": final_url,
        "final_origin": final_origin,
        "site_audit_origin": site_audit_origin,
        "origin_changed": origin_changed,
        "expected_indexable": expected_indexable,
        "expected_multilingual": expected_multilingual,
        "keyword": keyword,
        "site": site,
        "page": page,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a unified evidence-led technical SEO audit.")
    parser.add_argument("url")
    parser.add_argument("--keyword", help="User-supplied target query; optional.")
    parser.add_argument("--expected-indexable", action="store_true")
    parser.add_argument("--single-language", action="store_true", help="Disable the default multilingual expectation.")
    parser.add_argument("--skip-hreflang-validation", action="store_true")
    parser.add_argument("--max-hreflang", type=int, default=12)
    parser.add_argument("--max-sitemaps", type=int, default=12)
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    expected_multilingual = not args.single_language
    evidence = collect_evidence(
        args.url,
        args.keyword,
        args.expected_indexable,
        expected_multilingual,
        not args.skip_hreflang_validation,
        args.max_hreflang,
        args.max_sitemaps,
        args.timeout,
    )
    report_path = args.output or default_report_path(args.url)
    evidence_path = report_path.with_suffix(".json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_path.write_text(render_markdown(evidence, evidence_path), encoding="utf-8")
    print(json.dumps({"report": str(report_path), "evidence": str(evidence_path)}, ensure_ascii=False))
    has_error = any(isinstance(evidence[key], dict) and evidence[key].get("status") == "error" for key in ("site", "page"))
    has_failure = any(status == "fail" for _, status, _ in _rows(evidence))
    return 1 if has_error or has_failure else 0


if __name__ == "__main__":
    sys.exit(main())
