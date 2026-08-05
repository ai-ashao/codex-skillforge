import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_page import analyze_html  # noqa: E402


class PageCheckTests(unittest.TestCase):
    def test_flags_an_unexpected_noindex_without_using_length_thresholds(self):
        html = """
        <html><head><title>Short title</title><meta name="robots" content="noindex"></head>
        <body><h1>Useful tool</h1><img src="preview.png"><img src="decoration.svg" alt=""></body></html>
        """
        checks = analyze_html(html, "https://example.com/tool", keyword="useful tool", expected_indexable=True)
        self.assertEqual(checks["title"]["status"], "pass")
        self.assertEqual(checks["robots_meta"]["status"], "fail")
        self.assertEqual(checks["images"]["missing_alt_attribute"], 1)
        self.assertEqual(checks["target_query"]["status"], "info")

    def test_marks_target_query_unassessed_when_none_is_supplied(self):
        checks = analyze_html("<title>Example</title><h1>Example</h1>", "https://example.com/", keyword=None, expected_indexable=False)
        self.assertEqual(checks["target_query"]["status"], "unassessed")
        self.assertEqual(checks["headings"]["status"], "info")
