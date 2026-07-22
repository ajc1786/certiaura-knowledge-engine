from __future__ import annotations

import ast
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "Documentation/Build_Records/0052/ASSET_INTENT_MANIFEST.json"
UPDATER_PATH = ROOT / "Scripts/update_certiaura_accumulated_lessons.py"
IMPORTER_PATH = ROOT / "13_Project_Genesis/Import/run_build_0052_import.py"
REGRESSION_PS_PATH = ROOT / "Scripts/Invoke_Certiaura_Build_0052_Windows_PS51_Regression.ps1"
IMPORT_PS_PATH = ROOT / "Scripts/Invoke_Certiaura_Build_0052_Import.ps1"


def load_updater_module():
    specification = importlib.util.spec_from_file_location(
        "certiaura_accumulated_lessons_updater",
        UPDATER_PATH,
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("Unable to load accumulated lessons updater")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.paths = [item["repository_path"] for item in self.manifest["files"]]
        self.updater = load_updater_module()

    def test_no_candidate_authored_predecessor_fixture(self):
        self.assertFalse(
            any(
                "Predecessor_Repository" in path
                or "predecessor_build_0051_identity" in path
                for path in self.paths
            )
        )

    def test_exact_paths_unique(self):
        self.assertEqual(len(self.paths), len(set(self.paths)))

    def test_current_provenance(self):
        self.assertTrue(
            all(
                item["build_provenance"] == "CERT-BUILD-0052"
                for item in self.manifest["files"]
            )
        )

    def test_approved_replacements_are_explicit(self):
        replacements = [
            item
            for item in self.manifest["files"]
            if item.get("approved_replacement")
        ]
        self.assertTrue(replacements)
        self.assertTrue(
            all(item.get("predecessor_build") == "0051" for item in replacements)
        )

    def test_updater_renderer_has_no_markdown_hard_break_spaces(self):
        updater = UPDATER_PATH.read_text(encoding="utf-8")
        self.assertFalse(
            any(line.endswith((" ", "\t")) for line in updater.splitlines())
        )
        ast.parse(updater)

    def test_historical_missing_control_family_is_recorded_migration(self):
        matrix = {
            "controls": [
                {
                    "lesson_id": "CERT-LESSON-LEGACY-0041",
                    "origin_builds": ["0041"],
                    "defect": "A valid Build 0041 historical lesson lacks a control family.",
                    "root_cause": "The field predated the cumulative schema.",
                    "preventive_control": "Retain the historical control.",
                    "regression_test": "Validate migration provenance.",
                    "release_gate": "HISTORICAL_LESSONS_VALIDATED",
                    "status": "LOCKED_ACTIVE",
                }
            ]
        }
        records, migrations = self.updater.normalise_matrix(
            matrix,
            "0041",
            Path("Documentation/Build_Records/0041/LESSONS_LEARNED_CONTROL_MATRIX.json"),
            "0052",
        )
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0]["control_family"])
        self.assertEqual(len(migrations), 1)
        migrated_fields = {
            entry["field"]
            for entry in migrations[0]["migrations"]
        }
        self.assertIn("control_family", migrated_fields)
        self.assertEqual(
            records[0]["historical_schema_migration"]["source"],
            "Documentation/Build_Records/0041/LESSONS_LEARNED_CONTROL_MATRIX.json",
        )

    def test_current_missing_control_family_is_blocked(self):
        matrix = {
            "lessons": [
                {
                    "lesson_id": "CERT-LESSON-CURRENT-INVALID",
                    "origin_builds": ["0052"],
                    "defect_or_risk": "Current schema omission.",
                    "root_cause": "Test fixture.",
                    "preventive_control": "Test fixture.",
                    "regression_control": "Test fixture.",
                    "release_gate": "TEST_GATE",
                    "status": "LOCKED_ACTIVE",
                }
            ]
        }
        with self.assertRaisesRegex(
            RuntimeError,
            "CURRENT_LESSON_REQUIRED_FIELD_MISSING.*control_family",
        ):
            self.updater.normalise_matrix(
                matrix,
                "0052",
                Path("Documentation/Build_Records/0052/LESSONS_LEARNED_CONTROL_MATRIX.json"),
                "0052",
            )

    def test_empty_historical_record_is_blocked(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "LEGACY_LESSON_SUBSTANCE_MISSING",
        ):
            self.updater.normalise_matrix(
                {"entries": [{}]},
                "0041",
                Path("Documentation/Build_Records/0041/LESSONS_LEARNED_CONTROL_MATRIX.json"),
                "0052",
            )

    def test_historical_backfill_identifier_is_deterministic(self):
        matrix = {
            "entries": [
                {
                    "issue": "Legacy issue with no stable identifier.",
                    "cause": "Legacy schema.",
                    "corrective_action": "Retain and migrate.",
                    "test": "Repeatable migration test.",
                    "gate": "LEGACY_GATE",
                    "state": "LOCKED_ACTIVE",
                }
            ]
        }
        source = Path(
            "Documentation/Build_Records/0041/LESSONS_LEARNED_CONTROL_MATRIX.json"
        )
        first, _ = self.updater.normalise_matrix(matrix, "0041", source, "0052")
        second, _ = self.updater.normalise_matrix(matrix, "0041", source, "0052")
        self.assertEqual(first[0]["lesson_id"], second[0]["lesson_id"])
        self.assertEqual(
            first[0]["identifier_basis"],
            "DETERMINISTIC_HISTORICAL_BACKFILL",
        )

    def test_premerged_same_build_repeat_is_idempotent(self):
        existing = [
            {
                "lesson_id": "CERT-LESSON-IDEMPOTENT-TEST",
                "origin_builds": ["0052"],
                "control_family": "Test control",
                "defect_or_risk": "Test defect",
                "root_cause": "Same root cause",
                "preventive_control": "Existing preventive control",
                "regression_control": "Existing regression control",
                "release_gate": "TEST_GATE",
                "status": "LOCKED_ACTIVE",
                "repeat_defect": True,
            }
        ]
        incoming = json.loads(json.dumps(existing))
        merged, changes = self.updater.merge(existing, incoming)
        self.assertEqual(len(merged), 1)
        self.assertEqual(changes[0]["action"], "UPDATED")
        self.assertEqual(merged[0]["origin_builds"], ["0052"])

    def test_new_origin_repeat_without_stronger_control_is_blocked(self):
        existing = [
            {
                "lesson_id": "CERT-LESSON-REPEAT-TEST",
                "origin_builds": ["0051"],
                "control_family": "Test control",
                "defect_or_risk": "Test defect",
                "root_cause": "Same root cause",
                "preventive_control": "Existing preventive control",
                "regression_control": "Existing regression control",
                "release_gate": "TEST_GATE",
                "status": "LOCKED_ACTIVE",
                "repeat_defect": True,
            }
        ]
        incoming = json.loads(json.dumps(existing))
        incoming[0]["origin_builds"] = ["0052"]
        with self.assertRaisesRegex(
            RuntimeError,
            "REPEATED_DEFECT_CONTROL_NOT_STRENGTHENED",
        ):
            self.updater.merge(existing, incoming)


    def test_missing_historical_matrix_uses_exact_hash_bound_ledger_evidence(self):
        lessons = [
            {
                "lesson_id": "CERT-LESSON-LEGACY-COVERAGE-TEST",
                "origin_builds": ["0040"],
                "control_family": "Historical coverage test",
                "defect_or_risk": "Legacy matrix absent.",
                "root_cause": "Matrix predates the current retained build-record set.",
                "preventive_control": "Bind coverage to the authoritative ledger.",
                "regression_control": "Validate exact lesson identifiers and digest.",
                "release_gate": "HISTORICAL_LEDGER_COVERAGE_VALIDATED",
                "status": "LOCKED_ACTIVE",
            }
        ]
        lesson_ids = ["CERT-LESSON-LEGACY-COVERAGE-TEST"]
        master = {
            "lessons": lessons,
            "coverage": {
                "ledger_only_historical_evidence": {
                    "0040": {
                        "matrix_status": "LEGACY_MATRIX_NOT_PRESENT_CANONICALLY",
                        "evidence_mode": "AUTHORITATIVE_CUMULATIVE_LEDGER_EXACT_LESSON_SET",
                        "lesson_ids": lesson_ids,
                        "lesson_id_set_sha256": self.updater.lesson_id_set_sha256(lesson_ids),
                        "provenance": "CERT-GOV-LEARN-001",
                    }
                }
            },
        }
        records = self.updater.validate_ledger_only_historical_evidence(master, ["0040"])
        self.assertEqual(records[0]["build_number"], "0040")
        self.assertEqual(records[0]["lesson_count"], 1)

    def test_missing_historical_matrix_without_declared_evidence_is_blocked(self):
        master = {"lessons": [], "coverage": {"ledger_only_historical_evidence": {}}}
        with self.assertRaisesRegex(RuntimeError, "HISTORICAL_LEDGER_ONLY_BUILD_UNDECLARED"):
            self.updater.validate_ledger_only_historical_evidence(master, ["0040"])

    def test_ledger_only_historical_set_drift_is_blocked(self):
        lesson = {
            "lesson_id": "CERT-LESSON-LEGACY-COVERAGE-TEST",
            "origin_builds": ["0040"],
            "control_family": "Historical coverage test",
            "defect_or_risk": "Legacy matrix absent.",
            "root_cause": "Legacy retention.",
            "preventive_control": "Bind coverage.",
            "regression_control": "Validate exact set.",
            "release_gate": "HISTORICAL_LEDGER_COVERAGE_VALIDATED",
            "status": "LOCKED_ACTIVE",
        }
        master = {
            "lessons": [lesson],
            "coverage": {
                "ledger_only_historical_evidence": {
                    "0040": {
                        "matrix_status": "LEGACY_MATRIX_NOT_PRESENT_CANONICALLY",
                        "evidence_mode": "AUTHORITATIVE_CUMULATIVE_LEDGER_EXACT_LESSON_SET",
                        "lesson_ids": ["CERT-LESSON-WRONG"],
                        "lesson_id_set_sha256": self.updater.lesson_id_set_sha256(["CERT-LESSON-WRONG"]),
                    }
                }
            },
        }
        with self.assertRaisesRegex(RuntimeError, "HISTORICAL_LEDGER_ONLY_SET_MISMATCH"):
            self.updater.validate_ledger_only_historical_evidence(master, ["0040"])

    def test_transactional_importer_emits_rollback_reason(self):
        importer = IMPORTER_PATH.read_text(encoding="utf-8")
        self.assertIn("BUILD_0052_TRANSACTION_ROLLED_BACK", importer)
        self.assertIn("print(failure_message, file=sys.stderr)", importer)
        self.assertIn('result["rollback_reason"]', importer)

    def test_powershell_output_assertions_normalise_collection_to_scalar(self):
        for path in (REGRESSION_PS_PATH, IMPORT_PS_PATH):
            source = path.read_text(encoding="ascii")
            self.assertIn("function Convert-NativeOutputToText", source)
            self.assertIn("function Assert-NativeOutputContains", source)
            self.assertNotRegex(source, r"\.Output\s+-notmatch")
            self.assertIn("-join [Environment]::NewLine", source)

    def test_multiline_native_output_positive_and_negative_controls_exist(self):
        source = REGRESSION_PS_PATH.read_text(encoding="ascii")
        self.assertIn("MULTILINE_NATIVE_OUTPUT_MATCH_VALIDATED", source)
        self.assertIn("unrelated output before token", source)
        self.assertIn("unrelated output after token", source)
        self.assertIn("Multiline native output negative control failed", source)


if __name__ == "__main__":
    unittest.main()
