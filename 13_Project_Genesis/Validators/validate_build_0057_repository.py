from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
from build_0057_asset_ownership import load_manifest,owned_paths
from tesamorelin_workflow_simulation_common import load_json,validate_record
EXPECTED_COMMIT="2e6fe434bf1d0566bf3d1afa33bae24ce13b3b44"
CHECKPOINT_MARKER="<!-- CERTIAURA_BUILD_0057_CHECKPOINT_START -->"
LESSONS_MARKER="<!-- CERTIAURA_BUILD_0057_LESSONS_START -->"
def normalise(v): return str(v).replace("\\","/")
def validate(repository,report_path=None,expected_predecessor_commit=EXPECTED_COMMIT):
 repo=Path(repository).resolve(); errors=[]; mp=repo/"Documentation/Build_Records/0057/ASSET_INTENT_MANIFEST.json"
 if not mp.exists(): return {"build_number":"0057","valid":False,"errors":["Build 0057 Asset Intent Manifest missing"],"result":"FAIL"}
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
 ep=repo/"Documentation/Build_Records/0057/PREDECESSOR_CANONICAL_EVIDENCE.json"
 if not ep.exists(): errors.append("canonical predecessor evidence missing")
 else:
  ev=json.loads(ep.read_text(encoding="utf-8")); checks={"source":"CANONICAL_GIT_OBJECTS","predecessor_build":"0056","predecessor_candidate":"RC1","predecessor_commit":expected_predecessor_commit,"predecessor_path_count":91}
  for k,v in checks.items():
   if ev.get(k)!=v: errors.append("predecessor evidence "+k+" mismatch")
  if ev.get("prohibited_intersection"): errors.append("prohibited predecessor/current-build intersection exists")
  if ev.get("approved_intersection")!=[]: errors.append("unexpected predecessor intersection")
 for p,marker in [(repo/"00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",CHECKPOINT_MARKER),(repo/"00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md",LESSONS_MARKER)]:
  if p.exists() and marker not in p.read_text(encoding="utf-8"): errors.append("governance marker missing: "+marker)
 reg=repo/"Documentation/Master_Asset_Register.csv"
 if not reg.exists(): errors.append("Master Asset Register missing")
 else:
  with reg.open("r",encoding="utf-8-sig",newline="") as h: rows=list(csv.DictReader(h))
  by={normalise(r.get("Repository Path",r.get("repository_path",""))).lower():r for r in rows}
  for i in m.get("files",[])+m.get("generated_files",[]):
   if i.get("classification")=="FORMAL_ASSET":
    row=by.get(normalise(i["repository_path"]).lower())
    if not row: errors.append("formal asset not registered: "+i["repository_path"])
    elif not str(row.get("Universal Asset Identifier",row.get("UAI",""))).strip(): errors.append("formal asset blank UAI: "+i["repository_path"])
 result={"build_number":"0057","owned_path_count":len(owned_paths(m)),"example_count":len(ex),"formal_asset_count":len([i for i in m.get("files",[]) if i.get("classification")=="FORMAL_ASSET"]),"valid":not errors,"errors":errors,"result":"BUILD_0057_REPOSITORY_VALIDATED" if not errors else "FAIL"}
 return result
def main():
 p=argparse.ArgumentParser(); p.add_argument("repository"); p.add_argument("--report"); p.add_argument("--expected-predecessor-commit",default=EXPECTED_COMMIT); a=p.parse_args(); report=Path(a.report).resolve() if a.report else None; r=validate(a.repository,report,a.expected_predecessor_commit)
 if report: report.parent.mkdir(parents=True,exist_ok=True); report.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8",newline="\n")
 print(json.dumps(r,indent=2)); return 0 if r["valid"] else 1
if __name__=="__main__": raise SystemExit(main())
