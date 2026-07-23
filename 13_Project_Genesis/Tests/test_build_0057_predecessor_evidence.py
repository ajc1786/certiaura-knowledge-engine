from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREDECESSOR_ZIP = Path("/mnt/data/Certiaura_Build_0056_Tesamorelin_Controlled_Pilot_RC1.zip")
MODULE_PATH = ROOT / "13_Project_Genesis/Release/derive_build_0056_predecessor_evidence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("derive0056", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


class Tests(unittest.TestCase):
    def test_git_source_and_approved_overlap(self):
        if not PREDECESSOR_ZIP.exists():
            self.skipTest("predecessor ZIP unavailable outside build environment")
        module = load_module()
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            git(repo, "init", "-b", "main")
            git(repo, "config", "user.email", "test@example.invalid")
            git(repo, "config", "user.name", "Test")
            with zipfile.ZipFile(PREDECESSOR_ZIP) as zf:
                zf.extractall(repo)
            git(repo, "add", "--all")
            git(repo, "commit", "-m", "predecessor")
            commit = git(repo, "rev-parse", "HEAD")
            report = Path(temp) / "report.json"
            result = module.derive(repo, ROOT / "Documentation/Build_Records/0057/ASSET_INTENT_MANIFEST.json", report, expected_commit=commit, expected_count=91)
            self.assertEqual("PREDECESSOR_CANONICAL_SOURCE_VERIFIED", result["result"])
            self.assertEqual([], result["approved_intersection"])
            self.assertEqual([], result["prohibited_intersection"])

    def test_unapproved_overlap_is_rejected(self):
        if not PREDECESSOR_ZIP.exists():
            self.skipTest("predecessor ZIP unavailable outside build environment")
        module = load_module()
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            git(repo, "init", "-b", "main")
            git(repo, "config", "user.email", "test@example.invalid")
            git(repo, "config", "user.name", "Test")
            with zipfile.ZipFile(PREDECESSOR_ZIP) as zf:
                zf.extractall(repo)
            git(repo, "add", "--all")
            git(repo, "commit", "-m", "predecessor")
            commit = git(repo, "rev-parse", "HEAD")
            manifest = json.loads((ROOT / "Documentation/Build_Records/0057/ASSET_INTENT_MANIFEST.json").read_text(encoding="utf-8"))
            manifest["files"].append({"repository_path": "Standards/TESAMORELIN_BIOLOGICAL_BOUNDARY_MATRIX.json", "classification": "TEST_PROBE", "intended_action": "CREATE", "package_member": False})
            bad = Path(temp) / "bad.json"
            bad.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                module.derive(repo, bad, expected_commit=commit, expected_count=91)


if __name__ == "__main__":
    unittest.main()
