from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "13_Project_Genesis/Release/derive_build_0051_predecessor_evidence.py"
spec = importlib.util.spec_from_file_location("predecessor_evidence", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EvidenceValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.fixture = Path(self.temp.name)
        path = "Documentation/Build_Records/0051/test.txt"
        manifest_path = module.MANIFEST_PATH
        target = self.fixture / path
        target.parent.mkdir(parents=True)
        target.write_text("test\n", encoding="utf-8", newline="\n")
        manifest_target = self.fixture / manifest_path
        manifest_target.parent.mkdir(parents=True, exist_ok=True)
        predecessor_manifest = {
            "build_number": "0051",
            "build_provenance": "CERT-BUILD-0051",
            "commit_subject": module.EXPECTED_SUBJECT,
            "files": [
                {"repository_path": manifest_path, "classification": "BUILD_RECORD"},
                {"repository_path": path, "classification": "SUPPORTING_FILE"},
            ],
        }
        manifest_target.write_text(json.dumps(predecessor_manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        paths = sorted([manifest_path, path])
        hashes = {item: module.sha_bytes((self.fixture / item).read_bytes()) for item in paths}
        self.evidence = {
            "build_number": "0051",
            "build_provenance": "CERT-BUILD-0051",
            "import_commit_subject": module.EXPECTED_SUBJECT,
            "import_commit_sha": "a",
            "closed_snapshot_sha": "b",
            "predecessor_manifest_sha256": module.sha_bytes(manifest_target.read_bytes()),
            "predecessor_manifest_path_schema": {"container": "ARRAY", "path_fields": ["repository_path"]},
            "package_sha256": "D" * 64,
            "repository_paths": paths,
            "path_sha256": hashes,
            "universal_asset_identifiers": [],
            "approved_replacement_intersection": [],
        }
        self.manifest = {"files": []}

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_evidence_shape(self):
        self.assertEqual([], module.validate_evidence(self.evidence, self.fixture, self.manifest, "D" * 64))

    def test_wrong_subject_blocks(self):
        self.evidence["import_commit_subject"] = "wrong"
        self.assertIn("WRONG_COMMIT_SUBJECT", module.validate_evidence(self.evidence, self.fixture, self.manifest, "D" * 64))

    def test_hash_tamper_blocks(self):
        self.evidence["path_sha256"][self.evidence["repository_paths"][0]] = "0" * 64
        self.assertTrue(any(x.startswith("FIXTURE_HASH_MISMATCH") for x in module.validate_evidence(self.evidence, self.fixture, self.manifest, "D" * 64)))

    def test_unauthorised_intersection_blocks(self):
        self.manifest["files"].append({"repository_path": self.evidence["repository_paths"][0]})
        self.assertIn("UNAUTHORISED_MANIFEST_INTERSECTION", module.validate_evidence(self.evidence, self.fixture, self.manifest, "D" * 64))

    def test_legacy_path_field_is_supported_strictly(self):
        manifest = {"files": [{"path": "A/B.txt"}, {"path": "C/D.txt"}]}
        self.assertEqual(["A/B.txt", "C/D.txt"], module.paths_from_manifest(manifest))
        self.assertEqual({"container": "ARRAY", "path_fields": ["path"]}, module.manifest_path_schema(manifest))

    def test_string_entries_are_supported_strictly(self):
        manifest = {"files": ["A/B.txt", "C/D.txt"]}
        self.assertEqual(["A/B.txt", "C/D.txt"], module.paths_from_manifest(manifest))

    def test_path_alias_conflict_blocks(self):
        manifest = {"files": [{"repository_path": "A/B.txt", "path": "C/D.txt"}]}
        with self.assertRaisesRegex(RuntimeError, "PREDECESSOR_MANIFEST_PATH_ALIAS_CONFLICT"):
            module.paths_from_manifest(manifest)

    def test_path_traversal_blocks(self):
        manifest = {"files": [{"path": "../escape.txt"}]}
        with self.assertRaisesRegex(RuntimeError, "PREDECESSOR_MANIFEST_PATH_INVALID"):
            module.paths_from_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
