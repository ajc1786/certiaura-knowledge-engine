from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

IMPORT_DIR = Path(__file__).resolve().parents[1] / "Import"
if str(IMPORT_DIR) not in sys.path:
    sys.path.insert(0, str(IMPORT_DIR))

from historical_asset_backfill import (  # noqa: E402
    discover_historical_assets,
    load_policy,
    plan_full_historical_reconciliation,
)


class FullHistoricalBackfillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "Database").mkdir(parents=True)
        self.register = self.repo / "Database" / "MASTER_ASSET_REGISTER.csv"
        with self.register.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=[
                    "Universal Asset Identifier", "Asset Title", "Asset Type",
                    "Knowledge System", "Repository Path", "Version", "Status",
                    "Owner", "Completion Percentage", "Build Provenance"
                ],
            )
            writer.writeheader()
            writer.writerow({
                "Universal Asset Identifier": "CERT-SYS-000010",
                "Asset Title": "EXISTING GOVERNANCE",
                "Asset Type": "Governance Control",
                "Knowledge System": "SYS",
                "Repository Path": "00_Governance/EXISTING_GOVERNANCE.md",
                "Version": "1.0.0",
                "Status": "ACTIVE",
                "Owner": "Certiaura",
                "Completion Percentage": "100",
                "Build Provenance": "CERT-BUILD-0001",
            })
        (self.repo / "00_Governance").mkdir()
        (self.repo / "00_Governance" / "EXISTING_GOVERNANCE.md").write_text(
            "# Existing Governance\n\n**Version:** 1.1.0\n", encoding="utf-8"
        )
        (self.repo / "08_Product_Passports" / "Standards").mkdir(parents=True)
        (self.repo / "08_Product_Passports" / "Standards" / "NEW_STANDARD.md").write_text(
            "# New Standard\n\n**Version:** 1.0.0\n", encoding="utf-8"
        )
        (self.repo / "08_Product_Passports" / "Schemas").mkdir(parents=True)
        (self.repo / "08_Product_Passports" / "Schemas" / "new.schema.json").write_text(
            json.dumps({"title": "New Schema", "version": "1.0.0"}), encoding="utf-8"
        )
        (self.repo / "13_Project_Genesis" / "Tests").mkdir(parents=True)
        (self.repo / "13_Project_Genesis" / "Tests" / "test_ignore.py").write_text("pass\n", encoding="utf-8")
        (self.repo / "Documentation" / "Build_Records" / "0009").mkdir(parents=True)
        (self.repo / "Documentation" / "Build_Records" / "0009" / "FILE_INVENTORY.csv").write_text(
            "source_build,canonical_path\n0009,08_Product_Passports/Standards/NEW_STANDARD.md\n",
            encoding="utf-8",
        )
        self.manifest = {
            "build_number": "0038",
            "formal_assets": [],
        }

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_census_registers_reusable_assets_and_excludes_tests(self) -> None:
        census = discover_historical_assets(self.repo, load_policy(None), {}, self.register)
        paths = {x["repository_path"] for x in census["registerable_assets"]}
        self.assertIn("00_Governance/EXISTING_GOVERNANCE.md", paths)
        self.assertIn("08_Product_Passports/Standards/NEW_STANDARD.md", paths)
        self.assertIn("08_Product_Passports/Schemas/new.schema.json", paths)
        self.assertNotIn("13_Project_Genesis/Tests/test_ignore.py", paths)
        self.assertNotIn("Database/MASTER_ASSET_REGISTER.csv", paths)

    def test_existing_uai_is_preserved_and_missing_assets_are_allocated(self) -> None:
        report = plan_full_historical_reconciliation(
            self.repo, self.manifest, None, self.register, {}
        )
        self.assertTrue(report["valid"], report["conflicts"])
        changes = {x["path"]: x for x in report["changes"]}
        self.assertEqual(
            changes["00_Governance/EXISTING_GOVERNANCE.md"]["uai"],
            "CERT-SYS-000010",
        )
        self.assertTrue(
            changes["08_Product_Passports/Standards/NEW_STANDARD.md"]["uai"].startswith("CERT-PPS-")
        )

    def test_prior_build_provenance_is_read_from_inventory(self) -> None:
        census = discover_historical_assets(self.repo, load_policy(None), {}, self.register)
        asset = next(
            x for x in census["registerable_assets"]
            if x["repository_path"] == "08_Product_Passports/Standards/NEW_STANDARD.md"
        )
        self.assertEqual(asset["source_builds"], ["0009"])
        self.assertEqual(asset["build_provenance"], ["CERT-BUILD-0009"])

    def test_active_orphan_register_entry_blocks_reconciliation(self) -> None:
        with self.register.open("a", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow([
                "CERT-PPS-000099", "MISSING ASSET", "Standard", "PPS",
                "08_Product_Passports/Standards/MISSING.md", "1.0.0", "ACTIVE",
                "Certiaura", "100", "CERT-BUILD-0008"
            ])
        report = plan_full_historical_reconciliation(
            self.repo, self.manifest, None, self.register, {}
        )
        self.assertFalse(report["valid"])
        self.assertTrue(any(x["code"] == "ORPHAN_MASTER_ASSET_REGISTER_ENTRY" for x in report["conflicts"]))

    def test_retired_orphan_register_entry_is_allowed(self) -> None:
        with self.register.open("a", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow([
                "CERT-PPS-000099", "RETIRED ASSET", "Standard", "PPS",
                "08_Product_Passports/Standards/RETIRED.md", "1.0.0", "RETIRED",
                "Certiaura", "100", "CERT-BUILD-0008"
            ])
        report = plan_full_historical_reconciliation(
            self.repo, self.manifest, None, self.register, {}
        )
        self.assertTrue(report["valid"], report["conflicts"])

    def test_duplicate_embedded_uai_is_blocked(self) -> None:
        first = self.repo / "08_Product_Passports" / "Standards" / "DUPLICATE_ONE.md"
        second = self.repo / "08_Product_Passports" / "Standards" / "DUPLICATE_TWO.md"
        first.write_text("# One\n\n**UAI:** CERT-PPS-000777\n", encoding="utf-8")
        second.write_text("# Two\n\n**UAI:** CERT-PPS-000777\n", encoding="utf-8")
        report = plan_full_historical_reconciliation(
            self.repo, self.manifest, None, self.register, {}
        )
        self.assertFalse(report["valid"])
        self.assertTrue(any(x["code"] == "DUPLICATE_INCOMING_UAI" for x in report["conflicts"]))

    def test_duplicate_titles_on_different_paths_do_not_merge(self) -> None:
        first = self.repo / "08_Product_Passports" / "Standards" / "TITLE_ONE.md"
        second = self.repo / "08_Product_Passports" / "Standards" / "TITLE_TWO.md"
        first.write_text("# Shared Title\n", encoding="utf-8")
        second.write_text("# Shared Title\n", encoding="utf-8")
        report = plan_full_historical_reconciliation(
            self.repo, self.manifest, None, self.register, {}
        )
        self.assertTrue(report["valid"], report["conflicts"])
        changes = [x for x in report["changes"] if x["path"] in {
            "08_Product_Passports/Standards/TITLE_ONE.md",
            "08_Product_Passports/Standards/TITLE_TWO.md",
        }]
        self.assertEqual(len(changes), 2)
        self.assertNotEqual(changes[0]["uai"], changes[1]["uai"])


if __name__ == "__main__":
    unittest.main()
