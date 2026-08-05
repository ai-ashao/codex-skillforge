import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from url_safety import UnsafeUrlError, safe_fetch, validate_public_url  # noqa: E402


def resolver_for(*addresses):
    def resolve(hostname, port, type):
        family = socket.AF_INET6 if any(":" in address for address in addresses) else socket.AF_INET
        return [(family, socket.SOCK_STREAM, 6, "", (address, port)) for address in addresses]

    return resolve


class FakeResponse:
    def __init__(self, code=200, headers=None, body=b""):
        self.code = code
        self.headers = headers or {}
        self.body = body

    def read(self, size):
        return self.body[:size]


class MultiValueHeaders:
    def __init__(self, values):
        self.values = values

    def items(self):
        return [("Content-Type", "text/html"), ("X-Robots-Tag", self.values[0])]

    def get_all(self, name):
        return self.values if name.lower() == "x-robots-tag" else None


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)

    def open(self, request, timeout):
        if len(self.responses) == 1:
            return self.responses[0]
        return self.responses.pop(0)


class PublicUrlValidationTests(unittest.TestCase):
    def test_normalizes_a_public_url(self):
        value = validate_public_url("example.com/path?q=1#fragment", resolver=resolver_for("93.184.216.34"))
        self.assertEqual(value, "https://example.com/path?q=1")

    def test_rejects_non_public_records_even_when_a_public_record_exists(self):
        with self.assertRaises(UnsafeUrlError):
            validate_public_url("https://example.com", resolver=resolver_for("93.184.216.34", "127.0.0.1"))

    def test_rejects_credentials_and_nonstandard_ports(self):
        with self.assertRaises(UnsafeUrlError):
            validate_public_url("https://user:pass@example.com", resolver=resolver_for("93.184.216.34"))
        with self.assertRaises(UnsafeUrlError):
            validate_public_url("https://example.com:8080", resolver=resolver_for("93.184.216.34"))

    def test_rejects_non_http_schemes(self):
        with self.assertRaises(UnsafeUrlError):
            validate_public_url("file:///etc/hosts", resolver=resolver_for("93.184.216.34"))

    def test_rejects_private_ipv6(self):
        with self.assertRaises(UnsafeUrlError):
            validate_public_url("https://example.com", resolver=resolver_for("::1"))

    def test_accepts_public_ipv6(self):
        value = validate_public_url("https://example.com", resolver=resolver_for("2606:2800:220:1:248:1893:25c8:1946"))
        self.assertEqual(value, "https://example.com/")

    @patch("url_safety.build_opener")
    @patch("url_safety.validate_public_url")
    def test_revalidates_and_blocks_private_redirect(self, validate, build):
        validate.side_effect = ["https://example.com/", UnsafeUrlError("private redirect")]
        build.return_value = FakeOpener([FakeResponse(302, {"Location": "http://127.0.0.1/"})])
        result = safe_fetch("https://example.com")
        self.assertIn("private redirect", result.error)
        self.assertEqual(len(result.redirect_chain), 1)

    @patch("url_safety.build_opener")
    @patch("url_safety.validate_public_url", side_effect=lambda value: value)
    def test_stops_after_redirect_limit(self, validate, build):
        build.return_value = FakeOpener([FakeResponse(302, {"Location": "/again"})])
        result = safe_fetch("https://example.com/")
        self.assertEqual(result.error, "Too many redirects")

    @patch("url_safety.build_opener")
    @patch("url_safety.validate_public_url", side_effect=lambda value: value)
    def test_follows_lowercase_location_header(self, validate, build):
        build.return_value = FakeOpener([
            FakeResponse(301, {"location": "/final"}),
            FakeResponse(200, {"content-type": "text/html"}, b"<h1>Final</h1>"),
        ])
        result = safe_fetch("https://example.com/start")
        self.assertEqual(result.url, "https://example.com/final")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.redirect_chain, [{"url": "https://example.com/start", "status_code": 301}])

    @patch("url_safety.build_opener")
    @patch("url_safety.validate_public_url", side_effect=lambda value: value)
    def test_rejects_oversized_response(self, validate, build):
        build.return_value = FakeOpener([FakeResponse(200, {"Content-Type": "text/html"}, b"x" * 11)])
        result = safe_fetch("https://example.com/", max_bytes=10)
        self.assertIn("exceeds 10 byte", result.error)

    @patch("url_safety.build_opener")
    @patch("url_safety.validate_public_url", side_effect=lambda value: value)
    def test_decodes_declared_charset(self, validate, build):
        build.return_value = FakeOpener([FakeResponse(200, {"Content-Type": "text/html; charset=latin-1"}, "café".encode("latin-1"))])
        result = safe_fetch("https://example.com/")
        self.assertEqual(result.body, "café")

    @patch("url_safety.build_opener")
    @patch("url_safety.validate_public_url", side_effect=lambda value: value)
    def test_preserves_x_robots_response_field_boundaries(self, validate, build):
        response = FakeResponse(200, MultiValueHeaders(["bingbot: noindex", "index, follow"]), b"<h1>Tool</h1>")
        build.return_value = FakeOpener([response])
        result = safe_fetch("https://example.com/")
        self.assertEqual(result.headers["X-Robots-Tag"], "bingbot: noindex\nindex, follow")
