"""Bounded public-web retrieval helpers for technical SEO checks.

This module reduces accidental SSRF risk. It is not a substitute for running
untrusted URL fetches in a network-restricted environment.
"""

from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


MAX_REDIRECTS = 5
MAX_RESPONSE_BYTES = 2_000_000
ALLOWED_PORTS = {80, 443}
DEFAULT_HEADERS = {
    "User-Agent": "CodexTechnicalSeoAudit/1.0 (+https://github.com/ai-ashao/codex-skillforge)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class UnsafeUrlError(ValueError):
    """Raised when a URL is outside the public-web retrieval boundary."""


@dataclass(frozen=True)
class FetchResult:
    url: str
    status_code: int | None
    headers: dict[str, str]
    body: str | None
    byte_length: int
    redirect_chain: list[dict[str, object]]
    error: str | None


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


Resolver = Callable[..., list[tuple[object, object, object, object, tuple[object, ...]]]]


def _resolve_public(hostname: str, port: int, resolver: Resolver = socket.getaddrinfo) -> None:
    try:
        records = resolver(hostname, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise UnsafeUrlError(f"Could not resolve host {hostname!r}: {exc}") from exc
    addresses = {record[4][0] for record in records if record[4]}
    if not addresses:
        raise UnsafeUrlError(f"Could not resolve host {hostname!r} to an IP address")
    unsafe = []
    for address in addresses:
        try:
            ip = ipaddress.ip_address(str(address))
        except ValueError as exc:
            raise UnsafeUrlError(f"Host {hostname!r} resolved to an invalid IP address") from exc
        if not ip.is_global:
            unsafe.append(str(ip))
    if unsafe:
        raise UnsafeUrlError(f"Blocked non-public address for {hostname!r}: {', '.join(sorted(unsafe))}")


def validate_public_url(url: str, resolver: Resolver = socket.getaddrinfo) -> str:
    """Normalize and validate a public HTTP(S) URL before every request hop."""
    candidate = url.strip()
    parsed = urlsplit(candidate)
    if not parsed.scheme:
        candidate = f"https://{candidate}"
        parsed = urlsplit(candidate)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeUrlError(f"Only HTTP(S) URLs are allowed, got {parsed.scheme!r}")
    if not parsed.hostname or parsed.username or parsed.password:
        raise UnsafeUrlError("URL must contain a hostname and no user credentials")
    try:
        port = parsed.port
    except ValueError as exc:
        raise UnsafeUrlError("URL has an invalid port") from exc
    effective_port = port or (443 if parsed.scheme == "https" else 80)
    if effective_port not in ALLOWED_PORTS:
        raise UnsafeUrlError(f"Only ports 80 and 443 are allowed, got {effective_port}")
    _resolve_public(parsed.hostname, effective_port, resolver)
    path = parsed.path or "/"
    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, ""))


def _decode_body(raw: bytes, content_type: str) -> str:
    charset = "utf-8"
    for part in content_type.split(";")[1:]:
        key, _, value = part.partition("=")
        if key.strip().lower() == "charset" and value.strip():
            charset = value.strip().strip('"')
            break
    try:
        return raw.decode(charset, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


def safe_fetch(url: str, timeout: int = 15, max_bytes: int = MAX_RESPONSE_BYTES) -> FetchResult:
    """Fetch a public URL with redirect-by-redirect validation and body bounds."""
    current_url = validate_public_url(url)
    redirects: list[dict[str, object]] = []
    opener = build_opener(_NoRedirect())

    for _ in range(MAX_REDIRECTS + 1):
        request = Request(current_url, headers=DEFAULT_HEADERS)
        response = None
        try:
            response = opener.open(request, timeout=timeout)
        except HTTPError as exc:
            response = exc
        except (URLError, TimeoutError, OSError) as exc:
            return FetchResult(current_url, None, {}, None, 0, redirects, str(exc))

        headers = dict(response.headers.items())
        if hasattr(response.headers, "get_all"):
            x_robots_values = response.headers.get_all("X-Robots-Tag")
            if x_robots_values:
                headers["X-Robots-Tag"] = ", ".join(x_robots_values)
        status_code = response.code
        location = headers.get("Location")
        if 300 <= status_code < 400 and location:
            redirects.append({"url": current_url, "status_code": status_code})
            if len(redirects) > MAX_REDIRECTS:
                return FetchResult(current_url, status_code, headers, None, 0, redirects, "Too many redirects")
            try:
                current_url = validate_public_url(urljoin(current_url, location))
            except UnsafeUrlError as exc:
                return FetchResult(current_url, status_code, headers, None, 0, redirects, str(exc))
            continue

        try:
            raw = response.read(max_bytes + 1)
        except OSError as exc:
            return FetchResult(current_url, status_code, headers, None, 0, redirects, str(exc))
        if len(raw) > max_bytes:
            return FetchResult(current_url, status_code, headers, None, len(raw), redirects, f"Response exceeds {max_bytes} byte limit")
        return FetchResult(
            current_url,
            status_code,
            headers,
            _decode_body(raw, headers.get("Content-Type", "")),
            len(raw),
            redirects,
            None,
        )

    return FetchResult(current_url, None, {}, None, 0, redirects, "Unexpected redirect handling error")
