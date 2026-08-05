#!/usr/bin/env python3
"""Inspect observable on-page technical SEO signals from bounded static HTML."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from url_safety import UnsafeUrlError, safe_fetch


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


class PageParser(HTMLParser):
    def __init__(self, final_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.final_url = final_url
        self.title_parts: list[str] = []
        self.in_title = False
        self.current_heading: str | None = None
        self.current_heading_parts: list[str] = []
        self.headings: dict[str, list[str]] = {f"h{level}": [] for level in range(1, 7)}
        self.meta_description: str | None = None
        self.robots: str | None = None
        self.canonical: str | None = None
        self.images: list[dict[str, bool]] = []
        self.internal_links = 0
        self.external_links = 0
        self.text_parts: list[str] = []
        self.script_count = 0
        self.ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value or "" for key, value in attrs}
        if tag in {"script", "style", "noscript", "template"}:
            self.ignored_depth += 1
            if tag == "script":
                self.script_count += 1
            return
        if self.ignored_depth:
            return
        if tag == "title":
            self.in_title = True
        elif tag in self.headings:
            self.current_heading = tag
            self.current_heading_parts = []
        elif tag == "meta":
            name = attributes.get("name", "").lower()
            if name == "description":
                self.meta_description = attributes.get("content", "")
            if name == "robots":
                self.robots = attributes.get("content", "")
        elif tag == "link" and "canonical" in attributes.get("rel", "").lower().split():
            self.canonical = attributes.get("href") or None
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
        if tag in {"script", "style", "noscript", "template"}:
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
        if self.ignored_depth:
            return
        if self.in_title:
            self.title_parts.append(data)
        if self.current_heading:
            self.current_heading_parts.append(data)
        self.text_parts.append(data)


def analyze_html(html: str, final_url: str, keyword: str | None, expected_indexable: bool) -> dict[str, object]:
    parser = PageParser(final_url)
    parser.feed(html)
    parser.close()
    title = _clean(" ".join(parser.title_parts)) or None
    text = _clean(" ".join(parser.text_parts))
    word_count = len(re.findall(r"\b\w+[\w'-]*\b", text))
    resolved_canonical = urljoin(final_url, parser.canonical) if parser.canonical else None
    final_without_fragment = final_url.split("#", 1)[0]
    missing_alt = sum(1 for image in parser.images if not image["has_alt"])
    empty_alt = sum(1 for image in parser.images if image["empty_alt"])
    robots_tokens = {token.strip().lower() for token in (parser.robots or "").split(",") if token.strip()}
    noindex = "noindex" in robots_tokens or "none" in robots_tokens

    checks: dict[str, object] = {
        "title": {
            "status": "warn" if not title else "pass",
            "value": title,
            "length": len(title) if title else 0,
            "detail": "No title element in static HTML." if not title else "Title found; assess clarity and intent in context, not by a fixed length rule.",
        },
        "meta_description": {
            "status": "info" if parser.meta_description is not None else "review",
            "value": parser.meta_description,
            "length": len(parser.meta_description or ""),
            "detail": "Meta description found; assess truthfulness and snippet usefulness in context." if parser.meta_description is not None else "No meta description in static HTML; review whether a controlled snippet is useful for this route.",
        },
        "headings": {
            "status": "warn" if not parser.headings["h1"] else "info",
            "h1": parser.headings["h1"],
            "counts": {tag: len(values) for tag, values in parser.headings.items()},
            "detail": "No H1 found in static HTML." if not parser.headings["h1"] else "Heading structure observed; assess hierarchy against the page task rather than a fixed count.",
        },
        "canonical": {
            "status": "info" if not resolved_canonical or resolved_canonical == final_without_fragment else "review",
            "value": resolved_canonical,
            "detail": "No canonical declared; this can be valid for a single canonical URL." if not resolved_canonical else "Canonical matches fetched final URL." if resolved_canonical == final_without_fragment else "Canonical differs from fetched final URL; confirm whether consolidation is intentional.",
        },
        "robots_meta": {
            "status": "fail" if noindex and expected_indexable else "review" if noindex else "info",
            "value": parser.robots,
            "detail": "noindex present on a route expected to be indexable." if noindex and expected_indexable else "noindex present; confirm the route is intentionally excluded." if noindex else "No noindex directive observed in static HTML.",
        },
        "images": {
            "status": "warn" if missing_alt else "info",
            "count": len(parser.images),
            "missing_alt_attribute": missing_alt,
            "empty_alt": empty_alt,
            "detail": "Some images lack an alt attribute; inspect whether they carry content." if missing_alt else "No missing alt attributes observed; empty alt can be correct for decoration.",
        },
        "links": {
            "status": "info",
            "internal": parser.internal_links,
            "external": parser.external_links,
            "detail": "Counts exclude JavaScript-rendered links and do not establish internal-link quality.",
        },
        "content": {
            "status": "info",
            "word_count": word_count,
            "detail": "Word count is an observation, not a content-quality or ranking score.",
        },
        "rendering": {
            "status": "unassessed" if parser.script_count and word_count < 40 else "info",
            "script_count": parser.script_count,
            "detail": "Static HTML has little text and scripts are present; inspect the rendered DOM separately." if parser.script_count and word_count < 40 else "This script evaluates static HTML only; browser-rendered state remains outside scope.",
        },
    }
    if keyword:
        haystack = " ".join([title or "", *parser.headings["h1"]]).lower()
        checks["target_query"] = {
            "status": "info" if keyword.lower() in haystack else "review",
            "value": keyword,
            "detail": "Query phrase appears in title or H1; still review search-intent alignment." if keyword.lower() in haystack else "Query phrase is not an exact title/H1 match; review semantic intent and natural variants, do not treat this as an automatic defect.",
        }
    else:
        checks["target_query"] = {
            "status": "unassessed",
            "value": None,
            "detail": "No user-supplied target query; search-intent alignment is unassessed.",
        }
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded static-HTML technical SEO checks.")
    parser.add_argument("url")
    parser.add_argument("--keyword", help="User-supplied target query; optional.")
    parser.add_argument("--expected-indexable", action="store_true")
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()
    try:
        result = safe_fetch(args.url, timeout=args.timeout)
    except UnsafeUrlError as exc:
        print(json.dumps({"url": args.url, "status": "error", "error": str(exc)}, indent=2))
        return 1
    if result.error:
        print(json.dumps({"url": result.url, "status": "error", "error": result.error, "redirect_chain": result.redirect_chain}, indent=2))
        return 1
    output = {
        "url": args.url,
        "final_url": result.url,
        "http_status": result.status_code,
        "response_bytes": result.byte_length,
        "redirect_chain": result.redirect_chain,
        "checks": analyze_html(result.body or "", result.url, args.keyword, args.expected_indexable),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
