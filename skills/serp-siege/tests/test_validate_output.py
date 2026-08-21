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
            "| `REJECT` | | /media-metadata-viewer | protected-media-extraction | protected media downloader | acquisition | none | `REJECT` | outside the authorized execution scope |",
            "| `REJECT` | | /media-metadata-viewer | protected-media-extraction | protected media downloader | acquisition | none | `REJECT` | |",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn("SEO Page Map REJECT row 2 requires Reason.", errors)

    def test_reject_page_requires_canonical_parent(self) -> None:
        text = (FIXTURES / "constraint-heavy-platform.md").read_text(encoding="utf-8")
        text = text.replace(
            "| `REJECT` | | /media-metadata-viewer | protected-media-extraction | protected media downloader | acquisition | none | `REJECT` | outside the authorized execution scope |",
            "| `REJECT` | | | protected-media-extraction | protected media downloader | acquisition | none | `REJECT` | outside the authorized execution scope |",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn(
            "SEO Page Map REJECT row 2 requires Canonical Parent.", errors
        )

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

    def test_invalid_competitor_evidence_label_is_rejected(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        text = text.replace(
            "`MODEL_INFERENCE`: fixture assumption",
            "`BOGUS_EVIDENCE`: fixture assumption",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn(
            "Competitor Map row 1 has invalid evidence labels: BOGUS_EVIDENCE.",
            errors,
        )

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

    def test_supplied_destination_requires_user_or_upstream_basis(self) -> None:
        text = (FIXTURES / "existing-site-expansion.md").read_text(encoding="utf-8")
        text = text.replace(
            "`FIRST_PARTY`: user-selected existing-site page",
            "`MODEL_INFERENCE`: inferred destination",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn(
            "Supplied Destination requires FIRST_PARTY or USER_SUPPLIED_THIRD_PARTY basis.",
            errors,
        )

    def test_live_or_inferred_claim_requires_traceable_detail(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        text = text.replace(
            "`MODEL_INFERENCE`: fixture assumption",
            "`MODEL_INFERENCE`",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn(
            "Competitor Map row 1 requires a traceable source or observation.",
            errors,
        )

    def test_new_page_must_not_set_canonical_parent(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        text = text.replace(
            "| `NEW_TOOL_PAGE` | /image-compressor | | image-compression |",
            "| `NEW_TOOL_PAGE` | /image-compressor | /image-tools | image-compression |",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn(
            "SEO Page Map new-page row 1 must not set Canonical Parent.", errors
        )

    def test_proposed_urls_must_be_unique(self) -> None:
        text = (FIXTURES / "constraint-heavy-platform.md").read_text(encoding="utf-8")
        text = text.replace(
            "| `REJECT` | | /media-metadata-viewer | protected-media-extraction |",
            "| `REJECT` | /media-metadata-viewer | /media-metadata-viewer | protected-media-extraction |",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn(
            "SEO Page Map row 2 duplicates Proposed URL: /media-metadata-viewer.",
            errors,
        )

    def test_cluster_page_decision_must_match_across_maps(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        text = text.replace("`NEW_TOOL_PAGE` | `P0`", "`NEW_LANDING_PAGE` | `P0`", 1)
        errors = validate_output.validate(text)
        self.assertIn(
            "Cluster image-compression has inconsistent Page Decision.", errors
        )

    def test_keyword_cluster_must_be_covered_by_seo_page_map(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        row = "| image-resize | `ADJACENT_TOOL` | image resizer | resize an image | resize jpg | `NEW_TOOL_PAGE` | `P1` | `MODEL_INFERENCE`: fixture assumption |\n\n"
        text = text.replace("## Feature Coverage Map", row + "## Feature Coverage Map", 1)
        errors = validate_output.validate(text)
        self.assertIn(
            "Keyword cluster image-resize is missing from SEO Page Map.", errors
        )

    def test_first_batch_group_and_single_core_are_enforced(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        text = text.replace("| `CORE` | image-compression |", "| `FEATURED` | image-compression |", 1)
        errors = validate_output.validate(text)
        self.assertIn("First Batch row 1 has invalid Group.", errors)
        self.assertIn("First Batch must contain exactly one CORE item.", errors)

    def test_out_of_shape_batch_requires_structured_deviation(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        text = text.replace(
            "- **First Batch Deviation:** The fixture is intentionally smaller than the default batch because it tests structure, not market scope.\n",
            "",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn(
            "First Batch outside the default shape requires First Batch Deviation.",
            errors,
        )

    def test_serp_missing_p0_expansion_must_be_core_or_hold(self) -> None:
        text = (FIXTURES / "existing-site-expansion.md").read_text(encoding="utf-8")
        text = text.replace(
            "| /markdown-word-counter | `CORE` | markdown-word-count |",
            "| /markdown-word-counter | `SUPPORTING` | markdown-word-count |",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn(
            "SERP-missing P0 cluster markdown-word-count must be the First Batch CORE or move to HOLD.",
            errors,
        )

    def test_existing_candidate_feature_requires_candidate_evidence(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        text = text.replace(
            "| `YES` | `YES` | `MISSING` | `PLANNED` | `P0` | `MODEL_INFERENCE`: fixture assumption |",
            "| `YES` | `YES` | `MISSING` | `EXISTING` | `P0` | `MODEL_INFERENCE`: fixture assumption |",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn(
            "Feature Coverage Map row 1 marks Candidate EXISTING without first-party or live-public evidence.",
            errors,
        )

    def test_seo_p0_page_must_be_in_first_batch(self) -> None:
        text = (FIXTURES / "competitor-led-image-tools.md").read_text(encoding="utf-8")
        text = text.replace(
            "| /image-compressor | `CORE` | image-compression | validates the main task | client-side image pipeline | core tool entry |\n",
            "",
            1,
        )
        errors = validate_output.validate(text)
        self.assertIn(
            "SEO P0 cluster image-compression is missing from First Batch.", errors
        )

if __name__ == "__main__":
    unittest.main()
