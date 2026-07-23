from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "13_Project_Genesis/Release/audit_historical_github_actions_evidence.py"
SPEC = importlib.util.spec_from_file_location("historical_actions", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
import sys
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Tests(unittest.TestCase):
    def test_subject_parser_prefers_exact_add(self):
        self.assertEqual((54, "0054", True), MODULE.parse_build_subject("Add Certiaura Build 0054 title"))
        self.assertEqual((35, "0035E", False), MODULE.parse_build_subject("Close Certiaura Build 0035E"))
        self.assertIsNone(MODULE.parse_build_subject("Unrelated commit"))

    def test_run_selection_prefers_successful_repository_validation(self):
        runs = [
            {"id": 1, "event": "push", "head_branch": "main", "name": "Other", "status": "completed", "conclusion": "success", "created_at": "2026-01-01", "run_attempt": 1},
            {"id": 2, "event": "push", "head_branch": "main", "name": "Certiaura Repository Validation", "status": "completed", "conclusion": "success", "created_at": "2026-01-02", "run_attempt": 1},
        ]
        chosen, ids = MODULE.select_run(runs)
        self.assertEqual(2, chosen["id"])
        self.assertEqual(["2"], ids)

    def test_audit_writes_complete_accounting_bundle(self):
        commits = [("a" * 40, "Add Certiaura Build 0001 first"), ("b" * 40, "Add Certiaura Build 0002 second")]
        runs = [
            {"id": 101, "head_sha": "a" * 40, "event": "push", "head_branch": "main", "name": "Certiaura Repository Validation", "status": "completed", "conclusion": "success", "created_at": "2026-01-01", "updated_at": "2026-01-01", "run_attempt": 1, "html_url": "https://example/101"},
            {"id": 102, "head_sha": "b" * 40, "event": "push", "head_branch": "main", "name": "Certiaura Repository Validation", "status": "completed", "conclusion": "success", "created_at": "2026-01-02", "updated_at": "2026-01-02", "run_attempt": 1, "html_url": "https://example/102"},
        ]
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            (repo / ".git").mkdir(parents=True)
            out = Path(td) / "out"
            with mock.patch.object(MODULE, "first_parent_commits", return_value=commits), mock.patch.object(MODULE, "fetch_all_runs", return_value=runs), mock.patch.object(MODULE, "workflow_present", return_value=True), mock.patch.object(MODULE, "capture_status", return_value=("BACKFILLED_BY_BUILD_0055", None)), mock.patch.object(MODULE, "run_git", return_value="b" * 40 + "\n"):
                summary = MODULE.audit(repo, "owner", "repo", out, 1, 2, None)
            self.assertEqual("HISTORICAL_ACTIONS_AUDIT_COMPLETE", summary["result"])
            self.assertEqual(2, summary["verified_run_id_count"])
            evidence = json.loads((out / "HISTORICAL_GITHUB_ACTIONS_EVIDENCE.json").read_text(encoding="utf-8"))
            self.assertEqual(["0001", "0002"], [item["build_number"] for item in evidence["records"]])
            self.assertTrue((out / "HISTORICAL_GITHUB_ACTIONS_EVIDENCE_REGISTER.csv").is_file())

    def test_missing_build_commit_is_accounted_exception(self):
        record = MODULE.make_record(1, [], None, "NO_MATCHING_BUILD_COMMIT", {}, Path("."), [], None)
        self.assertTrue(record["accounted"])
        self.assertEqual("BUILD_COMMIT_NOT_FOUND", record["classification"])
        self.assertEqual("RESOLVED_EXCEPTION", record["capture_status"])


if __name__ == "__main__":
    unittest.main()
