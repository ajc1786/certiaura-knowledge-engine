from __future__ import annotations

import ast
import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "Documentation/Build_Records/0053/ASSET_INTENT_MANIFEST.json"
INVENTORY_PATH = ROOT / "Documentation/Build_Records/0053/PACKAGE_INVENTORY.csv"


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.package_items = list(cls.manifest["files"])
        cls.package_paths = {
            str(item["repository_path"]).replace("\\", "/")
            for item in cls.package_items
        }

    def test_manifest_covers_package_inventory(self) -> None:
        with INVENTORY_PATH.open("r", encoding="utf-8", newline="") as handle:
            inventory_paths = {
                row["repository_path"].replace("\\", "/")
                for row in csv.DictReader(handle)
            }
        self.assertEqual(self.package_paths, inventory_paths)
        self.assertEqual(len(self.package_paths), self.manifest["package_file_count"])
        for rel in sorted(self.package_paths):
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_no_runtime_artifacts_in_owned_scope(self) -> None:
        violations = [
            rel
            for rel in self.package_paths
            if rel.endswith(".pyc") or "/__pycache__/" in f"/{rel}/"
        ]
        self.assertEqual([], violations)

    def test_flat_allowed_roots(self) -> None:
        allowed = {
            "00_Governance",
            "01_Knowledge_Systems",
            "02_Peptides",
            "03_Biology",
            "04_Conditions",
            "05_Monitoring",
            "06_Evidence",
            "07_Goals",
            "08_Product_Passports",
            "09_Cost_Intelligence",
            "10_Marketplace",
            "11_Academy",
            "12_Reports",
            "13_Project_Genesis",
            "Assets",
            "Database",
            "Documentation",
            "Images",
            "Schemas",
            "Scripts",
            "Standards",
            "Templates",
        }
        for rel in sorted(self.package_paths):
            self.assertIn(Path(rel).parts[0], allowed, rel)

    def test_production_write_text_calls_force_lf_newlines(self) -> None:
        violations: list[str] = []
        production_python_paths = [
            ROOT / item["repository_path"]
            for item in self.package_items
            if str(item["repository_path"]).endswith(".py")
            and item.get("classification") != "TEST"
        ]
        for path in production_python_paths:
            rel = path.relative_to(ROOT).as_posix()
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                if not isinstance(func, ast.Attribute) or func.attr != "write_text":
                    continue
                newline = next(
                    (
                        keyword.value
                        for keyword in node.keywords
                        if keyword.arg == "newline"
                    ),
                    None,
                )
                if not (
                    isinstance(newline, ast.Constant)
                    and newline.value == "\n"
                ):
                    violations.append(f"{rel}:{node.lineno}")
        self.assertEqual([], violations)


if __name__ == "__main__":
    unittest.main()
