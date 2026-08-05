#!/usr/bin/env python3
"""Inspect public robots.txt and sitemap delivery without crawling the site."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as element_tree
from urllib.parse import urljoin, urlsplit, urlunsplit

from url_safety import UnsafeUrlError, safe_fetch, validate_public_url


def origin_for(url: str) -> str:
    parsed = urlsplit(validate_public_url(url))
    return urlunsplit((parsed.scheme, parsed.netloc, "/", "", ""))


def robots_result(origin: str, timeout: int) -> tuple[dict[str, object], list[str]]:
    result = safe_fetch(urljoin(origin, "robots.txt"), timeout=timeout)
    if result.error:
        return {"status": "unassessed", "detail": result.error, "url": result.url}, []
    if result.status_code == 404:
        return {"status": "info", "detail": "No robots.txt at the standard path; this alone does not block indexing.", "url": result.url}, []
    if result.status_code != 200:
        return {"status": "review", "detail": f"robots.txt returned HTTP {result.status_code}.", "url": result.url}, []
    body = result.body or ""
    sitemap_urls = [line.split(":", 1)[1].strip() for line in body.splitlines() if line.lower().startswith("sitemap:") and ":" in line]
    current_agents: list[str] = []
    blocks_all = False
    for raw_line in body.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = (piece.strip() for piece in line.split(":", 1))
        if key.lower() == "user-agent":
            current_agents = [value.lower()]
        elif key.lower() == "disallow" and value in {"/", "/*"} and any(agent in {"*", "googlebot"} for agent in current_agents):
            blocks_all = True
    return {
        "status": "fail" if blocks_all else "pass",
        "detail": "robots.txt contains a root Disallow for Googlebot or all crawlers; confirm this is intentional." if blocks_all else "robots.txt retrieved; no root block for Googlebot/all crawlers observed.",
        "url": result.url,
        "sitemap_directives": sitemap_urls,
    }, sitemap_urls


def sitemap_result(origin: str, sitemap_urls: list[str], timeout: int) -> dict[str, object]:
    candidates = [urljoin(origin, value) for value in sitemap_urls[:3]] or [urljoin(origin, "sitemap.xml")]
    for candidate in candidates:
        result = safe_fetch(candidate, timeout=timeout)
        if result.error or result.status_code == 404:
            continue
        if result.status_code != 200:
            return {"status": "review", "url": result.url, "detail": f"Sitemap returned HTTP {result.status_code}."}
        try:
            root = element_tree.fromstring(result.body or "")
        except element_tree.ParseError as exc:
            return {"status": "warn", "url": result.url, "detail": f"Sitemap is not parseable XML: {exc}."}
        tag = root.tag.rsplit("}", 1)[-1].lower()
        child_tag = "sitemap" if tag == "sitemapindex" else "url"
        count = sum(1 for child in root if child.tag.rsplit("}", 1)[-1].lower() == child_tag)
        return {"status": "pass", "url": result.url, "type": tag, "entry_count": count, "detail": "Sitemap XML retrieved; count is an observation, not a coverage guarantee."}
    return {"status": "info", "url": candidates, "detail": "No accessible sitemap found at discovered/default locations; confirm whether one is needed for this site."}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded robots.txt and sitemap checks.")
    parser.add_argument("url")
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()
    try:
        origin = origin_for(args.url)
        robots, sitemap_urls = robots_result(origin, args.timeout)
        output = {"origin": origin, "robots": robots, "sitemap": sitemap_result(origin, sitemap_urls, args.timeout)}
    except UnsafeUrlError as exc:
        output = {"url": args.url, "status": "error", "error": str(exc)}
        print(json.dumps(output, indent=2))
        return 1
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 1 if output["robots"]["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
