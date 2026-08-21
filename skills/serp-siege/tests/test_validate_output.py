from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_output.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

spec = importlib.util.spec_from_file_location("validate_output", SCRIPT)
assert spec and spec.loader
validate_output = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_output)


class ValidateOutputTests(unittest.TestCase):
    def test_three_acceptance_scenarios_pass(self) -> None:
        for name in (
            "competitor-led-image-tools.md",
            "existing-site-expansion.md",
            "constraint-heavy-platform.md",
        ):
            with self.subTest(name=name):
                text = (FIXTURES / name).read_text(encoding="utf-8")
                self.assertEqual([], validate_output.validate(text))

    def test_opportunity_decision_fields_are_rejected(self) -> None:
        text = (FIXTURES / "constraint-heavy-platform.md").read_text(encoding="utf-8")
        text = text.replace(
            "- **Planning Confidence:** `LOW`",
            "- **Planning Confidence:** `LOW`\n- **Decision:** `NO_GO`",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn("Execution report must not contain field: Decision.", errors)
        self.assertIn("Execution report must not contain GO/NO_GO decisions.", errors)

    def test_reject_page_may_omit_url_but_requires_reason(self) -> None:
        text = (FIXTURES / "constraint-heavy-platform.md").read_text(encoding="utf-8")
        text = text.replace(
            "| `REJECT` | | | protected-media-extraction | protected media downloader | acquisition | none | `REJECT` | outside the authorized execution scope |",
            "| `REJECT` | | | protected-media-extraction | protected media downloader | acquisition | none | `REJECT` | |",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn("SEO Page Map REJECT row 2 requires Reason.", errors)

    def test_execution_report_requires_serp_coverage_map(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        start = text.index("## SERP Coverage Map")
        end = text.index("## SEO Page Map")
        errors = validate_output.validate(text[:start] + text[end:])
        self.assertIn("Missing required heading: SERP Coverage Map.", errors)

    def test_proposed_page_requires_cluster(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        text = text.replace(
            "| `NEW_TOOL_PAGE` | /image-compressor | | image-compression | image compressor | tool | client-side image pipeline | `P0` | establishes the core workflow |",
            "| `NEW_TOOL_PAGE` | /image-compressor | | MISSING | image compressor | tool | client-side image pipeline | `P0` | establishes the core workflow |",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn("SEO Page Map row 1 is not bound to a target cluster.", errors)

    def test_deprecated_evidence_label_is_rejected(self) -> None:
        text = (FIXTURES / "constraint-heavy-platform.md").read_text(encoding="utf-8")
        text = text.replace("MODEL_INFERENCE", "INFERENCE", 1)
        errors = validate_output.validate(text)
        self.assertIn("Deprecated evidence label found: INFERENCE.", errors)

    def test_same_page_requires_canonical_parent(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        marker = "| `NEW_TOOL_PAGE` | /image-compressor | | image-compression | image compressor | tool | client-side image pipeline | `P0` | establishes the core workflow |"
        replacement = marker + "\n| `SAME_PAGE` | | | image-compression-synonym | compress image | tool | client-side image pipeline | `HOLD` | merge duplicate intent |"
        text = text.replace(marker, replacement, 1)
        errors = validate_output.validate(text)
        self.assertIn("SEO Page Map SAME_PAGE row 2 requires Canonical Parent.", errors)

    def test_p1_and_p2_may_be_none(self) -> None:
        text = (FIXTURES / "constraint-heavy-platform.md").read_text(encoding="utf-8")
        self.assertEqual([], validate_output.validate(text))

if __name__ == "__main__":
    unittest.main()
