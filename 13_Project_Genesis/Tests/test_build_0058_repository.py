from __future__ import annotations
import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; REC=ROOT/"Documentation/Build_Records/0058"
class Tests(unittest.TestCase):
 def test_inventory_matches_manifest(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text()); rows=list(csv.DictReader((REC/"PACKAGE_INVENTORY.csv").open())); self.assertEqual(sorted(x["repository_path"] for x in m["files"]),sorted(x["repository_path"] for x in rows))
 def test_counts(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text()); self.assertEqual(len(m["files"]),86); self.assertEqual(len(m["generated_files"]),8); self.assertEqual(len(m["files"])+len(m["generated_files"]),94)
 def test_allowed_roots(self):
  allowed={"05_Monitoring","13_Project_Genesis","Database","Documentation","Schemas","Scripts","Standards","Templates"}; m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text()); self.assertFalse({x["repository_path"].split("/")[0] for x in m["files"]}-allowed)
 def test_no_runtime_artifacts(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text()); self.assertFalse([x for x in m["files"] if "__pycache__" in x["repository_path"] or x["repository_path"].endswith(".pyc")])
 def test_closure_evidence_requirement(self):
  d=json.loads((REC/"GITHUB_ACTIONS_CLOSURE_EVIDENCE_REQUIREMENTS.json").read_text()); self.assertTrue(d["must_match_canonical_commit"]); self.assertEqual(d["required_conclusion"],"success")
 def test_commit_subject_exact(self): self.assertEqual((REC/"COMMIT_MESSAGE.txt").read_text().strip(),"Add Certiaura Build 0058 tesamorelin multi-source evidence quality assessment, conflicting-evidence adjudication, longitudinal signal recurrence, controlled amendment and pilot continuation governance baseline")
 def test_windows_report_path_self_exclusion_normalises_single_backslashes(self):
  import importlib.util
  p=ROOT/"13_Project_Genesis/Validators/validate_build_0058_repository.py"
  s=importlib.util.spec_from_file_location("validate_build_0058_repository",p); self.assertIsNotNone(s); self.assertIsNotNone(s.loader)
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  self.assertEqual(m.normalise(r"Documentation\Build_Records\0058\POST_IMPORT_REPOSITORY_VALIDATION.json"),"Documentation/Build_Records/0058/POST_IMPORT_REPOSITORY_VALIDATION.json")
 def test_lf_text(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text());
  for x in m["files"]:
   p=ROOT/x["repository_path"]
   if p.suffix.lower() in {".json",".md",".py",".ps1",".cmd",".csv",".txt"}: self.assertNotIn(b"\r",p.read_bytes(),x["repository_path"])
if __name__=="__main__": unittest.main()
