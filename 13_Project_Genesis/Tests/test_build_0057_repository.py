from __future__ import annotations
import csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; MP=ROOT/"Documentation/Build_Records/0057/ASSET_INTENT_MANIFEST.json"
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.m=json.loads(MP.read_text(encoding="utf-8")); cls.paths=sorted(i["repository_path"] for i in cls.m["files"])
 def test_inventory_exact(self):
  with (ROOT/"Documentation/Build_Records/0057/PACKAGE_INVENTORY.csv").open(newline="",encoding="utf-8") as h: rows=list(csv.DictReader(h)); self.assertEqual(self.paths,sorted(r["repository_path"] for r in rows))
 def test_no_runtime_artifacts(self): self.assertFalse(any("__pycache__" in p or p.endswith(".pyc") for p in self.paths))
 def test_allowed_roots(self):
  allowed={"00_Governance","05_Monitoring","13_Project_Genesis","Database","Documentation","Schemas","Scripts","Standards","Templates"}; self.assertFalse({p.split("/",1)[0] for p in self.paths}-allowed)
 def test_examples_manifest_scoped(self):
  t=(ROOT/"13_Project_Genesis/Tests/test_build_0057_workflow_simulation.py").read_text(); self.assertIn("ASSET_INTENT_MANIFEST.json",t)
 def test_actions_run_id_required(self):
  d=json.loads((ROOT/"Documentation/Build_Records/0057/GITHUB_ACTIONS_CLOSURE_EVIDENCE_REQUIREMENTS.json").read_text()); self.assertTrue(d["mandatory"]); self.assertIn("run_id",d["fields"])
 def test_git_guard_required(self):
  d=json.loads((ROOT/"Documentation/Build_Records/0057/VALIDATION_REQUIREMENTS.json").read_text()); self.assertIn("non-interactive Git guard and config restoration",d["requirements"])
 def test_ps_scripts_ascii(self):
  for p in [ROOT/x for x in self.paths if x.endswith((".ps1",".cmd"))]: p.read_bytes().decode("ascii")
 def test_lf_text(self):
  for p in [ROOT/x for x in self.paths if x.endswith((".json",".md",".py",".csv",".txt"))]: self.assertNotIn(b"\r\n",p.read_bytes(),str(p))
 def test_close_exact_actions_match(self):
  t=(ROOT/"Scripts/Close_Certiaura_Build_0057.ps1").read_text();
  for x in ['head_sha -eq $Head','head_branch -eq "main"','event -eq "push"','name -eq $WorkflowName','run_attempt']: self.assertIn(x,t)
 def test_regression_has_guard_endpoint(self):
  t=(ROOT/"Scripts/Invoke_Certiaura_Build_0057_Windows_PS51_Regression.ps1").read_text(); self.assertIn("BUILD_0057_GIT_NONINTERACTIVE_GUARD_VALIDATED",t); self.assertIn("NO_MANUAL_GIT_OBJECT_CLEANUP_PROMPTS",t)
 def test_ps_scripts_have_no_control_characters(self):
  for p in [ROOT/x for x in self.paths if x.endswith((".ps1",".cmd"))]:
   data=p.read_bytes(); self.assertFalse(any(b<32 and b not in (9,10,13) for b in data),str(p))
 def test_close_manifest_path_and_normalisation(self):
  t=(ROOT/"Scripts/Close_Certiaura_Build_0057.ps1").read_text(); self.assertIn("Documentation\\Build_Records\\0057\\ASSET_INTENT_MANIFEST.json",t); self.assertIn('Replace("\\", "/")',t)
if __name__=="__main__": unittest.main()
