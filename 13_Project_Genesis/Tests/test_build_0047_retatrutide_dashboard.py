from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_DIR = ROOT / "13_Project_Genesis" / "Validators"
if str(VALIDATOR_DIR) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_DIR))

from validate_retatrutide_longitudinal_dashboard import validate_alert, validate_journey, validate_repository


class Build0047Tests(unittest.TestCase):
    def load(self, rel: str):
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))

    def test_valid_journey_passes(self):
        data = self.load("05_Monitoring/Examples/Retatrutide/valid_longitudinal_journey.example.json")
        self.assertEqual([], validate_journey(data))

    def test_conditional_journey_passes_structurally(self):
        data = self.load("05_Monitoring/Examples/Retatrutide/conditional_insufficient_trend.example.json")
        self.assertEqual([], validate_journey(data))

    def test_invalid_autonomous_treatment_fails(self):
        data = self.load("05_Monitoring/Examples/Retatrutide/invalid_autonomous_treatment.example.json")
        self.assertTrue(validate_journey(data))

    def test_valid_alert_passes(self):
        data = self.load("05_Monitoring/Examples/Retatrutide/valid_alert_review.example.json")
        self.assertEqual([], validate_alert(data))

    def test_invalid_alert_action_fails(self):
        data = self.load("05_Monitoring/Examples/Retatrutide/invalid_alert_treatment_action.example.json")
        self.assertTrue(validate_alert(data))

    def test_repository_uses_exact_manifest_owned_paths(self):
        result = validate_repository(ROOT)
        self.assertTrue(result["valid"], result)
        self.assertGreater(result["owned_path_count"], 20)

    def test_package_resolver_deduplicates_identical_content_hashes(self):
        script = (ROOT / "Scripts/Run_Certiaura_Build_0047.ps1").read_text(encoding="ascii")
        self.assertIn("Group-Object -Property PackageSha256", script)
        self.assertIn("byte-identical copies", script)
        self.assertIn("Multiple distinct Build 0047 packages", script)
        self.assertIn("LatestRegression.package_sha256", script)
        self.assertIn("RegressionReportRoot", script)

    def test_package_resolver_uses_ps51_safe_generic_list_conversion(self):
        script = (ROOT / "Scripts/Run_Certiaura_Build_0047.ps1").read_text(encoding="ascii")
        self.assertIn("$ApprovedMatches = [object[]]$Matches.ToArray()", script)
        self.assertNotIn("$ApprovedMatches = @($Matches)", script)


    def test_predecessor_schema_and_shared_helper_paths_are_not_replaced(self):
        manifest = self.load("Documentation/Build_Records/0047/ASSET_INTENT_MANIFEST.json")
        paths = {item["path"] for item in manifest["files"]}
        self.assertNotIn("Schemas/retatrutide_longitudinal_journey.schema.json", paths)
        self.assertIn("Schemas/retatrutide_longitudinal_dashboard_journey.schema.json", paths)
        self.assertNotIn("13_Project_Genesis/Validators/build_asset_ownership.py", paths)
        self.assertIn("13_Project_Genesis/Validators/build_0047_asset_ownership.py", paths)

    def test_dry_run_blocks_nonidentical_collision_before_apply(self):
        manifest = self.load("Documentation/Build_Records/0047/ASSET_INTENT_MANIFEST.json")
        importer = ROOT / "13_Project_Genesis/Import/build_0047_transactional_import.py"
        collision_path = "Schemas/retatrutide_alert_review.schema.json"
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            package = temp / "candidate.zip"
            with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in manifest["files"]:
                    zf.write(ROOT / item["path"], item["path"])
            repo = temp / "repo"
            repo.mkdir()
            subprocess.run(["git", "-C", str(repo), "init"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Certiaura Test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
            register = repo / "Documentation/Master_Asset_Register.csv"
            register.parent.mkdir(parents=True)
            fields = [
                "Universal Asset Identifier", "Asset Name", "Knowledge System", "Asset Type", "Status", "Owner",
                "Parent Assets", "Last Review", "Notes", "Repository Path", "Supporting Files", "Version",
                "Completion Percentage", "Child Assets", "Relationship List", "Evidence Links", "Report Links",
                "Marketplace Links", "Next Review", "Change History", "Build Provenance", "Source Builds",
                "Registration Basis", "File SHA256", "Last Updated",
            ]
            with register.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
            collision = repo / collision_path
            collision.parent.mkdir(parents=True)
            collision.write_text("{\n  \"pre_existing\": true\n}\n", encoding="utf-8", newline="\n")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-m", "baseline"], check=True, capture_output=True)
            report = temp / "report.json"
            result = subprocess.run([
                sys.executable, "-B", str(importer),
                "--repository", str(repo),
                "--package", str(package),
                "--report", str(report),
            ], check=False, capture_output=True, text=True)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(payload["valid"])
            self.assertFalse(payload["applied"])
            self.assertEqual("FAILED_CLOSED", payload["transaction_status"])
            self.assertIn(collision_path, {item["path"] for item in payload["conflicts"]})

    def test_canonical_runner_uses_discovery_and_automatic_rollback(self):
        script = (ROOT / "Scripts/Run_Certiaura_Build_0047.ps1").read_text(encoding="ascii")
        self.assertIn('-m unittest discover -s $TestRoot -p "test_build_0047_retatrutide_dashboard.py"', script)
        self.assertNotIn('-m unittest (Join-Path $Repository', script)
        self.assertIn("BUILD 0047 POST-APPLY ROLLBACK: PASS", script)
        self.assertIn("rollback_build_0047_pending_import.py", script)

    def test_pending_import_rollback_restores_clean_repository(self):
        manifest = self.load("Documentation/Build_Records/0047/ASSET_INTENT_MANIFEST.json")
        importer = ROOT / "13_Project_Genesis/Import/build_0047_transactional_import.py"
        rollback = ROOT / "13_Project_Genesis/Import/rollback_build_0047_pending_import.py"
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            package = temp / "candidate.zip"
            with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in manifest["files"]:
                    zf.write(ROOT / item["path"], item["path"])

            repo = temp / "repo"
            repo.mkdir()
            subprocess.run(["git", "-C", str(repo), "init"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Certiaura Test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)

            register = repo / "Documentation/Master_Asset_Register.csv"
            register.parent.mkdir(parents=True)
            fields = [
                "Universal Asset Identifier", "Asset Name", "Knowledge System", "Asset Type", "Status", "Owner",
                "Parent Assets", "Last Review", "Notes", "Repository Path", "Supporting Files", "Version",
                "Completion Percentage", "Child Assets", "Relationship List", "Evidence Links", "Report Links",
                "Marketplace Links", "Next Review", "Change History", "Build Provenance", "Source Builds",
                "Registration Basis", "File SHA256", "Last Updated",
            ]
            with register.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
                writer.writerow({
                    "Universal Asset Identifier": "CERT-SYS-000046",
                    "Asset Name": "Historical fixture",
                    "Knowledge System": "SYS",
                    "Asset Type": "FIXTURE",
                    "Status": "ACTIVE",
                    "Repository Path": "Documentation/Historical_Fixture.md",
                    "Build Provenance": "CERT-BUILD-0046",
                })
            historical = repo / "Documentation/Historical_Fixture.md"
            historical.write_text("# Historical fixture\n", encoding="utf-8", newline="\n")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-m", "baseline"], check=True, capture_output=True)

            apply_report = temp / "apply.json"
            backup_root = temp / "backups"
            result = subprocess.run([
                sys.executable, "-B", str(importer),
                "--repository", str(repo),
                "--package", str(package),
                "--report", str(apply_report),
                "--backup-root", str(backup_root),
                "--apply",
            ], check=False, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            payload = json.loads(apply_report.read_text(encoding="utf-8"))
            self.assertTrue(payload["applied"])

            rollback_report = temp / "rollback.json"
            rollback_result = subprocess.run([
                sys.executable, "-B", str(rollback),
                "--repository", str(repo),
                "--apply-report", str(apply_report),
                "--rollback-report", str(rollback_report),
                "--expected-package-sha256", payload["package_sha256"],
            ], check=False, capture_output=True, text=True)
            self.assertEqual(0, rollback_result.returncode, rollback_result.stdout + rollback_result.stderr)
            rolled_back = json.loads(rollback_report.read_text(encoding="utf-8"))
            self.assertEqual("ROLLED_BACK_CLEAN", rolled_back["status"])
            status = subprocess.run(
                ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
                check=True, capture_output=True, text=True,
            ).stdout
            self.assertEqual("", status)
            with register.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(1, len(rows))
            self.assertEqual("CERT-SYS-000046", rows[0]["Universal Asset Identifier"])


    def test_ps51_regression_reuses_defined_external_backup_root(self):
        script = (
            ROOT / "Scripts/Invoke_Certiaura_Build_0047_Windows_PS51_Regression.ps1"
        ).read_text(encoding="ascii")
        self.assertEqual(2, script.count("-BackupRoot $ExternalBackupRoot"))
        self.assertNotIn("-BackupRoot $BackupRoot", script)
        self.assertIn(
            'if ([string]::IsNullOrWhiteSpace([string]$ExternalBackupRoot))',
            script,
        )

    def test_generator_outputs_export_markdown_and_html(self):
        generator = ROOT / "13_Project_Genesis/Dashboards/generate_retatrutide_longitudinal_dashboard.py"
        journey = ROOT / "05_Monitoring/Examples/Retatrutide/valid_longitudinal_journey.example.json"
        alert = ROOT / "05_Monitoring/Examples/Retatrutide/valid_alert_review.example.json"
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, "-B", str(generator), str(journey), "--alert", str(alert), "--output-dir", tmp], check=True)
            out = Path(tmp)
            export = json.loads((out / "retatrutide_clinician_export.json").read_text(encoding="utf-8"))
            self.assertEqual("DRAFT_FOR_CLINICIAN_REVIEW", export["status"])
            self.assertTrue((out / "retatrutide_clinician_export.md").is_file())
            self.assertTrue((out / "retatrutide_dashboard.html").is_file())


if __name__ == "__main__":
    unittest.main()
