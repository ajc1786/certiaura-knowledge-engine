from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "Import" / "transactional_build_import.py"
SPEC = importlib.util.spec_from_file_location("build_neutral_importer", MODULE)
IMPORTER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(IMPORTER)


class BuildNeutralImporterCompatibilityTests(unittest.TestCase):
    def make_repo(self, root: Path) -> Path:
        repo = root / "repo"
        (repo / "Documentation").mkdir(parents=True)
        fields = [
            "Universal Asset Identifier", "Asset Name", "Knowledge System", "Asset Type",
            "Status", "Owner", "Repository Path", "Version", "Completion Percentage",
            "Last Review", "Next Review", "Build Provenance", "Source Builds", "Registration Basis",
        ]
        rows = [{
            "Universal Asset Identifier": "CERT-SYS-000082",
            "Asset Name": "Existing Importer",
            "Knowledge System": "SYS",
            "Repository Path": "13_Project_Genesis/Import/transactional_build_import.py",
        }]
        register = repo / "Documentation/Master_Asset_Register.csv"
        with register.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        existing = repo / rows[0]["Repository Path"]
        existing.parent.mkdir(parents=True)
        existing.write_text("old importer\n", encoding="utf-8")
        return repo

    def make_zip(self, root: Path, build: str, title: str, version: str) -> Path:
        package = root / f"build_{build}.zip"
        record = f"Documentation/Build_Records/{build}"
        files = {
            "13_Project_Genesis/Import/transactional_build_import.py": b"new importer\n",
            "Standards/NEW_STANDARD.md": b"# New standard\n",
        }
        all_paths = sorted(set(files) | {
            f"{record}/BUILD_MANIFEST.json",
            f"{record}/ASSET_INTENT_MANIFEST.json",
            f"{record}/ROUTING_MANIFEST.json",
        })
        manifest = {
            "build_number": build,
            "build_title": title,
            "package_version": version,
            "package_file_count": len(all_paths),
            "formal_assets_created": 1,
        }
        intent = {
            "build_number": build,
            "files": [
                {
                    "path": path,
                    "classification": "FORMAL_ASSET" if path == "Standards/NEW_STANDARD.md" else "SCRIPT",
                    "intended_action": "CREATE" if path == "Standards/NEW_STANDARD.md" else "UPDATE",
                    "asset_title": "New Standard",
                    "asset_type": "Platform Governance Standard",
                    "knowledge_system": "SYS",
                    "universal_asset_identifier": "UAI_ALLOCATION_REQUIRED",
                    "proposed_version": "1.0.0",
                }
                for path in all_paths
            ],
        }
        routing = {
            "build_number": build,
            "files": [
                {
                    "path": path,
                    "destination": path,
                    "action": "REPLACE_FILE" if path == "13_Project_Genesis/Import/transactional_build_import.py" else "CREATE_FILE",
                }
                for path in all_paths
            ],
        }
        files[f"{record}/BUILD_MANIFEST.json"] = (json.dumps(manifest) + "\n").encode()
        files[f"{record}/ASSET_INTENT_MANIFEST.json"] = (json.dumps(intent) + "\n").encode()
        files[f"{record}/ROUTING_MANIFEST.json"] = (json.dumps(routing) + "\n").encode()
        with zipfile.ZipFile(package, "w") as archive:
            for path, content in files.items():
                archive.writestr(path, content)
        return package

    def test_metadata_is_discovered_from_each_candidate_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for build, title, version in [
                ("0040", "first test build", "1.1.0"),
                ("0041", "second test build", "2.0.0"),
            ]:
                repo = self.make_repo(root / build)
                package = self.make_zip(root / build, build, title, version)
                report = root / build / "report.json"
                code = IMPORTER.main([str(package), str(repo), "--report", str(report)])
                self.assertEqual(code, 0)
                data = json.loads(report.read_text(encoding="utf-8"))
                self.assertEqual(data["build_number"], build)
                self.assertEqual(data["build_title"], title)
                self.assertEqual(data["package_version"], version)
                self.assertTrue(data["apply_allowed"])
                self.assertFalse(data["applied"])


if __name__ == "__main__":
    unittest.main()
