import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_site import evaluate_robots, parse_robots, parse_sitemap_document  # noqa: E402


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
