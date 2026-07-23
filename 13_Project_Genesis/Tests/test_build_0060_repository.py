import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; REC=ROOT/"Documentation/Build_Records/0060"; CLOSE=ROOT/"Scripts/Close_Certiaura_Build_0060.ps1"
class Tests(unittest.TestCase):
 def manifest(self): return json.loads((REC/"ASSET_INTENT_MANIFEST.json").read_text())
 def test_counts(self):
  m=self.manifest(); self.assertEqual(len([x for x in m["files"] if x.get("classification")=="EXAMPLE"]),21); self.assertEqual(len([x for x in m["files"] if x.get("classification")=="FORMAL_ASSET"]),7)
 def test_inventory_matches_manifest(self):
  m=self.manifest();
  with (REC/"PACKAGE_INVENTORY.csv").open(encoding="utf-8",newline="") as h: rows=list(csv.DictReader(h))
  self.assertEqual(sorted(x["repository_path"] for x in m["files"]),sorted(x["repository_path"] for x in rows))
 def test_allowed_roots(self):
  m=self.manifest(); allowed=set(json.loads((REC/"ROUTING_MANIFEST.json").read_text())["allowed_roots"]); self.assertTrue(all(x["repository_path"].split("/",1)[0] in allowed for x in m["files"]))
 def test_no_runtime_artifacts(self): self.assertFalse([x for x in self.manifest()["files"] if "__pycache__" in x["repository_path"] or x["repository_path"].endswith(".pyc")])
 def test_lf_text(self):
  for x in self.manifest()["files"]:
   p=ROOT/x["repository_path"]
   if p.suffix.lower() in {".json",".md",".py",".ps1",".cmd",".csv",".txt",".sha256",".gitignore"}: self.assertNotIn(b"\r\n",p.read_bytes(),p)
 def test_commit_subject_exact(self): self.assertEqual((REC/"COMMIT_MESSAGE.txt").read_text().strip(),"Add Certiaura Build 0060 BPC-157 governed evidence reconstruction, regulatory and sport boundary assessment, human-evidence gap control, review-board transition, appeal resolution and repeatable multi-peptide onboarding baseline")
 def test_closure_evidence_requirement(self):
  t=CLOSE.read_text();
  for token in ["CERTIAURA_BUILD_0060_CLOSURE_EVIDENCE_BEGIN","BUILD_0060_GITHUB_ACTIONS_GREEN","BUILD_0060_READY_FOR_FOUNDER_GREEN","BUILD_0060_CLOSURE_EVIDENCE.json"]: self.assertIn(token,t)
 def test_git_guard_carryforward(self): self.assertIn("Invoke-CertiauraGitNonInteractiveGuard",CLOSE.read_text())
 def test_ignored_evidence_folder(self): self.assertEqual((REC/"Closure_Evidence/.gitignore").read_text(),"*.json\n")
 def test_bpc157_formal_asset_paths(self):
  paths=[x["repository_path"] for x in self.manifest()["files"] if x.get("classification")=="FORMAL_ASSET"]; self.assertTrue(all("BPC157" in p or "MULTI_PEPTIDE" in p for p in paths))
if __name__=="__main__": unittest.main()
