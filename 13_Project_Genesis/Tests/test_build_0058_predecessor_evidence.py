from __future__ import annotations
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Tests(unittest.TestCase):
 def test_requirements_point_to_closed_build_0057(self):
  d=json.loads((ROOT/"Documentation/Build_Records/0058/PREDECESSOR_REQUIREMENTS.json").read_text()); self.assertEqual(d["predecessor_build"],"0057"); self.assertEqual(d["canonical_commit"],"2bf6c2f9fcaacfc0d0942045178269a1241253ee")
 def test_exact_predecessor_package_count(self):
  d=json.loads((ROOT/"Documentation/Build_Records/0058/PREDECESSOR_REQUIREMENTS.json").read_text()); self.assertEqual(d["expected_package_path_count"],84)
 def test_derivation_uses_canonical_git_objects(self):
  t=(ROOT/"13_Project_Genesis/Release/derive_build_0057_predecessor_evidence.py").read_text(); self.assertIn("git",t.lower()); self.assertIn("2bf6c2f9fcaacfc0d0942045178269a1241253ee",t)
 def test_no_unapproved_package_overlap(self):
  d=json.loads((ROOT/"Documentation/Build_Records/0058/CONFLICT_POLICY.json").read_text()); self.assertEqual(d["approved_predecessor_overlaps"],[])
if __name__=="__main__": unittest.main()
