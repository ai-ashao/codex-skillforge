import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit import collect_evidence  # noqa: E402


class UnifiedAuditTests(unittest.TestCase):
    @patch("audit.audit_site")
    @patch("audit.audit_page")
    def test_checks_site_signals_at_final_redirect_origin(self, page_audit, site_audit):
        page_audit.return_value = {
            "url": "https://www.example.com/tool",
            "final_url": "https://example.com/tool",
            "checks": {},
        }
        site_audit.return_value = {"origin": "https://example.com/", "robots": {}, "sitemap": {}}

        evidence = collect_evidence(
            "https://www.example.com/tool",
            None,
            True,
            True,
            False,
            12,
            12,
            15,
        )

        site_audit.assert_called_once_with("https://example.com/tool", 15, 12)
        self.assertEqual(evidence["requested_origin"], "https://www.example.com")
        self.assertEqual(evidence["final_origin"], "https://example.com")
        self.assertEqual(evidence["site_audit_origin"], "https://example.com")
        self.assertTrue(evidence["origin_changed"])
