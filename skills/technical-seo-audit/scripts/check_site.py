#!/usr/bin/env python3
"""Inspect robots.txt and bounded sitemap delivery for a public target URL."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as element_tree
from collections import deque
from urllib.parse import urljoin, urlsplit, urlunsplit

from url_safety import UnsafeUrlError, safe_fetch, validate_public_url


def origin_for(url: str) -> str:
    parsed = urlsplit(validate_public_url(url))
    return urlunsplit((parsed.scheme, parsed.netloc, "/", "", ""))


def parse_robots(content: str) -> tuple[list[dict[str, object]], list[str]]:
    """Parse robots groups, preserving consecutive User-agent lines."""
    groups: list[dict[str, object]] = []
    sitemaps: list[str] = []
    current: dict[str, object] | None = None
    previous_key = ""
    for raw_line in content.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = (piece.strip() for piece in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if current is None or previous_key != "user-agent":
                current = {"agents": [], "rules": []}
                groups.append(current)
            current["agents"].append(value.lower())
        elif key in {"allow", "disallow"} and current is not None:
            current["rules"].append({"directive": key, "pattern": value})
        elif key == "sitemap" and value:
            sitemaps.append(value)
        previous_key = key
    return groups, sitemaps


def _selected_rules(groups: list[dict[str, object]], user_agent: str) -> tuple[list[dict[str, str]], list[str]]:
    matches: list[tuple[int, dict[str, object], str]] = []
    user_agent = user_agent.lower()
    for group in groups:
        for token in group["agents"]:
            specificity = 0 if token == "*" else len(token) if token and token in user_agent else -1
            if specificity >= 0:
                matches.append((specificity, group, token))
    if not matches:
        return [], []
    best = max(item[0] for item in matches)
    selected_groups = []
    selected_tokens = []
    for specificity, group, token in matches:
        if specificity == best and id(group) not in {id(item) for item in selected_groups}:
            selected_groups.append(group)
            selected_tokens.append(token)
    rules = [rule for group in selected_groups for rule in group["rules"]]
    return rules, selected_tokens


def _rule_matches(pattern: str, path: str) -> bool:
    if not pattern:
        return False
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    expression = "^" + re.escape(body).replace(r"\*", ".*") + ("$" if anchored else "")
    return re.search(expression, path) is not None


def evaluate_robots(groups: list[dict[str, object]], user_agent: str, path: str) -> dict[str, object]:
    """Apply longest-match rules for one crawler and target path."""
    rules, selected_tokens = _selected_rules(groups, user_agent)
    matches = [rule for rule in rules if _rule_matches(rule["pattern"], path)]
    matched = None
    if matches:
        matched = max(matches, key=lambda rule: (len(rule["pattern"].replace("*", "").rstrip("$")), rule["directive"] == "allow"))
    allowed = matched is None or matched["directive"] == "allow"
    broad_disallow = any(rule["directive"] == "disallow" and rule["pattern"] in {"/", "/*", "/*$"} for rule in rules)
    exceptions = [rule for rule in rules if rule["directive"] == "allow" and rule["pattern"]]
    return {
        "selected_agents": selected_tokens,
        "rules": rules,
        "allowed": allowed,
        "matched_rule": matched,
        "site_wide_block": broad_disallow and not exceptions,
    }


def robots_result(target_url: str, timeout: int) -> tuple[dict[str, object], list[str]]:
    origin = origin_for(target_url)
    result = safe_fetch(urljoin(origin, "robots.txt"), timeout=timeout)
    if result.error:
        return {"status": "unassessed", "detail": result.error, "url": result.url}, []
    if result.status_code == 404:
        return {"status": "info", "detail": "No robots.txt at the standard path; this alone does not block crawling.", "url": result.url}, []
    if result.status_code != 200:
        return {"status": "review", "detail": f"robots.txt returned HTTP {result.status_code}.", "url": result.url}, []
    groups, sitemap_urls = parse_robots(result.body or "")
    parsed_target = urlsplit(target_url)
    target_path = parsed_target.path or "/"
    if parsed_target.query:
        target_path += f"?{parsed_target.query}"
    googlebot = evaluate_robots(groups, "googlebot", target_path)
    wildcard = evaluate_robots(groups, "*", target_path)
    target_blocked = not googlebot["allowed"]
    site_wide_block = bool(googlebot["site_wide_block"])
    return {
        "status": "fail" if target_blocked or site_wide_block else "pass",
        "detail": "Target URL or the entire site is blocked for Googlebot; confirm this is intentional." if target_blocked or site_wide_block else "No blocking Googlebot rule matched the target URL.",
        "url": result.url,
        "target_path": target_path,
        "target_url_blocked": target_blocked,
        "site_wide_block": site_wide_block,
        "googlebot": googlebot,
        "wildcard": wildcard,
        "sitemap_directives": sitemap_urls,
    }, sitemap_urls


def _local_name(element: element_tree.Element) -> str:
    return element.tag.rsplit("}", 1)[-1].lower()


def _loc_values(root: element_tree.Element, sitemap_type: str) -> list[str]:
    """Read only url > loc or sitemap > loc, excluding image/video loc nodes."""
    entry_name = "url" if sitemap_type == "urlset" else "sitemap"
    values = []
    for entry in root:
        if _local_name(entry) != entry_name:
            continue
        for element in entry:
            if _local_name(element) == "loc" and element.text and element.text.strip():
                values.append(element.text.strip())
    return values


def parse_sitemap_document(content: str, source_url: str, target_url: str) -> dict[str, object]:
    try:
        root = element_tree.fromstring(content)
    except element_tree.ParseError as exc:
        return {"status": "warn", "type": None, "detail": f"Sitemap is not parseable XML: {exc}.", "locations": []}
    sitemap_type = _local_name(root)
    if sitemap_type not in {"urlset", "sitemapindex"}:
        return {"status": "warn", "type": sitemap_type, "detail": f"Unexpected sitemap root element: {sitemap_type}.", "locations": []}
    locations = _loc_values(root, sitemap_type)
    unique = list(dict.fromkeys(locations))
    invalid = [value for value in unique if urlsplit(value).scheme not in {"http", "https"} or not urlsplit(value).netloc]
    source_origin = (urlsplit(source_url).scheme, urlsplit(source_url).netloc)
    foreign_origins = sorted({urlsplit(value).netloc for value in unique if urlsplit(value).netloc and (urlsplit(value).scheme, urlsplit(value).netloc) != source_origin})
    target_included = _normalized_sitemap_url(target_url) in {_normalized_sitemap_url(value) for value in unique}
    return {
        "status": "review" if not locations else "warn" if invalid else "pass",
        "type": sitemap_type,
        "entry_count": len(locations),
        "unique_entry_count": len(unique),
        "duplicate_count": len(locations) - len(unique),
        "invalid_locations": invalid,
        "foreign_origins": foreign_origins,
        "target_url_included": target_included,
        "locations": unique,
        "detail": "Sitemap XML is valid but contains no usable url/sitemap entries." if not locations else "Sitemap contains invalid loc values." if invalid else "Sitemap parsed; inclusion and counts are observations, not index coverage guarantees.",
    }


def _normalized_sitemap_url(value: str) -> str:
    parsed = urlsplit(value)
    return parsed._replace(fragment="").geturl().rstrip("/")


def sitemap_result(origin: str, target_url: str, sitemap_urls: list[str], timeout: int, max_sitemaps: int) -> dict[str, object]:
    declared = bool(sitemap_urls)
    initial = [urljoin(origin, value) for value in sitemap_urls] if sitemap_urls else [urljoin(origin, "sitemap.xml")]
    unique_initial = list(dict.fromkeys(initial))
    document_limit = max(0, max_sitemaps)
    queue = deque(unique_initial[:document_limit])
    queued = set(unique_initial)
    bounded_out = max(0, len(unique_initial) - document_limit)
    documents = []
    while queue and len(documents) < document_limit:
        candidate = queue.popleft()
        try:
            result = safe_fetch(candidate, timeout=timeout)
        except UnsafeUrlError as exc:
            documents.append({"url": candidate, "status": "warn", "detail": str(exc)})
            continue
        if result.error or result.status_code != 200:
            documents.append({"url": candidate, "status": "warn" if declared else "info", "http_status": result.status_code, "detail": result.error or f"Sitemap returned HTTP {result.status_code}."})
            continue
        parsed = parse_sitemap_document(result.body or "", result.url, target_url)
        parsed["url"] = result.url
        documents.append(parsed)
        if parsed.get("type") == "sitemapindex":
            for child in parsed.get("locations", []):
                parsed_child = urlsplit(child)
                if parsed_child.scheme not in {"http", "https"} or not parsed_child.netloc:
                    continue
                if child in queued:
                    continue
                queued.add(child)
                if len(documents) + len(queue) < document_limit:
                    queue.append(child)
                else:
                    bounded_out += 1
    valid = [document for document in documents if document.get("status") == "pass"]
    warnings = [document for document in documents if document.get("status") == "warn"]
    reviews = [document for document in documents if document.get("status") == "review"]
    target_included = any(document.get("type") == "urlset" and document.get("target_url_included") for document in documents)
    if warnings:
        status = "warn"
    elif reviews:
        status = "review"
    elif valid:
        status = "pass"
    else:
        status = "warn" if declared else "info"
    queued_remaining = len(queue)
    return {
        "status": status,
        "declared": declared,
        "documents_checked": len(documents),
        "documents_queued_remaining": queued_remaining,
        "documents_bounded_out": bounded_out,
        "documents_not_checked": queued_remaining + bounded_out,
        "target_url_included": target_included,
        "documents": documents,
        "detail": "Some sitemap documents were valid XML but had no usable entries; review whether they are intentionally empty." if reviews and not warnings else "Sitemap documents checked within the configured bound; target absence is review-only." if valid else "No valid sitemap document was retrieved within the configured locations/bound.",
    }


def audit_site(url: str, timeout: int = 15, max_sitemaps: int = 12) -> dict[str, object]:
    try:
        target_url = validate_public_url(url)
        origin = origin_for(target_url)
        robots, sitemap_urls = robots_result(target_url, timeout)
        return {"target_url": target_url, "origin": origin, "robots": robots, "sitemap": sitemap_result(origin, target_url, sitemap_urls, timeout, max_sitemaps)}
    except UnsafeUrlError as exc:
        return {"url": url, "status": "error", "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded robots.txt and sitemap checks.")
    parser.add_argument("url")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--max-sitemaps", type=int, default=12)
    args = parser.parse_args()
    output = audit_site(args.url, args.timeout, args.max_sitemaps)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    if output.get("status") == "error":
        return 1
    return 1 if output["robots"]["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
