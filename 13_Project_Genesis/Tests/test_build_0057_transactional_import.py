from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path("/mnt/data/Certiaura_Build_0057_Tesamorelin_Workflow_Simulation_RC1.zip")
PREDECESSOR = Path("/mnt/data/Certiaura_Build_0056_Tesamorelin_Controlled_Pilot_RC1.zip")
IMPORTER_PATH = ROOT / "13_Project_Genesis/Import/run_build_0057_import.py"
VALIDATOR_PATH = ROOT / "13_Project_Genesis/Validators/validate_build_0057_repository.py"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def seed_repository(repo):
    with zipfile.ZipFile(PREDECESSOR) as zf:
        zf.extractall(repo)
    governance = repo / "00_Governance"
    governance.mkdir(parents=True, exist_ok=True)
    (governance / "CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md").write_text("# continuity\n", encoding="utf-8", newline="\n")
    (governance / "CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md").write_text("# lessons\n", encoding="utf-8", newline="\n")
    (governance / "CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json").write_text("{}\n", encoding="utf-8", newline="\n")
    register = repo / "Documentation/Master_Asset_Register.csv"
    register.parent.mkdir(parents=True, exist_ok=True)
    headers = ["Universal Asset Identifier", "Asset Name", "Knowledge System", "Asset Type", "Status", "Owner", "Repository Path", "Version", "Build Provenance"]
    rows = []
    with zipfile.ZipFile(PREDECESSOR) as zf:
        manifest = json.loads(zf.read("Documentation/Build_Records/0056/ASSET_INTENT_MANIFEST.json"))
        index = 1
        for item in manifest.get("files", []):
            if item.get("classification") == "FORMAL_ASSET":
                rows.append({"Universal Asset Identifier": f"CERT-{item.get('knowledge_system','SYS')}-{index:06d}", "Asset Name": item.get("asset_title", Path(item["repository_path"]).stem), "Knowledge System": item.get("knowledge_system", "SYS"), "Asset Type": item.get("asset_type", "Controlled Standard"), "Status": "ACTIVE", "Owner": "Certiaura Governance", "Repository Path": item["repository_path"], "Version": "1.0.0", "Build Provenance": "Build 0056"})
                index += 1
    with register.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Test")
    git(repo, "add", "--all")
    git(repo, "commit", "-m", "predecessor")
    return git(repo, "rev-parse", "HEAD")


class Tests(unittest.TestCase):
    def setUp(self):
        if not PACKAGE.exists() or not PREDECESSOR.exists():
            self.skipTest("release packages unavailable outside build environment")

    def test_rollback_clean_reapply_and_validator(self):
        importer = load_module(IMPORTER_PATH, "import0057")
        validator = load_module(VALIDATOR_PATH, "validate0057")
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            commit = seed_repository(repo)
            backup = Path(temp) / "backup"
            dry = importer.run_import(PACKAGE, repo, backup, Path(temp) / "dry.json", False, expected_predecessor_commit=commit)
            self.assertEqual("DRY_RUN_VALIDATED", dry["result"])
            forced = importer.run_import(PACKAGE, repo, backup, Path(temp) / "forced.json", True, True, expected_predecessor_commit=commit)
            self.assertEqual("ROLLBACK_STATE_EXACT", forced["result"])
            self.assertEqual("", git(repo, "status", "--porcelain", "--untracked-files=all"))
            applied = importer.run_import(PACKAGE, repo, backup, Path(temp) / "apply.json", True, expected_predecessor_commit=commit)
            self.assertEqual("CLEAN_REAPPLY_VALIDATED", applied["result"])
            result = validator.validate(repo, Path(temp) / "validation.json", expected_predecessor_commit=commit)
            self.assertTrue(result["valid"], result)
            rollback = importer.rollback_from_backup(repo, applied["backup_path"], Path(temp) / "rollback.json")
            self.assertEqual("ROLLBACK_STATE_EXACT", rollback["result"])
            self.assertEqual("", git(repo, "status", "--porcelain", "--untracked-files=all"))

    def test_generated_reports_are_lf(self):
        importer = load_module(IMPORTER_PATH, "import0057_lf")
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            commit = seed_repository(repo)
            applied = importer.run_import(PACKAGE, repo, Path(temp) / "backup", Path(temp) / "apply.json", True, expected_predecessor_commit=commit)
            manifest = json.loads((repo / "Documentation/Build_Records/0057/ASSET_INTENT_MANIFEST.json").read_text(encoding="utf-8"))
            for item in manifest.get("generated_files", []):
                path = repo / item["repository_path"]
                if path.suffix.lower() in {".json", ".md", ".csv", ".txt"}:
                    self.assertNotIn(b"\r\n", path.read_bytes(), item["repository_path"])
            importer.rollback_from_backup(repo, applied["backup_path"], Path(temp) / "rollback.json")


if __name__ == "__main__":
    unittest.main()
