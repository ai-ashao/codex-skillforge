import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_page import analyze_delivery, analyze_html, parse_directives, validate_hreflang_targets  # noqa: E402
from url_safety import UnsafeUrlError  # noqa: E402
from unittest.mock import patch


class PageCheckTests(unittest.TestCase):
    def test_short_title_is_not_failed_by_length(self):
        checks = analyze_html("<title>Short</title><h1>Useful tool</h1>", "https://example.com/tool", "useful tool", True)
        self.assertEqual(checks["title"]["status"], "pass")

    def test_marks_target_query_unassessed_when_none_is_supplied(self):
        checks = analyze_html("<title>Example</title><h1>Example</h1>", "https://example.com/", None, False)
        self.assertEqual(checks["target_query"]["status"], "unassessed")

    def test_delivery_classifies_expected_404_and_server_error(self):
        self.assertEqual(analyze_delivery(404, {"Content-Type": "text/html"}, True)["status"], "fail")
        self.assertEqual(analyze_delivery(503, {"Content-Type": "text/html"}, False)["status"], "fail")

    def test_delivery_marks_auth_and_non_html_unassessed_or_review(self):
        self.assertEqual(analyze_delivery(403, {}, True)["status"], "unassessed")
        self.assertEqual(analyze_delivery(200, {"Content-Type": "application/pdf"}, True)["status"], "review")

    def test_combines_meta_googlebot_and_x_robots_tag(self):
        html = '<meta name="googlebot" content="nofollow"><h1>Tool</h1>'
        checks = analyze_html(html, "https://example.com/tool", None, True, {"X-Robots-Tag": "googlebot: noindex, max-snippet:-1"})
        indexability = checks["indexability_directives"]
        self.assertEqual(indexability["status"], "fail")
        self.assertIn("noindex", indexability["directives"])
        self.assertIn("nofollow", indexability["directives"])

    def test_ignores_bingbot_only_x_robots_directives_for_googlebot(self):
        checks = analyze_html(
            "<h1>Tool</h1>",
            "https://example.com/tool",
            None,
            True,
            {"X-Robots-Tag": "bingbot: noindex, nofollow"},
        )
        indexability = checks["indexability_directives"]
        self.assertEqual(indexability["status"], "info")
        self.assertNotIn("noindex", indexability["directives"])
        self.assertEqual(indexability["ignored_scoped_directives"]["bingbot"], ["nofollow", "noindex"])

    def test_resets_x_robots_scope_between_response_fields(self):
        parsed = parse_directives(
            None,
            None,
            "bingbot: noindex, nofollow\nindex, follow",
            target_agent="googlebot",
        )
        self.assertEqual(parsed["directives"], ["follow", "index"])
        self.assertEqual(parsed["ignored_scoped_directives"]["bingbot"], ["nofollow", "noindex"])

    def test_parses_json_ld_graph_types_and_context(self):
        html = '<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"WebSite"},{"@type":["Organization","Thing"]}]}</script>'
        check = analyze_html(html, "https://example.com/", None, False)["json_ld"]
        self.assertEqual(check["parseable_blocks"], 1)
        self.assertEqual(check["types"], ["Organization", "Thing", "WebSite"])
        self.assertTrue(check["semantic_review_required"])

    def test_reports_json_ld_syntax_error(self):
        html = '<script type="application/ld+json">{"@type":}</script>'
        check = analyze_html(html, "https://example.com/", None, False)["json_ld"]
        self.assertEqual(check["status"], "warn")
        self.assertEqual(len(check["parse_errors"]), 1)

    def test_supports_multiple_json_ld_blocks(self):
        html = '<script type="application/ld+json">{"@type":"WebSite"}</script><script type="application/ld+json">[{"@type":"FAQPage"}]</script>'
        check = analyze_html(html, "https://example.com/", None, False)["json_ld"]
        self.assertEqual(check["blocks_found"], 2)
        self.assertEqual(check["parseable_blocks"], 2)

    def test_distinguishes_declared_and_nested_json_ld_types(self):
        html = '<script type="application/ld+json">{"@type":"Product","offers":{"@type":"Offer"}}</script>'
        check = analyze_html(html, "https://example.com/", None, False)["json_ld"]
        self.assertEqual(check["top_level_types"], ["Product"])
        self.assertEqual(check["all_nested_types"], ["Offer", "Product"])

    def test_multilingual_page_tracks_self_reference_and_x_default(self):
        html = '<html lang="en"><link rel="alternate" hreflang="en" href="/tool"><link rel="alternate" hreflang="zh-CN" href="/zh/tool"><link rel="alternate" hreflang="x-default" href="/tool"></html>'
        check = analyze_html(html, "https://example.com/tool", None, False, expected_multilingual=True)["hreflang"]
        self.assertEqual(check["status"], "info")
        self.assertTrue(check["has_self_reference"])
        self.assertTrue(check["has_x_default"])

    def test_multilingual_page_reports_invalid_duplicate_and_missing_self(self):
        html = '<html><link rel="alternate" hreflang="english" href="/en"><link rel="alternate" hreflang="ENGLISH" href="/en-2"></html>'
        check = analyze_html(html, "https://example.com/tool", None, False, expected_multilingual=True)["hreflang"]
        self.assertEqual(check["status"], "warn")
        self.assertTrue(check["invalid_codes"])
        self.assertEqual(check["duplicate_codes"], ["english"])

    def test_reviews_html_lang_self_hreflang_primary_language_mismatch(self):
        html = '<html lang="fr"><link rel="alternate" hreflang="en-US" href="/tool"></html>'
        check = analyze_html(html, "https://example.com/tool", None, False, expected_multilingual=True)["hreflang"]
        self.assertEqual(check["status"], "review")
        self.assertFalse(check["html_lang_matches_self_reference"])

    def test_accepts_compatible_html_lang_and_regional_self_hreflang(self):
        html = '<html lang="en"><link rel="alternate" hreflang="en-US" href="/tool"></html>'
        check = analyze_html(html, "https://example.com/tool", None, False, expected_multilingual=True)["hreflang"]
        self.assertEqual(check["status"], "info")
        self.assertTrue(check["html_lang_matches_self_reference"])

    def test_uses_canonical_as_hreflang_self_reference_target(self):
        html = '<html lang="en"><link rel="canonical" href="https://example.com/tool"><link rel="alternate" hreflang="en" href="/tool"></html>'
        check = analyze_html(html, "https://example.com/tool?source=redirect", None, False, expected_multilingual=True)["hreflang"]
        self.assertEqual(check["self_reference_target"], "https://example.com/tool")
        self.assertTrue(check["has_self_reference"])
        self.assertEqual(check["status"], "info")

    def test_single_language_scope_does_not_claim_declarations_exist(self):
        check = analyze_html("<h1>Tool</h1>", "https://example.com/tool", None, False, expected_multilingual=False)["hreflang"]
        self.assertEqual(check["status"], "info")
        self.assertIn("No language declarations", check["detail"])

    def test_relative_canonical_and_nested_heading_are_resolved(self):
        html = '<link rel="canonical" href="/tool"><h1>Useful <strong>Tool &amp; Guide</strong></h1>'
        checks = analyze_html(html, "https://example.com/tool", None, False)
        self.assertEqual(checks["canonical"]["status"], "info")
        self.assertEqual(checks["headings"]["h1"], ["Useful Tool & Guide"])

    def test_static_link_inventory_does_not_claim_link_validation(self):
        html = '<a href="/one">One</a><a href="https://other.example/two">Two</a>'
        check = analyze_html(html, "https://example.com/", None, False)["static_link_inventory"]
        self.assertEqual(check["internal"], 1)
        self.assertEqual(check["external"], 1)

    @patch("check_page.safe_fetch", side_effect=UnsafeUrlError("blocked alternate"))
    def test_hreflang_validation_records_unsafe_target(self, fetch):
        result = validate_hreflang_targets([{"hreflang": "en", "href": "http://127.0.0.1/"}], "https://example.com/", 5, 5)
        self.assertEqual(result["status"], "warn")
        self.assertIn("blocked alternate", result["results"][0]["error"])
