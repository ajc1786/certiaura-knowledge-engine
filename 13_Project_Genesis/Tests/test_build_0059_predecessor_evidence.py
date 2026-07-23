from __future__ import annotations
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; REC=ROOT/"Documentation/Build_Records/0059"
class Tests(unittest.TestCase):
 def test_requirements_point_to_closed_build_0058(self):
  d=json.loads((REC/"PREDECESSOR_REQUIREMENTS.json").read_text()); self.assertEqual(d["predecessor_build"],"0058"); self.assertEqual(d["predecessor_candidate"],"RC2"); self.assertEqual(d["canonical_commit"],"011f5a47d756d638b4c0c8b2e122628ff5a6d35a")
 def test_derivation_uses_canonical_git_objects(self): self.assertIn("CANONICAL_GIT_OBJECTS",(ROOT/"13_Project_Genesis/Release/derive_build_0058_predecessor_evidence.py").read_text())
 def test_exact_predecessor_commit_subject(self):
  text=(ROOT/"13_Project_Genesis/Release/derive_build_0058_predecessor_evidence.py").read_text(); self.assertIn("EXPECTED_SUBJECT",text); self.assertIn("Add Certiaura Build 0058 tesamorelin multi-source evidence quality assessment",text)
 def test_exact_predecessor_formal_uais(self):
  text=(ROOT/"13_Project_Genesis/Release/derive_build_0058_predecessor_evidence.py").read_text();
  for uai in ["CERT-EKS-000787","CERT-SYS-000870","CERT-MKS-000220","CERT-EKS-000788","CERT-PKS-000438","CERT-EKS-000789"]: self.assertIn(uai,text)
 def test_exact_predecessor_package_count(self): self.assertEqual(json.loads((REC/"PREDECESSOR_REQUIREMENTS.json").read_text())["expected_package_path_count"],86)
 def test_no_unapproved_package_overlap(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text()); self.assertEqual([x for x in m["files"] if x.get("approved_predecessor_overlap")],[])
