import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; REC=ROOT/"Documentation/Build_Records/0060"; P=ROOT/"13_Project_Genesis/Release/derive_build_0059_predecessor_evidence.py"
class Tests(unittest.TestCase):
 def test_requirements_point_to_closed_build_0059(self):
  d=json.loads((REC/"PREDECESSOR_REQUIREMENTS.json").read_text()); self.assertEqual(d["canonical_commit"],"594152fcfba3b1612b71d7b6e5c23759c906e464"); self.assertEqual(d["expected_package_path_count"],97)
 def test_derivation_uses_canonical_git_objects(self):
  t=P.read_text(); self.assertIn("git_bytes",t); self.assertIn("EXPECTED_FORMAL_UAIS",t); self.assertIn("EXPECTED_SUBJECT",t)
 def test_exact_predecessor_commit_subject(self): self.assertIn("Add Certiaura Build 0059 tesamorelin governed review-board approvals",P.read_text())
 def test_exact_predecessor_formal_uais(self):
  t=P.read_text();
  for u in ["CERT-SYS-000871","CERT-SYS-000872","CERT-SYS-000873","CERT-EKS-000790","CERT-MKS-000221","CERT-PKS-000439","CERT-PKS-000440"]: self.assertIn(u,t)
 def test_no_unapproved_package_overlap(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text()); self.assertEqual([x for x in m["files"] if x.get("approved_predecessor_overlap")],[])
 def test_exact_predecessor_package_count(self): self.assertIn("EXPECTED_PATH_COUNT = 97",P.read_text())
if __name__=="__main__": unittest.main()
