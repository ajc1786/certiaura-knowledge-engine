from __future__ import annotations
import importlib.util, json, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"13_Project_Genesis/Release/derive_build_0052_predecessor_evidence.py"
spec=importlib.util.spec_from_file_location("derive0052",SCRIPT); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
def git(repo,*args): return subprocess.run(["git","-C",str(repo),*args],check=True,text=True,stdout=subprocess.PIPE).stdout.strip()
class PredecessorEvidenceTests(unittest.TestCase):
 def make_repo(self,td):
  repo=Path(td)/"repo"; repo.mkdir(); git(repo,"init"); git(repo,"config","user.email","test@example.com"); git(repo,"config","user.name","Test")
  files=[]
  for i in range(59):
   rel=f"Standards/Build0052Fixture/file_{i:02d}.txt"; p=repo/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(f"fixture {i}\n",encoding="utf-8"); files.append({"repository_path":rel})
  rec=repo/"Documentation/Build_Records/0052"; rec.mkdir(parents=True); (rec/"ASSET_INTENT_MANIFEST.json").write_text(json.dumps({"build_number":"0052","candidate":"RC6","files":files})+"\n",encoding="utf-8"); (rec/"CANDIDATE_DELIVERY.json").write_text(json.dumps({"candidate":"RC6"})+"\n",encoding="utf-8")
  git(repo,"add","."); git(repo,"commit","-m","synthetic predecessor"); return repo,git(repo,"rev-parse","HEAD"),files
 def test_derives_from_git_objects_and_rejects_unapproved_overlap(self):
  with tempfile.TemporaryDirectory() as td:
   repo,commit,files=self.make_repo(td); current=Path(td)/"current.json"; current.write_text(json.dumps({"build_number":"0053","files":[]})+"\n",encoding="utf-8")
   result=mod.derive(repo,current,expected_commit=commit,expected_count=59); self.assertEqual(result["source"],"CANONICAL_GIT_OBJECTS"); self.assertEqual(result["predecessor_path_count"],59)
   current.write_text(json.dumps({"build_number":"0053","files":[{"repository_path":files[0]["repository_path"]}]})+"\n",encoding="utf-8")
   with self.assertRaises(RuntimeError): mod.derive(repo,current,expected_commit=commit,expected_count=59)
 def test_explicit_overlap_is_allowed(self):
  with tempfile.TemporaryDirectory() as td:
   repo,commit,files=self.make_repo(td); current=Path(td)/"current.json"; current.write_text(json.dumps({"build_number":"0053","files":[{"repository_path":files[0]["repository_path"],"approved_predecessor_overlap":True}]})+"\n",encoding="utf-8")
   result=mod.derive(repo,current,expected_commit=commit,expected_count=59); self.assertEqual(result["approved_intersection"],[files[0]["repository_path"]])
if __name__=="__main__": unittest.main()
