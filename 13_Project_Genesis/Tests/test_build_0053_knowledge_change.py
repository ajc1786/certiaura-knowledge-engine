from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATORS = ROOT / "13_Project_Genesis/Validators"
sys.path.insert(0, str(VALIDATORS))

from retatrutide_knowledge_change_common import load_json, validate_bundle, validate_record


class KnowledgeChangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        manifest_path = ROOT / "Documentation/Build_Records/0053/ASSET_INTENT_MANIFEST.json"
        cls.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        cls.example_paths = sorted(
            ROOT / item["repository_path"]
            for item in cls.manifest["files"]
            if item.get("classification") == "EXAMPLE"
        )

    def examples(self, name: str) -> Path:
        return ROOT / "05_Monitoring/Examples/Retatrutide" / name

    def test_valid_and_conditional_examples(self) -> None:
        paths = [
            path
            for path in self.example_paths
            if path.name.startswith(("valid_", "conditional_"))
        ]
        self.assertGreater(len(paths), 0)
        for path in paths:
            self.assertEqual(validate_record(load_json(path)), [], path.name)

    def test_invalid_examples_fail(self) -> None:
        paths = [path for path in self.example_paths if path.name.startswith("invalid_")]
        self.assertGreater(len(paths), 0)
        for path in paths:
            self.assertTrue(validate_record(load_json(path)), path.name)

    def test_valid_bundle(self) -> None:
        names = [
            "valid_knowledge_change_proposal.example.json",
            "valid_cross_asset_impact_assessment.example.json",
            "valid_controlled_change_approval.example.json",
            "valid_change_implementation_package.example.json",
            "valid_publication_release.example.json",
            "valid_post_change_effectiveness_review.example.json",
        ]
        self.assertEqual(
            validate_bundle([load_json(self.examples(name)) for name in names]),
            [],
        )


if __name__ == "__main__":
    unittest.main()
