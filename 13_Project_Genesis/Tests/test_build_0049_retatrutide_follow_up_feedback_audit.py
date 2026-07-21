from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "13_Project_Genesis/Validators"))

from validate_retatrutide_follow_up_feedback_audit import (
    validate_acknowledgement,
    validate_amendment,
    validate_feedback,
    validate_follow_up,
)


class Build0049Tests(unittest.TestCase):
    def load(self, rel: str) -> dict:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))

    def test_valid_acknowledgement_passes(self):
        data = self.load(
            "12_Reports/Retatrutide/Examples/valid_handoff_acknowledgement.example.json"
        )
        self.assertEqual([], validate_acknowledgement(data))

    def test_no_response_acknowledgement_passes(self):
        data = self.load(
            "12_Reports/Retatrutide/Examples/conditional_no_response_acknowledgement.example.json"
        )
        self.assertEqual([], validate_acknowledgement(data))

    def test_valid_follow_up_passes(self):
        data = self.load(
            "12_Reports/Retatrutide/Examples/valid_follow_up_review.example.json"
        )
        self.assertEqual([], validate_follow_up(data))

    def test_locked_urgent_routing_passes(self):
        data = self.load(
            "12_Reports/Retatrutide/Examples/valid_locked_urgent_follow_up.example.json"
        )
        self.assertEqual([], validate_follow_up(data))

    def test_direct_identifier_fails(self):
        data = self.load(
            "12_Reports/Retatrutide/Examples/invalid_direct_identifier_feedback.example.json"
        )
        self.assertTrue(any("direct identifier" in item for item in validate_feedback(data)))

    def test_autonomous_treatment_fails(self):
        data = self.load(
            "12_Reports/Retatrutide/Examples/invalid_autonomous_treatment_feedback.example.json"
        )
        self.assertTrue(
            any("prohibited autonomous" in item for item in validate_feedback(data))
        )

    def test_valid_amendment_passes(self):
        data = self.load(
            "12_Reports/Retatrutide/Examples/valid_export_amendment_audit.example.json"
        )
        self.assertEqual([], validate_amendment(data))

    def test_invalid_amendment_chain_fails(self):
        data = self.load(
            "12_Reports/Retatrutide/Examples/invalid_amendment_chain.example.json"
        )
        self.assertTrue(validate_amendment(data))

    def test_manifest_exact_path_and_provenance(self):
        manifest = self.load(
            "Documentation/Build_Records/0049/ASSET_INTENT_MANIFEST.json"
        )
        paths = [item["path"] for item in manifest["files"]]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(
            all(
                item["build_provenance"] == "CERT-BUILD-0049"
                for item in manifest["files"]
            )
        )
        self.assertTrue(manifest["substring_matching_prohibited"])

    def test_no_build48_path_collision(self):
        manifest = self.load(
            "Documentation/Build_Records/0049/ASSET_INTENT_MANIFEST.json"
        )
        paths = {item["path"] for item in manifest["files"]}
        old = {
            "12_Reports/Standards/RETATRUTIDE_CONTROLLED_CLINICIAN_HANDOFF_BUNDLE_STANDARD.md",
            "Schemas/retatrutide_handoff_receipt.schema.json",
            "13_Project_Genesis/Validators/build_0048_asset_ownership.py",
        }
        self.assertFalse(paths & old)

    def test_generator_creates_manifest_and_summary(self):
        generator = (
            ROOT
            / "13_Project_Genesis/Reports/generate_retatrutide_follow_up_feedback_audit.py"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(generator),
                    str(
                        ROOT
                        / "12_Reports/Retatrutide/Examples/valid_handoff_acknowledgement.example.json"
                    ),
                    str(
                        ROOT
                        / "12_Reports/Retatrutide/Examples/valid_follow_up_review.example.json"
                    ),
                    str(
                        ROOT
                        / "12_Reports/Retatrutide/Examples/valid_clinician_feedback_requires_amendment.example.json"
                    ),
                    str(
                        ROOT
                        / "12_Reports/Retatrutide/Examples/valid_export_amendment_audit.example.json"
                    ),
                    "--output-dir",
                    temp_dir,
                    "--now",
                    "2026-07-21T19:00:00Z",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            output = Path(temp_dir)
            self.assertTrue((output / "bundle_manifest.json").is_file())
            self.assertTrue((output / "audit_summary.md").is_file())

    def test_generator_rejects_treatment_feedback(self):
        generator = (
            ROOT
            / "13_Project_Genesis/Reports/generate_retatrutide_follow_up_feedback_audit.py"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(generator),
                    str(
                        ROOT
                        / "12_Reports/Retatrutide/Examples/valid_handoff_acknowledgement.example.json"
                    ),
                    str(
                        ROOT
                        / "12_Reports/Retatrutide/Examples/valid_follow_up_review.example.json"
                    ),
                    str(
                        ROOT
                        / "12_Reports/Retatrutide/Examples/invalid_autonomous_treatment_feedback.example.json"
                    ),
                    str(
                        ROOT
                        / "12_Reports/Retatrutide/Examples/valid_export_amendment_audit.example.json"
                    ),
                    "--output-dir",
                    temp_dir,
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)

    def test_runner_uses_unittest_discovery_and_rollback(self):
        source = (ROOT / "Scripts/Run_Certiaura_Build_0049.ps1").read_text(
            encoding="ascii"
        )
        self.assertIn(
            '-m unittest discover -s $TestRoot -p "test_build_0049_retatrutide_follow_up_feedback_audit.py"',
            source,
        )
        self.assertIn("BUILD 0049 POST-APPLY ROLLBACK: PASS", source)
        self.assertNotIn("$Candidates.FullName", source)

    def test_ps51_collection_and_alias_controls(self):
        for rel in [
            "Scripts/Run_Certiaura_Build_0049.ps1",
            "Scripts/Invoke_Certiaura_Build_0049_Windows_PS51_Regression.ps1",
        ]:
            source = (ROOT / rel).read_text(encoding="ascii")
            self.assertNotIn(
                "$MatchesArray = @($Matches)",
                [line.strip() for line in source.splitlines()],
            )
        regression = (
            ROOT / "Scripts/Invoke_Certiaura_Build_0049_Windows_PS51_Regression.ps1"
        ).read_text(encoding="ascii")
        self.assertNotIn("-BackupRoot $BackupRoot", regression)
        self.assertEqual(2, regression.count("-BackupRoot $ExternalBackupRoot"))

    def test_accumulated_lessons_gates_present(self):
        text = (
            ROOT / "Documentation/Build_Records/0049/LESSONS_LEARNED_REVIEW.md"
        ).read_text(encoding="utf-8")
        for phrase in [
            "Accumulated prior-build lessons reviewed",
            "Current-build lessons recorded",
            "Lessons converted to regression controls",
            "Continuity checkpoint updated",
        ]:
            self.assertIn(phrase, text)

    def test_ps51_manifest_scope_assertion_tolerates_pep8_multiline_format(self):
        regression = (
            ROOT
            / "Scripts"
            / "Invoke_Certiaura_Build_0049_Windows_PS51_Regression.ps1"
        ).read_text(encoding="ascii")
        self.assertIn("$ManifestScopePattern", regression)
        self.assertIn("$OwnedPathsPattern", regression)
        self.assertIn(
            "[regex]::IsMatch($BuildTestText, $ManifestScopePattern)",
            regression,
        )
        self.assertIn(
            "[regex]::IsMatch($BuildTestText, $OwnedPathsPattern)",
            regression,
        )
        self.assertNotIn(
            'manifest=self.load("Documentation/Build_Records/0049/ASSET_INTENT_MANIFEST.json")',
            regression,
        )
        self.assertIn(
            '& $Python -B -m unittest discover `',
            regression,
        )
        self.assertIn(
            '-p "test_build_0049_retatrutide_follow_up_feedback_audit.py"',
            regression,
        )

    def test_dry_run_blocks_nonidentical_collision(self):
        manifest = self.load(
            "Documentation/Build_Records/0049/ASSET_INTENT_MANIFEST.json"
        )
        importer = (
            ROOT
            / "13_Project_Genesis/Import/build_0049_transactional_import.py"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            package = temp / "package.zip"
            with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
                for item in manifest["files"]:
                    archive.write(ROOT / item["path"], item["path"])

            repository = temp / "repository"
            repository.mkdir()
            subprocess.run(
                ["git", "-C", str(repository), "init"],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(repository), "config", "user.name", "Test"],
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "config",
                    "user.email",
                    "test@example.invalid",
                ],
                check=True,
            )
            register = repository / "Documentation/Master_Asset_Register.csv"
            register.parent.mkdir(parents=True)
            fields = [
                "Universal Asset Identifier",
                "Asset Name",
                "Knowledge System",
                "Asset Type",
                "Status",
                "Owner",
                "Parent Assets",
                "Last Review",
                "Notes",
                "Repository Path",
                "Supporting Files",
                "Version",
                "Completion Percentage",
                "Child Assets",
                "Relationship List",
                "Evidence Links",
                "Report Links",
                "Marketplace Links",
                "Next Review",
                "Change History",
                "Build Provenance",
                "Source Builds",
                "Registration Basis",
                "File SHA256",
                "Last Updated",
            ]
            with register.open("w", encoding="utf-8", newline="") as handle:
                csv.DictWriter(
                    handle,
                    fieldnames=fields,
                    lineterminator="\n",
                ).writeheader()

            collision = repository / "Schemas/retatrutide_handoff_acknowledgement.schema.json"
            collision.parent.mkdir(parents=True)
            collision.write_text("{}\n", encoding="utf-8", newline="\n")
            subprocess.run(
                ["git", "-C", str(repository), "add", "-A"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repository), "commit", "-m", "baseline"],
                check=True,
                capture_output=True,
            )

            report = temp / "report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(importer),
                    "--repository",
                    str(repository),
                    "--package",
                    str(package),
                    "--report",
                    str(report),
                ],
                capture_output=True,
                text=True,
            )
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("FAILED_CLOSED", payload["transaction_status"])
            self.assertTrue(payload["conflicts"])

    def test_package_scripts_ascii_and_lf(self):
        manifest = self.load(
            "Documentation/Build_Records/0049/ASSET_INTENT_MANIFEST.json"
        )
        owned_paths = [ROOT / item["path"] for item in manifest["files"]]
        scripts = [path for path in owned_paths if path.suffix.lower() in {".ps1", ".cmd"}]
        self.assertTrue(scripts)
        for path in scripts:
            data = path.read_bytes()
            data.decode("ascii")
            self.assertNotIn(b"\r", data)

    def test_hygiene_scope_uses_exact_manifest_paths(self):
        source = Path(__file__).read_text(encoding="utf-8")
        self.assertIn(
            'manifest = self.load(\n            "Documentation/Build_Records/0049/ASSET_INTENT_MANIFEST.json"',
            source,
        )
        self.assertIn(
            'owned_paths = [ROOT / item["path"] for item in manifest["files"]]',
            source,
        )
        broad_scan = 'for path in ROOT.' + 'rglob("*")'
        self.assertNotIn(broad_scan, source)


if __name__ == "__main__":
    unittest.main()
