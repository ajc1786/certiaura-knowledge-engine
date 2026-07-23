from __future__ import annotations
import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; REC=ROOT/"Documentation/Build_Records/0059"
class Tests(unittest.TestCase):
 def test_counts(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text()); self.assertEqual(len([x for x in m["files"] if x.get("classification")=="EXAMPLE"]),20); self.assertEqual(len([x for x in m["files"] if x.get("classification")=="FORMAL_ASSET"]),7)
 def test_inventory_matches_manifest(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text());
  with (REC/"PACKAGE_INVENTORY.csv").open(encoding="utf-8",newline="") as h: rows=list(csv.DictReader(h))
  self.assertEqual(sorted(x["repository_path"] for x in m["files"]),sorted(x["repository_path"] for x in rows))
 def test_allowed_roots(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text()); allowed=set(json.loads((REC/"ROUTING_MANIFEST.json").read_text())["allowed_roots"]); self.assertTrue(all(x["repository_path"].split("/",1)[0] in allowed for x in m["files"]))
 def test_no_runtime_artifacts(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text()); self.assertFalse([x for x in m["files"] if "__pycache__" in x["repository_path"] or x["repository_path"].endswith(".pyc")])
 def test_commit_subject_exact(self): self.assertEqual((REC/"COMMIT_MESSAGE.txt").read_text().strip(),"Add Certiaura Build 0059 tesamorelin governed review-board approvals, evidence-pack version control, challenge and appeal resolution, suspension recovery, periodic reassessment and reusable peptide-review operating model baseline")
 def test_closure_evidence_requirement(self): self.assertTrue(json.loads((REC/"GITHUB_ACTIONS_CLOSURE_EVIDENCE_REQUIREMENTS.json").read_text())["copy_ready_final_block_required"])
 def test_lf_text(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text());
  for x in m["files"]:
   p=ROOT/x["repository_path"]
   if p.suffix.lower() in {".json",".md",".py",".ps1",".cmd",".csv",".txt",".sha256",".gitignore"}: self.assertNotIn(b"\r\n",p.read_bytes(),x["repository_path"])
 def test_ignored_evidence_folder(self): self.assertIn("*.json",(REC/"Closure_Evidence/.gitignore").read_text())
 def test_windows_normalisation_carried_forward(self): self.assertIn('replace("\\\\","/")',(ROOT/"13_Project_Genesis/Validators/validate_build_0059_repository.py").read_text())
 def test_copy_ready_standard_formal_asset(self):
  m=json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text()); paths=[x["repository_path"] for x in m["files"] if x.get("classification")=="FORMAL_ASSET"]; self.assertIn("Standards/CERTIAURA_POWERSHELL_CLOSURE_EVIDENCE_OUTPUT_STANDARD.md",paths)
