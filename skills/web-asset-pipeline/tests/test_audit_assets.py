import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_assets.py"


class AssetAuditTests(unittest.TestCase):
    def run_audit(self, directory: Path):
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--format", "json", str(directory)],
            check=True,
            text=True,
            capture_output=True,
        )
        return json.loads(result.stdout)

    def test_reports_png_dimensions_and_size_review(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            asset = Path(temporary_directory) / "hero.png"
            asset.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + (3000).to_bytes(4, "big") + (1600).to_bytes(4, "big") + b"\x00" * 260000)
            records = self.run_audit(asset.parent)
        self.assertEqual(records[0]["dimensions"], "3000x1600")
        self.assertIn("review modern format", records[0]["review"])
        self.assertIn("review rendered size", records[0]["review"])

    def test_reports_svg_viewbox(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            asset = Path(temporary_directory) / "logo.svg"
            asset.write_text('<svg viewBox="0 0 48 24"><path d="M0 0"/></svg>', encoding="utf-8")
            records = self.run_audit(asset.parent)
        self.assertEqual(records[0]["format"], "svg")
        self.assertEqual(records[0]["dimensions"], "48x24")

    def test_scans_only_the_requested_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            requested = directory / "requested.svg"
            requested.write_text('<svg viewBox="0 0 1 1"/>', encoding="utf-8")
            (directory / "unrequested.svg").write_text('<svg viewBox="0 0 2 2"/>', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--format", "json", str(requested)],
                check=True,
                text=True,
                capture_output=True,
            )
        records = json.loads(result.stdout)
        self.assertEqual([record["path"] for record in records], [str(requested)])
