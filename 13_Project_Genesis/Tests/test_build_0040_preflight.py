from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "Release" / "build_package_preflight.py"
SPEC = importlib.util.spec_from_file_location("build_package_preflight", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

IMPORTER_PATH = Path(__file__).resolve().parents[1] / "Import" / "transactional_build_import.py"
RUNNER_PATH = Path(__file__).resolve().parents[1] / "Import" / "run_build_0040_import.py"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_package(path: Path, mutate: str | None = None) -> None:
    build = "9999"
    root = f"Documentation/Build_Records/{build}/"
    importer = IMPORTER_PATH.read_text(encoding="utf-8")
    runner = RUNNER_PATH.read_text(encoding="utf-8").replace('BUILD_NUMBER = "0040"', 'BUILD_NUMBER = "9999"')
    if mutate == "legacy_importer_metadata":
        importer = importer.replace(
            '"build_number": build_number,',
            '"build_number": "0039",',
            1,
        )
    files: dict[str, bytes] = {
        "Standards/VALID_STANDARD.md": b"# Valid\n",
        "Scripts/valid.py": b"VALUE = 1\n",
        "13_Project_Genesis/Import/transactional_build_import.py": importer.encode(),
        f"13_Project_Genesis/Import/run_build_{build}_import.py": runner.encode(),
        root + "COMMIT_MESSAGE.txt": b"Add Certiaura Build 9999 valid synthetic test package\n",
        root + "PRE_RELEASE_SYNTHETIC_IMPORT_REPORT.json": b'{"valid": true}\n',
    }
    if mutate == "trailing_whitespace":
        files["Standards/VALID_STANDARD.md"] = b"# Invalid  \n"
    if mutate == "runtime":
        files["Scripts/__pycache__/valid.cpython-314.pyc"] = b"bytecode"
    if mutate == "case_collision":
        files["standards/VALID_STANDARD.md"] = b"collision\n"

    generated = {
        root + "BUILD_MANIFEST.json",
        root + "ROUTING_MANIFEST.json",
        root + "ASSET_INTENT_MANIFEST.json",
        root + "PACKAGE_INVENTORY.csv",
        root + "CHECKSUMS.sha256",
    }
    all_paths = sorted(set(files) | generated)
    manifest = {
        "build_number": build,
        "build_title": "valid synthetic test package",
        "package_version": "9.9.9",
        "exact_commit_message": "Add Certiaura Build 9999 valid synthetic test package",
        "package_file_count": len(all_paths),
        "formal_assets_created": 1,
        "destructive_deletions_permitted": False,
    }
    files[root + "BUILD_MANIFEST.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    routing = {
        "build_number": build,
        "files": [
            {
                "path": item,
                "destination": item,
                "action": "CREATE_FILE",
                "classification": "TEST",
            }
            for item in all_paths
        ],
    }
    files[root + "ROUTING_MANIFEST.json"] = (json.dumps(routing, indent=2) + "\n").encode()
    intent_files = []
    for item in all_paths:
        record = {"path": item, "classification": "TEST", "intended_action": "CREATE"}
        if item == "Standards/VALID_STANDARD.md":
            record.update({
                "classification": "FORMAL_ASSET",
                "asset_title": "Valid Standard",
                "asset_type": "Platform Governance Standard",
                "knowledge_system": "SYS",
                "universal_asset_identifier": "UAI_ALLOCATION_REQUIRED",
                "proposed_version": "1.0.0",
                "proposed_status": "ACTIVE",
            })
        intent_files.append(record)
    intent = {"build_number": build, "files": intent_files}
    files[root + "ASSET_INTENT_MANIFEST.json"] = (json.dumps(intent, indent=2) + "\n").encode()

    def refresh_records() -> None:
        output = io.StringIO(newline="")
        writer = csv.DictWriter(
            output,
            fieldnames=["path", "classification", "action", "sha256", "size_bytes"],
            lineterminator="\n",
        )
        writer.writeheader()
        for item in all_paths:
            data = files.get(item, b"")
            digest = "" if item.endswith("PACKAGE_INVENTORY.csv") or item.endswith("CHECKSUMS.sha256") else sha256(data)
            writer.writerow({
                "path": item,
                "classification": "TEST",
                "action": "CREATE_FILE",
                "sha256": digest,
                "size_bytes": len(data),
            })
        files[root + "PACKAGE_INVENTORY.csv"] = output.getvalue().encode()
        checks = [
            f"{sha256(files[item])}  {item}"
            for item in all_paths
            if not item.endswith("CHECKSUMS.sha256")
        ]
        files[root + "CHECKSUMS.sha256"] = ("\n".join(checks) + "\n").encode()

    refresh_records()
    refresh_records()
    refresh_records()

    if mutate == "unlisted":
        files["Documentation/UNLISTED.txt"] = b"not declared\n"
    if mutate == "checksum":
        files["Standards/VALID_STANDARD.md"] = b"changed after checksums\n"
    if mutate == "wrapper":
        files = {f"Certiaura_Build_9999_Test/{key}": value for key, value in files.items()}

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in sorted(files):
            archive.writestr(item, files[item])


class Build0040PreflightTests(unittest.TestCase):
    def check(self, mutation: str | None):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "package.zip"
            make_package(package, mutation)
            return MODULE.run_preflight(package)

    def test_valid_package_passes_actual_importer_dry_run_and_apply(self):
        report = self.check(None)
        self.assertTrue(report.valid, report.errors)
        self.assertTrue(report.gates["actual_transactional_importer_dry_run"])
        self.assertTrue(report.gates["actual_transactional_importer_apply"])
        self.assertTrue(report.gates["git_diff_check_after_staging"])
        self.assertTrue(report.gates["git_diff_cached_check_after_staging"])
        self.assertTrue(report.synthetic_repository["unrelated_historical_files_preserved"])
        self.assertTrue(report.synthetic_repository["importer_metadata_matches_current_build"])

    def test_prior_build_importer_residue_is_rejected(self):
        self.assertFalse(self.check("legacy_importer_metadata").valid)

    def test_wrapper_folder_is_rejected(self):
        self.assertFalse(self.check("wrapper").valid)

    def test_trailing_whitespace_is_rejected(self):
        self.assertFalse(self.check("trailing_whitespace").valid)

    def test_runtime_artifact_is_rejected(self):
        self.assertFalse(self.check("runtime").valid)

    def test_case_only_collision_is_rejected(self):
        self.assertFalse(self.check("case_collision").valid)

    def test_unlisted_package_member_is_rejected(self):
        self.assertFalse(self.check("unlisted").valid)

    def test_checksum_drift_is_rejected(self):
        self.assertFalse(self.check("checksum").valid)


if __name__ == "__main__":
    unittest.main()
