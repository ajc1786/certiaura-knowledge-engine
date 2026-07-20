from __future__ import annotations
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "13_Project_Genesis/Validators/validate_retatrutide_evidence_corpus.py"
spec = importlib.util.spec_from_file_location("ret_validator", VALIDATOR_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

class Build0041EvidenceTests(unittest.TestCase):
    def test_valid_corpus(self):
        self.assertEqual([], module.validate(ROOT))

    def test_invalid_primary_identifier_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "repo"
            shutil.copytree(ROOT, target)
            src = target / "13_Project_Genesis/Tests/Fixtures/Build_0041/invalid_missing_primary_identifier.example.json"
            dst = target / "06_Evidence/Retatrutide/Corpus/RET-EVD-0001.json"
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            errors = module.validate(target)
            self.assertTrue(any("incomplete primary_identifier" in e for e in errors))

    def test_sponsor_topline_is_conditional(self):
        data = json.loads((ROOT / "06_Evidence/Retatrutide/Corpus/RET-EVD-0008.json").read_text(encoding="utf-8"))
        self.assertEqual("not_peer_reviewed", data["peer_review_status"])
        self.assertIn("CONDITIONAL", data["review_status"])

    def test_registry_is_not_results(self):
        data = json.loads((ROOT / "06_Evidence/Retatrutide/Corpus/RET-EVD-0010.json").read_text(encoding="utf-8"))
        self.assertEqual("clinical_trial_registry_record", data["source_type"])
        self.assertTrue(any("final results" in x.lower() for x in data["limitations"]))

    def test_windows_powershell_launchers_are_ascii_safe(self):
        scripts = sorted(list(ROOT.rglob("*.ps1")) + list(ROOT.rglob("*.cmd")))
        self.assertTrue(scripts)
        for script in scripts:
            try:
                script.read_bytes().decode("ascii")
            except UnicodeDecodeError as exc:
                self.fail(f"Windows PowerShell 5.1 executable script is not ASCII-safe: {script.relative_to(ROOT)}: {exc}")

    def test_one_drive_restart_uses_a_full_path_resolver(self):
        launcher = (ROOT / "Scripts/Run_Certiaura_Build_0041.ps1").read_text(encoding="ascii")
        self.assertIn("function Resolve-OneDriveExecutable", launcher)
        self.assertIn("foreach ($Candidate in $CandidatePaths)", launcher)
        self.assertNotIn("Start-Process -FilePath $Candidates[0]", launcher)

    def test_import_wrapper_receives_explicit_package_path(self):
        wrapper = (ROOT / "Scripts/Invoke_Certiaura_Build_0041_Import.ps1").read_text(encoding="ascii")
        self.assertIn("[string]$Package", wrapper)
        self.assertIn("Get-FileHash -LiteralPath $Package", wrapper)
        self.assertNotIn("Dropbox\\PC\\Downloads", wrapper)

if __name__ == "__main__": unittest.main()
