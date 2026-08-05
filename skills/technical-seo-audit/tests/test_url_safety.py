import socket
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from url_safety import UnsafeUrlError, validate_public_url  # noqa: E402


def resolver_for(*addresses):
    def resolve(hostname, port, type):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, port)) for address in addresses]

    return resolve


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
