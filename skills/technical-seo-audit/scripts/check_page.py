#!/usr/bin/env python3
"""Inspect observable on-page technical SEO signals from bounded static HTML."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin, urlsplit

from url_safety import UnsafeUrlError, safe_fetch


LANGUAGE_CODE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
ROBOTS_DIRECTIVE_NAMES = {
    "all",
    "follow",
    "index",
    "indexifembedded",
    "max-image-preview",
    "max-snippet",
    "max-video-preview",
    "noarchive",
    "nofollow",
    "noimageindex",
    "noindex",
    "none",
    "nosnippet",
    "notranslate",
    "unavailable_after",
}


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _without_fragment(url: str) -> str:
    parsed = urlsplit(url)
    return parsed._replace(fragment="").geturl()


def _directive_tokens(value: str | None) -> list[str]:
    if not value:
        return []
    return [token for segment in value.lower().split(",") for token in segment.strip().split() if token]


def parse_directives(
    meta_robots: str | None,
    meta_googlebot: str | None,
    x_robots_headers: str | None,
    target_agent: str = "googlebot",
) -> dict[str, object]:
    """Return directives effective for one crawler without merging other scopes."""
    target_agent = target_agent.lower()
    effective = _directive_tokens(meta_robots)
    ignored_scopes: dict[str, list[str]] = {}
    if target_agent == "googlebot":
        effective.extend(_directive_tokens(meta_googlebot))
    elif meta_googlebot:
        ignored_scopes["googlebot"] = _directive_tokens(meta_googlebot)

    for header_value in (x_robots_headers or "").splitlines():
        current_scope: str | None = None
        for raw_segment in header_value.split(","):
            segment = raw_segment.strip()
            if not segment:
                continue
            scoped = re.match(r"^([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.*)$", segment)
            if scoped and scoped.group(1).lower() not in ROBOTS_DIRECTIVE_NAMES:
                current_scope = scoped.group(1).lower()
                segment = scoped.group(2).strip()
            tokens = _directive_tokens(segment)
            if current_scope is None or current_scope == target_agent:
                effective.extend(tokens)
            elif tokens:
                ignored_scopes.setdefault(current_scope, []).extend(tokens)

    return {
        "target_agent": target_agent,
        "directives": sorted(set(effective)),
        "ignored_scoped_directives": {
            scope: sorted(set(tokens)) for scope, tokens in sorted(ignored_scopes.items())
        },
    }


class PageParser(HTMLParser):
    def __init__(self, final_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.final_url = final_url
        self.html_lang: str | None = None
        self.title_parts: list[str] = []
        self.in_title = False
        self.current_heading: str | None = None
        self.current_heading_parts: list[str] = []
        self.headings: dict[str, list[str]] = {f"h{level}": [] for level in range(1, 7)}
        self.meta_description: str | None = None
        self.robots: str | None = None
        self.googlebot: str | None = None
        self.canonical: str | None = None
        self.hreflang_entries: list[dict[str, str]] = []
        self.images: list[dict[str, bool]] = []
        self.internal_links = 0
        self.external_links = 0
        self.text_parts: list[str] = []
        self.script_count = 0
        self.ignored_depth = 0
        self.in_json_ld = False
        self.current_json_ld: list[str] = []
        self.json_ld_blocks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag == "script":
            self.script_count += 1
            if attributes.get("type", "").split(";", 1)[0].strip().lower() == "application/ld+json":
                self.in_json_ld = True
                self.current_json_ld = []
            else:
                self.ignored_depth += 1
            return
        if tag in {"style", "noscript", "template"}:
            self.ignored_depth += 1
            return
        if self.ignored_depth:
            return
        if tag == "html":
            self.html_lang = attributes.get("lang") or None
        elif tag == "title":
            self.in_title = True
        elif tag in self.headings:
            self.current_heading = tag
            self.current_heading_parts = []
        elif tag == "meta":
            name = attributes.get("name", "").lower()
            if name == "description":
                self.meta_description = attributes.get("content", "")
            elif name == "robots":
                self.robots = attributes.get("content", "")
            elif name == "googlebot":
                self.googlebot = attributes.get("content", "")
        elif tag == "link":
            rel_tokens = attributes.get("rel", "").lower().split()
            if "canonical" in rel_tokens:
                self.canonical = attributes.get("href") or None
            if "alternate" in rel_tokens and attributes.get("hreflang") and attributes.get("href"):
                self.hreflang_entries.append({
                    "hreflang": attributes["hreflang"],
                    "href": urljoin(self.final_url, attributes["href"]),
                })
        elif tag == "img":
            self.images.append({"has_alt": "alt" in attributes, "empty_alt": attributes.get("alt", "") == ""})
        elif tag == "a" and attributes.get("href"):
            parsed = urlsplit(urljoin(self.final_url, attributes["href"]))
            if parsed.scheme in {"http", "https"}:
                if parsed.netloc == urlsplit(self.final_url).netloc:
                    self.internal_links += 1
                else:
                    self.external_links += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "script":
            if self.in_json_ld:
                self.json_ld_blocks.append("".join(self.current_json_ld).strip())
                self.in_json_ld = False
                self.current_json_ld = []
            else:
                self.ignored_depth = max(0, self.ignored_depth - 1)
            return
        if tag in {"style", "noscript", "template"}:
            self.ignored_depth = max(0, self.ignored_depth - 1)
            return
        if self.ignored_depth:
            return
        if tag == "title":
            self.in_title = False
        if tag == self.current_heading:
            value = _clean(" ".join(self.current_heading_parts))
            if value:
                self.headings[tag].append(value)
            self.current_heading = None
            self.current_heading_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_json_ld:
            self.current_json_ld.append(data)
            return
        if self.ignored_depth:
            return
        if self.in_title:
            self.title_parts.append(data)
        if self.current_heading:
            self.current_heading_parts.append(data)
        self.text_parts.append(data)


def analyze_delivery(http_status: int | None, headers: dict[str, str], expected_indexable: bool) -> dict[str, object]:
    content_type = next((value for key, value in headers.items() if key.lower() == "content-type"), "")
    if http_status == 200:
        status = "pass"
        detail = "Final response returned HTTP 200."
    elif http_status in {404, 410}:
        status = "fail" if expected_indexable else "review"
        detail = f"Final response returned HTTP {http_status}; confirm whether this target should exist and be indexable."
    elif http_status in {401, 403}:
        status = "unassessed"
        detail = f"Final response returned HTTP {http_status}; page signals cannot be fully assessed."
    elif http_status is not None and http_status >= 500:
        status = "fail"
        detail = f"Final response returned server error HTTP {http_status}."
    elif http_status is None:
        status = "unassessed"
        detail = "No final HTTP response was available."
    else:
        status = "review"
        detail = f"Final response returned HTTP {http_status}; review delivery behavior."
    if content_type and "html" not in content_type.lower() and "xhtml" not in content_type.lower():
        status = "review" if status == "pass" else status
        detail += f" Content-Type is {content_type!r}, not HTML."
    return {"status": status, "http_status": http_status, "content_type": content_type or None, "detail": detail}


def _json_ld_check(blocks: list[str]) -> dict[str, object]:
    errors: list[dict[str, object]] = []
    top_level_types: set[str] = set()
    all_nested_types: set[str] = set()
    contexts: set[str] = set()
    parsed_blocks = 0

    def add_types(value: Any, destination: set[str]) -> None:
        if isinstance(value, str):
            destination.add(value)
        elif isinstance(value, list):
            destination.update(str(item) for item in value)

    def visit_declared_nodes(value: Any) -> None:
        if isinstance(value, list):
            for item in value:
                visit_declared_nodes(item)
        elif isinstance(value, dict):
            context = value.get("@context")
            if isinstance(context, str):
                contexts.add(context)
            add_types(value.get("@type"), top_level_types)
            if "@graph" in value:
                visit_declared_nodes(value["@graph"])

    def visit_all_nodes(value: Any) -> None:
        if isinstance(value, list):
            for item in value:
                visit_all_nodes(item)
        elif isinstance(value, dict):
            add_types(value.get("@type"), all_nested_types)
            for child in value.values():
                visit_all_nodes(child)

    for index, raw in enumerate(blocks):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append({"block": index + 1, "line": exc.lineno, "column": exc.colno, "message": exc.msg})
            continue
        parsed_blocks += 1
        visit_declared_nodes(value)
        visit_all_nodes(value)
    return {
        "status": "warn" if errors else "info",
        "blocks_found": len(blocks),
        "parseable_blocks": parsed_blocks,
        "parse_errors": errors,
        "types": sorted(top_level_types),
        "top_level_types": sorted(top_level_types),
        "all_nested_types": sorted(all_nested_types),
        "contexts": sorted(contexts),
        "semantic_review_required": bool(all_nested_types),
        "detail": "JSON-LD syntax errors observed." if errors else "JSON-LD parsed; verify that types and claims match visible page content." if blocks else "No JSON-LD block observed; absence is not automatically a defect.",
    }


def _hreflang_check(parser: PageParser, self_reference_url: str, expected_multilingual: bool) -> dict[str, object]:
    entries = parser.hreflang_entries
    codes = [entry["hreflang"] for entry in entries]
    comparable_codes = [code.lower() for code in codes]
    invalid = sorted({code for code in codes if code.lower() != "x-default" and not LANGUAGE_CODE.fullmatch(code)})
    duplicates = sorted({code for code in comparable_codes if comparable_codes.count(code) > 1})
    self_entries = [entry for entry in entries if _without_fragment(entry["href"]) == _without_fragment(self_reference_url)]
    self_reference = bool(self_entries)
    self_codes = sorted({entry["hreflang"] for entry in self_entries if entry["hreflang"].lower() != "x-default"})
    lang_matches_self = None
    if parser.html_lang and self_codes:
        html_primary = parser.html_lang.lower().split("-", 1)[0]
        lang_matches_self = any(code.lower().split("-", 1)[0] == html_primary for code in self_codes)
    has_x_default = "x-default" in comparable_codes
    issues = []
    review_issues = []
    if expected_multilingual and not parser.html_lang:
        issues.append("Missing html lang on a page expected to be multilingual.")
    if expected_multilingual and not entries:
        issues.append("No hreflang alternates on a page expected to be multilingual.")
    if entries and not self_reference:
        issues.append("Hreflang set has no self-reference for the canonical URL or fetched final URL used as its fallback.")
    if invalid:
        issues.append("Invalid or unsupported hreflang code syntax observed.")
    if duplicates:
        issues.append("Duplicate hreflang codes observed.")
    if lang_matches_self is False:
        review_issues.append("html lang and the self-referencing hreflang use different primary languages; review the declarations.")
    detail = " ".join([*issues, *review_issues])
    if not detail:
        detail = "Language declarations observed; x-default is optional and language-tag casing is not significant." if parser.html_lang or entries else "No language declarations observed; multilingual delivery was not expected for this run."
    return {
        "status": "warn" if issues else "review" if review_issues else "info",
        "html_lang": parser.html_lang,
        "entries": entries,
        "self_reference_target": self_reference_url,
        "has_self_reference": self_reference,
        "self_reference_codes": self_codes,
        "html_lang_matches_self_reference": lang_matches_self,
        "has_x_default": has_x_default,
        "invalid_codes": invalid,
        "duplicate_codes": duplicates,
        "validation": None,
        "detail": detail,
    }


def analyze_html(
    html: str,
    final_url: str,
    keyword: str | None,
    expected_indexable: bool,
    response_headers: dict[str, str] | None = None,
    http_status: int | None = 200,
    expected_multilingual: bool = False,
) -> dict[str, object]:
    parser = PageParser(final_url)
    parser.feed(html)
    parser.close()
    headers = response_headers or {}
    title = _clean(" ".join(parser.title_parts)) or None
    text = _clean(" ".join(parser.text_parts))
    word_count = len(re.findall(r"\b\w+[\w'-]*\b", text))
    resolved_canonical = urljoin(final_url, parser.canonical) if parser.canonical else None
    missing_alt = sum(1 for image in parser.images if not image["has_alt"])
    empty_alt = sum(1 for image in parser.images if image["empty_alt"])
    x_robots = next((value for key, value in headers.items() if key.lower() == "x-robots-tag"), None)
    parsed_directives = parse_directives(parser.robots, parser.googlebot, x_robots, target_agent="googlebot")
    directives = parsed_directives["directives"]
    noindex = "noindex" in directives or "none" in directives
    checks: dict[str, object] = {
        "delivery": analyze_delivery(http_status, headers, expected_indexable),
        "title": {"status": "warn" if not title else "pass", "value": title, "length": len(title) if title else 0, "detail": "No title element in static HTML." if not title else "Title found; assess clarity and intent in context, not by a fixed length rule."},
        "meta_description": {"status": "info" if parser.meta_description is not None else "review", "value": parser.meta_description, "length": len(parser.meta_description or ""), "detail": "Meta description found; assess truthfulness and snippet usefulness in context." if parser.meta_description is not None else "No meta description in static HTML; review whether a controlled snippet is useful for this route."},
        "headings": {"status": "warn" if not parser.headings["h1"] else "info", "h1": parser.headings["h1"], "counts": {tag: len(values) for tag, values in parser.headings.items()}, "detail": "No H1 found in static HTML." if not parser.headings["h1"] else "Heading structure observed; assess hierarchy against the page task rather than a fixed count."},
        "canonical": {"status": "info" if not resolved_canonical or _without_fragment(resolved_canonical) == _without_fragment(final_url) else "review", "value": resolved_canonical, "detail": "No canonical declared; this can be valid for a single canonical URL." if not resolved_canonical else "Canonical matches fetched final URL." if _without_fragment(resolved_canonical) == _without_fragment(final_url) else "Canonical differs from fetched final URL; confirm whether consolidation is intentional."},
        "indexability_directives": {"status": "fail" if noindex and expected_indexable else "review" if noindex else "info", "target_agent": parsed_directives["target_agent"], "meta_robots": parser.robots, "meta_googlebot": parser.googlebot, "x_robots_tag": x_robots, "directives": directives, "ignored_scoped_directives": parsed_directives["ignored_scoped_directives"], "detail": "noindex observed on a route expected to be indexable." if noindex and expected_indexable else "noindex observed; confirm the route is intentionally excluded." if noindex else "No noindex directive observed for the target crawler in static HTML or response headers."},
        "images": {"status": "warn" if missing_alt else "info", "count": len(parser.images), "missing_alt_attribute": missing_alt, "empty_alt": empty_alt, "detail": "Some images lack an alt attribute; inspect whether they carry content." if missing_alt else "No missing alt attributes observed; empty alt can be correct for decoration."},
        "static_link_inventory": {"status": "info", "internal": parser.internal_links, "external": parser.external_links, "detail": "Static link counts do not test broken links, depth, orphaning, anchor quality, or rendered links."},
        "content": {"status": "info", "word_count": word_count, "detail": "Word count is an observation, not a content-quality or ranking score."},
        "rendering": {"status": "unassessed" if parser.script_count and word_count < 40 else "info", "script_count": parser.script_count, "detail": "Static HTML has little text and scripts are present; inspect the rendered DOM separately." if parser.script_count and word_count < 40 else "This script evaluates static HTML only; browser-rendered state remains outside scope."},
        "json_ld": _json_ld_check(parser.json_ld_blocks),
        "hreflang": _hreflang_check(parser, resolved_canonical or final_url, expected_multilingual),
    }
    if keyword:
        haystack = " ".join([title or "", *parser.headings["h1"]]).lower()
        checks["target_query"] = {"status": "info" if keyword.lower() in haystack else "review", "value": keyword, "detail": "Query phrase appears in title or H1; still review search-intent alignment." if keyword.lower() in haystack else "Query phrase is not an exact title/H1 match; review semantic intent and natural variants, do not treat this as an automatic defect."}
    else:
        checks["target_query"] = {"status": "unassessed", "value": None, "detail": "No user-supplied target query; search-intent alignment is unassessed."}
    return checks


def validate_hreflang_targets(entries: list[dict[str, str]], source_url: str, timeout: int, max_entries: int) -> dict[str, object]:
    results = []
    unique_entries = list({(entry["hreflang"].lower(), entry["href"]): entry for entry in entries}.values())
    for entry in unique_entries[:max_entries]:
        try:
            result = safe_fetch(entry["href"], timeout=timeout)
        except UnsafeUrlError as exc:
            results.append({"hreflang": entry["hreflang"], "url": entry["href"], "final_url": None, "http_status": None, "error": str(exc), "reciprocal": None})
            continue
        reciprocal = None
        if not result.error and result.status_code == 200 and result.body is not None:
            target_parser = PageParser(result.url)
            target_parser.feed(result.body)
            target_parser.close()
            reciprocal = any(_without_fragment(item["href"]) == _without_fragment(source_url) for item in target_parser.hreflang_entries)
        results.append({"hreflang": entry["hreflang"], "url": entry["href"], "final_url": result.url, "http_status": result.status_code, "error": result.error, "reciprocal": reciprocal})
    failed = [item for item in results if item["error"] or item["http_status"] != 200 or item["reciprocal"] is False]
    return {"checked": len(results), "not_checked": max(0, len(unique_entries) - len(results)), "results": results, "status": "warn" if failed else "info", "detail": "Some hreflang targets were unreachable or lacked a reciprocal reference." if failed else "Checked hreflang targets were reachable and reciprocal within the configured bound."}


def audit_page(url: str, keyword: str | None = None, expected_indexable: bool = False, expected_multilingual: bool = False, validate_hreflang: bool = False, max_hreflang: int = 12, timeout: int = 15) -> dict[str, object]:
    try:
        result = safe_fetch(url, timeout=timeout)
    except UnsafeUrlError as exc:
        return {"url": url, "status": "error", "error": str(exc)}
    if result.error:
        return {"url": result.url, "status": "error", "error": result.error, "redirect_chain": result.redirect_chain}
    checks = analyze_html(result.body or "", result.url, keyword, expected_indexable, result.headers, result.status_code, expected_multilingual)
    hreflang = checks["hreflang"]
    if validate_hreflang and isinstance(hreflang, dict) and hreflang["entries"]:
        reciprocal_source = hreflang.get("self_reference_target") or result.url
        hreflang["validation"] = validate_hreflang_targets(hreflang["entries"], reciprocal_source, timeout, max_hreflang)
        if hreflang["validation"]["status"] == "warn":
            hreflang["status"] = "warn"
            hreflang["detail"] = f"{hreflang['detail']} {hreflang['validation']['detail']}"
    return {"url": url, "final_url": result.url, "http_status": result.status_code, "response_bytes": result.byte_length, "redirect_chain": result.redirect_chain, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded static-HTML technical SEO checks.")
    parser.add_argument("url")
    parser.add_argument("--keyword", help="User-supplied target query; optional.")
    parser.add_argument("--expected-indexable", action="store_true")
    parser.add_argument("--expected-multilingual", action="store_true")
    parser.add_argument("--validate-hreflang", action="store_true")
    parser.add_argument("--max-hreflang", type=int, default=12)
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()
    output = audit_page(args.url, args.keyword, args.expected_indexable, args.expected_multilingual, args.validate_hreflang, args.max_hreflang, args.timeout)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    if output.get("status") == "error":
        return 1
    checks = output.get("checks", {})
    return 1 if any(isinstance(value, dict) and value.get("status") == "fail" for value in checks.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
