from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
from build_0060_asset_ownership import load_manifest,owned_paths
from bpc157_transition_common import load_json,validate_record
EXPECTED_COMMIT="594152fcfba3b1612b71d7b6e5c23759c906e464"
CHECKPOINT_MARKER="<!-- CERTIAURA_BUILD_0060_CHECKPOINT_START -->"
LESSONS_MARKER="<!-- CERTIAURA_BUILD_0060_LESSONS_START -->"
def normalise(v): return str(v).replace("\\","/")
def validate(repository,report_path=None,expected_predecessor_commit=EXPECTED_COMMIT):
 repo=Path(repository).resolve(); errors=[]; mp=repo/"Documentation/Build_Records/0060/ASSET_INTENT_MANIFEST.json"
 if not mp.exists(): return {"build_number":"0060","valid":False,"errors":["Build 0060 Asset Intent Manifest missing"],"result":"FAIL"}
 m=load_manifest(mp); skip=None
 if report_path:
  try: skip=normalise(Path(report_path).resolve().relative_to(repo))
  except ValueError: pass
 for rel in owned_paths(m):
  if rel!=skip and not (repo/rel).is_file(): errors.append("owned path missing: "+rel)
 ex=[i for i in m.get("files",[]) if i.get("classification")=="EXAMPLE"]
 for i in ex:
  p=repo/i["repository_path"]
  if not p.exists(): continue
  ve=validate_record(load_json(p))
  if p.name.startswith(("valid_","conditional_")): errors.extend([p.name+": "+x for x in ve])
  elif p.name.startswith("invalid_") and not ve: errors.append(p.name+" unexpectedly passed")
 if len(ex)!=21: errors.append("expected 21 examples")
 formal=[i for i in m.get("files",[]) if i.get("classification")=="FORMAL_ASSET"]
 if len(formal)!=7: errors.append("expected 7 formal assets")
 mar=repo/"Documentation/Master_Asset_Register.csv"
 if not mar.exists(): errors.append("Master Asset Register missing")
 else:
  with mar.open(encoding="utf-8-sig",newline="") as h: rows=list(csv.DictReader(h))
  for item in formal:
   matches=[r for r in rows if normalise(r.get("Repository Path",""))==item["repository_path"]]
   if len(matches)!=1: errors.append("formal asset registration count is not one: "+item["repository_path"])
 for rel,marker in [("00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",CHECKPOINT_MARKER),("00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md",LESSONS_MARKER)]:
  p=repo/rel
  if not p.exists() or p.read_text(encoding="utf-8").count(marker)!=1: errors.append("governance marker invalid: "+marker)
 close=repo/"Scripts/Close_Certiaura_Build_0060.ps1"
 if close.exists():
  text=close.read_text(encoding="utf-8")
  tokens=["Invoke-CertiauraGitNonInteractiveGuard","CERTIAURA_BUILD_0060_CLOSURE_EVIDENCE_BEGIN","CERTIAURA_BUILD_0060_CLOSURE_EVIDENCE_END","BUILD_0060_COMMITTED_PUSHED","BUILD_0060_GITHUB_ACTIONS_GREEN","BUILD_0060_READY_FOR_FOUNDER_GREEN","NO_MANUAL_GIT_OBJECT_CLEANUP_PROMPTS","BUILD_0060_CLOSURE_EVIDENCE.json","Actions URL:","Run attempt:","Local and origin/main aligned:","Repository clean:"]
  for token in tokens:
   if token not in text: errors.append("close script missing "+token)
 ignored=repo/"Documentation/Build_Records/0060/Closure_Evidence/.gitignore"
 if not ignored.exists() or "*.json" not in ignored.read_text(encoding="utf-8"): errors.append("closure evidence local runtime JSON is not ignored")
 result={"build_number":"0060","owned_path_count":len(owned_paths(m)),"example_count":len(ex),"formal_asset_count":len(formal),"valid":not errors,"errors":errors,"result":"BUILD_0060_REPOSITORY_VALIDATED" if not errors else "FAIL"}
 if report_path: Path(report_path).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
 return result
def main():
 p=argparse.ArgumentParser(); p.add_argument("repository"); p.add_argument("--report"); p.add_argument("--expected-predecessor-commit",default=EXPECTED_COMMIT); a=p.parse_args(); r=validate(a.repository,a.report,a.expected_predecessor_commit); print(json.dumps(r,indent=2)); return 0 if r["valid"] else 1
if __name__=="__main__": raise SystemExit(main())
