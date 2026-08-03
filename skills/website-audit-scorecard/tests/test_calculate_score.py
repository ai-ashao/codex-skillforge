"""Regression tests for the deterministic audit-score calculator."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("calculator", ROOT / "scripts" / "calculate_score.py")
calculator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(calculator)


class CalculateScoreTests(unittest.TestCase):
    def load_sample(self) -> dict:
        return json.loads((ROOT / "assets" / "sample-audit.json").read_text(encoding="utf-8"))

    def test_sample_matches_saved_result(self) -> None:
        expected = json.loads((ROOT / "assets" / "sample-result.json").read_text(encoding="utf-8"))
        self.assertEqual(calculator.calculate(self.load_sample()), expected)

    def test_missing_rating_is_rejected(self) -> None:
        audit = {"ratings": {"PV1": {"evidence": "A"}}}
        with self.assertRaisesRegex(ValueError, "must include rating"):
            calculator.calculate(audit)

    def test_unknown_gate_is_rejected(self) -> None:
        audit = {"ratings": {}, "gates": [{"id": "G9", "triggered": True}]}
        with self.assertRaisesRegex(ValueError, "Unknown gate ID"):
            calculator.calculate(audit)

    def test_unassessed_monetization_is_not_claimed_assessed(self) -> None:
        result = calculator.calculate({"ratings": {"PV1": {"rating": 3, "evidence": "A"}}})
        self.assertEqual(result["monetization_status"], "unassessed")

    def test_g5_overrides_unassessed_monetization(self) -> None:
        result = calculator.calculate({
            "ratings": {},
            "gates": [{"id": "G5", "triggered": True, "note": "Policy blocker"}],
        })
        self.assertEqual(result["monetization_status"], "not ready")


if __name__ == "__main__":
    unittest.main()
