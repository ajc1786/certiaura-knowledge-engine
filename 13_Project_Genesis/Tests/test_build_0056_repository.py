from __future__ import annotations

import ast
import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "Documentation/Build_Records/0056/ASSET_INTENT_MANIFEST.json"
INVENTORY_PATH = ROOT / "Documentation/Build_Records/0056/PACKAGE_INVENTORY.csv"


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.items = cls.manifest["files"]
        cls.paths = {item["repository_path"].replace("\\", "/") for item in cls.items}

    def test_inventory(self):
        with INVENTORY_PATH.open(encoding="utf-8", newline="") as handle:
            inventory = {row["repository_path"] for row in csv.DictReader(handle)}
        self.assertEqual(self.paths, inventory)
        self.assertEqual(len(self.paths), self.manifest["package_file_count"])

    def test_allowed_roots(self):
        allowed = {"00_Governance", "01_Knowledge_Systems", "02_Peptides", "03_Biology", "04_Conditions", "05_Monitoring", "06_Evidence", "07_Goals", "08_Product_Passports", "09_Cost_Intelligence", "10_Marketplace", "11_Academy", "12_Reports", "13_Project_Genesis", "Assets", "Database", "Documentation", "Images", "Schemas", "Scripts", "Standards", "Templates"}
        for rel in self.paths:
            self.assertIn(Path(rel).parts[0], allowed)

    def test_no_runtime_artifacts(self):
        self.assertFalse([path for path in self.paths if path.endswith(".pyc") or "/__pycache__/" in "/" + path + "/"])

    def test_lf_writers(self):
        bad = []
        for item in self.items:
            rel = item["repository_path"]
            if rel.endswith(".py") and item.get("classification") != "TEST":
                tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "write_text":
                        keyword = next((value.value for value in node.keywords if value.arg == "newline"), None)
                        if not (isinstance(keyword, ast.Constant) and keyword.value == "\n"):
                            bad.append(f"{rel}:{node.lineno}")
        self.assertEqual([], bad)

    def test_staged_byte_validator_is_approved_update_and_manifest_driven(self):
        item = next(entry for entry in self.items if entry["repository_path"] == "13_Project_Genesis/Validators/verify_staged_byte_equality.py")
        self.assertEqual("UPDATE", item["intended_action"])
        self.assertIs(True, item.get("approved_predecessor_overlap"))
        self.assertEqual("NO_CHANGE", item.get("master_asset_register_action"))
        text = (ROOT / item["repository_path"]).read_text(encoding="utf-8")
        self.assertIn('manifest.get("build_number"', text)
        self.assertNotIn('"build_number": "0053"', text)

    def test_staging_and_strictmode_gates(self):
        for rel in ["Scripts/Invoke_Certiaura_Build_0056_Windows_PS51_Regression.ps1", "Scripts/Run_Certiaura_Build_0056.ps1"]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("BUILD_0056_STAGED_CHANGESET_VALIDATED", text)
            self.assertIn('PSObject.Properties["approved_predecessor_overlap"]', text)
            self.assertIn("BUILD_0056_OPTIONAL_PROPERTY_STRICTMODE_VALIDATED", text)
            self.assertIn("Compare-Object", text)
            self.assertIn("diff HEAD --name-only", text)

    def test_actions_run_id_closure_requirement(self):
        data = json.loads((ROOT / "Documentation/Build_Records/0056/GITHUB_ACTIONS_CLOSURE_EVIDENCE_REQUIREMENTS.json").read_text(encoding="utf-8"))
        self.assertTrue(data["mandatory"])
        self.assertIn("run_id", data["fields"])
        self.assertTrue(data["must_match_canonical_commit"])

    def test_target_specific_boundaries(self):
        all_text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in self.paths if path.startswith("Standards/") or path.startswith("Templates/"))
        self.assertIn("clinical equivalence", all_text.lower())
        self.assertIn("autonomous", all_text.lower())
        example_paths = [path for path in self.paths if path.startswith("05_Monitoring/Examples/")]
        self.assertTrue(example_paths)
        self.assertTrue(all("/Tesamorelin/" in path for path in example_paths))

    def test_close_script_requires_exact_actions_run(self):
        text = (ROOT / "Scripts/Close_Certiaura_Build_0056.ps1").read_text(encoding="utf-8")
        self.assertIn('$_ .head_sha'.replace(' ', ''), text.replace(' ', ''))
        self.assertIn('$_.head_branch -eq "main"', text)
        self.assertIn('$_.event -eq "push"', text)
        self.assertIn('$_.name -eq $WorkflowName', text)
        self.assertIn('run_attempt', text)
        self.assertIn('BUILD_0056_GITHUB_ACTIONS_GREEN', text)

    def test_current_build_examples_are_manifest_scoped(self):
        text = (ROOT / "13_Project_Genesis/Tests/test_build_0056_tesamorelin_pilot.py").read_text(encoding="utf-8")
        self.assertIn("ASSET_INTENT_MANIFEST.json", text)
        self.assertNotIn("glob(\"valid_*.example.json\")", text)


if __name__ == "__main__":
    unittest.main()
