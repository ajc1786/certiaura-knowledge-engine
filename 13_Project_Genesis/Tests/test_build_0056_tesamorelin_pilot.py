from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "Documentation/Build_Records/0056/ASSET_INTENT_MANIFEST.json"
VALIDATOR_DIR = ROOT / "13_Project_Genesis/Validators"
import sys
sys.path.insert(0, str(VALIDATOR_DIR))
from tesamorelin_pilot_common import load_json, validate_bundle, validate_record


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.examples = [
            ROOT / item["repository_path"]
            for item in manifest["files"]
            if item.get("classification") == "EXAMPLE"
        ]

    def test_valid_and_conditional_examples(self):
        targets = [path for path in self.examples if path.name.startswith(("valid_", "conditional_"))]
        self.assertTrue(targets)
        for path in targets:
            self.assertEqual([], validate_record(load_json(path)), path.name)

    def test_invalid_examples_fail(self):
        targets = [path for path in self.examples if path.name.startswith("invalid_")]
        self.assertTrue(targets)
        for path in targets:
            self.assertTrue(validate_record(load_json(path)), path.name)

    def test_valid_bundle(self):
        selected_names = {
            "valid_evidence_corpus_map.example.json",
            "valid_biological_boundary.example.json",
            "valid_safety_boundary.example.json",
            "valid_monitoring_model.example.json",
            "valid_pilot_acceptance_decision.example.json",
            "valid_evidence_gap_decision.example.json",
        }
        records = [load_json(path) for path in self.examples if path.name in selected_names]
        self.assertEqual([], validate_bundle(records))

    def test_target_specific_paths_only(self):
        for path in self.examples:
            self.assertIn("/Tesamorelin/", path.as_posix())
            self.assertNotIn("/Retatrutide/", path.as_posix())


if __name__ == "__main__":
    unittest.main()
