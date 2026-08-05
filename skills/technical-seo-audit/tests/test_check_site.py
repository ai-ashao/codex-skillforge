import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_site import evaluate_robots, parse_robots, parse_sitemap_document, sitemap_result  # noqa: E402


class RobotsTests(unittest.TestCase):
    def test_combines_consecutive_user_agents(self):
        groups, _ = parse_robots("User-agent: Googlebot\nUser-agent: Bingbot\nDisallow: /")
        self.assertFalse(evaluate_robots(groups, "googlebot", "/page")["allowed"])
        self.assertFalse(evaluate_robots(groups, "bingbot", "/page")["allowed"])

    def test_starts_new_group_after_non_user_agent_directive(self):
        groups, _ = parse_robots("User-agent: Googlebot\nCrawl-delay: 5\nUser-agent: Bingbot\nDisallow: /")
        self.assertTrue(evaluate_robots(groups, "googlebot", "/page")["allowed"])
        self.assertFalse(evaluate_robots(groups, "bingbot", "/page")["allowed"])

    def test_specific_googlebot_group_overrides_wildcard(self):
        groups, _ = parse_robots("User-agent: *\nDisallow: /\n\nUser-agent: Googlebot\nAllow: /")
        self.assertTrue(evaluate_robots(groups, "googlebot", "/page")["allowed"])

    def test_longer_allow_rule_wins(self):
        groups, _ = parse_robots("User-agent: *\nDisallow: /\nAllow: /public/")
        result = evaluate_robots(groups, "googlebot", "/public/page")
        self.assertTrue(result["allowed"])
        self.assertFalse(result["site_wide_block"])

    def test_target_path_can_be_blocked_without_sitewide_block(self):
        groups, _ = parse_robots("User-agent: *\nDisallow: /private/\nAllow: /")
        self.assertFalse(evaluate_robots(groups, "googlebot", "/private/page")["allowed"])
        self.assertTrue(evaluate_robots(groups, "googlebot", "/public/page")["allowed"])

    def test_tied_allow_rule_wins(self):
        groups, _ = parse_robots("User-agent: *\nDisallow: /same\nAllow: /same")
        self.assertTrue(evaluate_robots(groups, "googlebot", "/same")["allowed"])


class SitemapTests(unittest.TestCase):
    def test_parses_urlset_and_target_inclusion(self):
        xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/tool</loc></url></urlset>'
        result = parse_sitemap_document(xml, "https://example.com/sitemap.xml", "https://example.com/tool")
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["target_url_included"])

    def test_reports_duplicates_and_foreign_origin(self):
        xml = '<urlset><url><loc>https://other.example/a</loc></url><url><loc>https://other.example/a</loc></url></urlset>'
        result = parse_sitemap_document(xml, "https://example.com/sitemap.xml", "https://example.com/")
        self.assertEqual(result["duplicate_count"], 1)
        self.assertEqual(result["foreign_origins"], ["other.example"])

    def test_parses_sitemap_index(self):
        xml = '<sitemapindex><sitemap><loc>https://example.com/child.xml</loc></sitemap></sitemapindex>'
        result = parse_sitemap_document(xml, "https://example.com/sitemap.xml", "https://example.com/")
        self.assertEqual(result["type"], "sitemapindex")
        self.assertEqual(result["locations"], ["https://example.com/child.xml"])

    def test_reports_malformed_xml(self):
        self.assertEqual(parse_sitemap_document("<urlset>", "https://example.com/sitemap.xml", "https://example.com/")["status"], "warn")

    def test_rejects_unknown_root_element(self):
        result = parse_sitemap_document("<feed><loc>https://example.com/</loc></feed>", "https://example.com/sitemap.xml", "https://example.com/")
        self.assertEqual(result["status"], "warn")

    def test_reports_invalid_relative_loc(self):
        result = parse_sitemap_document("<urlset><url><loc>/relative</loc></url></urlset>", "https://example.com/sitemap.xml", "https://example.com/")
        self.assertEqual(result["status"], "warn")
        self.assertEqual(result["invalid_locations"], ["/relative"])

    def test_ignores_image_loc_when_parsing_page_urls(self):
        xml = '''<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
        <url><loc>https://example.com/tool</loc><image:image><image:loc>https://cdn.example.com/tool.webp</image:loc></image:image></url>
        </urlset>'''
        result = parse_sitemap_document(xml, "https://example.com/sitemap.xml", "https://example.com/tool")
        self.assertEqual(result["locations"], ["https://example.com/tool"])
        self.assertEqual(result["foreign_origins"], [])

    def test_reviews_valid_but_empty_sitemap(self):
        result = parse_sitemap_document("<urlset></urlset>", "https://example.com/sitemap.xml", "https://example.com/")
        self.assertEqual(result["status"], "review")
        self.assertEqual(result["entry_count"], 0)

    @patch("check_site.safe_fetch")
    def test_counts_sitemaps_discarded_by_document_bound(self, fetch):
        children = "".join(f"<sitemap><loc>https://example.com/{index}.xml</loc></sitemap>" for index in range(5))

        def response(url, timeout):
            body = f"<sitemapindex>{children}</sitemapindex>" if url.endswith("sitemap.xml") else "<urlset><url><loc>https://example.com/tool</loc></url></urlset>"
            return SimpleNamespace(error=None, status_code=200, body=body, url=url)

        fetch.side_effect = response
        result = sitemap_result("https://example.com/", "https://example.com/tool", [], 5, 2)
        self.assertEqual(result["documents_checked"], 2)
        self.assertEqual(result["documents_queued_remaining"], 0)
        self.assertEqual(result["documents_bounded_out"], 4)
        self.assertEqual(result["documents_not_checked"], 4)

    @patch("check_site.safe_fetch")
    def test_does_not_fetch_invalid_relative_child_sitemap(self, fetch):
        fetch.return_value = SimpleNamespace(
            error=None,
            status_code=200,
            body="<sitemapindex><sitemap><loc>/child.xml</loc></sitemap></sitemapindex>",
            url="https://example.com/sitemap.xml",
        )
        result = sitemap_result("https://example.com/", "https://example.com/tool", [], 5, 12)
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(result["documents_checked"], 1)
        self.assertEqual(result["documents"][0]["invalid_locations"], ["/child.xml"])
