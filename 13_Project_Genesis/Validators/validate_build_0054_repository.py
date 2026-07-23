from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
from build_0054_asset_ownership import load_manifest,owned_paths
from retatrutide_operational_assurance_common import load_json,validate_record
EXPECTED_COMMIT="d5b7b84a2c543bbdd5cad8727f1c9005c27ca70d"; MARK="<!-- CERTIAURA_BUILD_0054_CHECKPOINT_START -->"; LM="<!-- CERTIAURA_BUILD_0054_LESSONS_START -->"
def norm(x): return x.replace("\\","/")
def validate(repo,report_path=None,expected_predecessor_commit=EXPECTED_COMMIT):
 errors=[]; mp=repo/"Documentation/Build_Records/0054/ASSET_INTENT_MANIFEST.json"
 if not mp.exists(): return {"build_number":"0054","valid":False,"errors":["Build 0054 Asset Intent Manifest missing"],"result":"FAIL"}
 m=load_manifest(mp); skip=None
 if report_path:
  try: skip=norm(str(report_path.resolve().relative_to(repo.resolve())))
  except ValueError: pass
 for rel in owned_paths(m):
  if rel!=skip and not (repo/rel).is_file(): errors.append(f"owned path missing: {rel}")
 ex=[x for x in m.get("files",[]) if x.get("classification")=="EXAMPLE"]
 for x in ex:
  p=repo/x["repository_path"]
  if not p.exists(): continue
  ve=validate_record(load_json(p))
  if p.name.startswith(("valid_","conditional_")): errors += [f"{p.name}: {z}" for z in ve]
  elif p.name.startswith("invalid_") and not ve: errors.append(f"{p.name} unexpectedly passed")
 ep=repo/"Documentation/Build_Records/0054/PREDECESSOR_CANONICAL_EVIDENCE.json"
 if not ep.exists(): errors.append("canonical predecessor evidence missing")
 else:
  e=json.loads(ep.read_text(encoding="utf-8")); checks={"source":"CANONICAL_GIT_OBJECTS","predecessor_build":"0053","predecessor_candidate":"RC4","predecessor_commit":expected_predecessor_commit,"predecessor_path_count":83,"withdrawn_candidates":["RC1","RC2","RC3"]}
  for k,v in checks.items():
   if e.get(k)!=v: errors.append(f"predecessor evidence {k} mismatch")
  if e.get("prohibited_intersection"): errors.append("prohibited predecessor/current-build intersection exists")
 for path,marker in [(repo/"00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",MARK),(repo/"00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md",LM)]:
  if path.exists() and marker not in path.read_text(encoding="utf-8"): errors.append(f"governance marker missing: {marker}")
 reg=repo/"Documentation/Master_Asset_Register.csv"
 if not reg.exists(): errors.append("Master Asset Register missing")
 else:
  with reg.open("r",encoding="utf-8-sig",newline="") as h: rows=list(csv.DictReader(h)); headers=h.seek(0) if False else []
  by={norm(str(r.get("Repository Path",r.get("repository_path","")))).lower():r for r in rows}
  for x in m.get("files",[])+m.get("generated_files",[]):
   if x.get("classification")=="FORMAL_ASSET":
    r=by.get(norm(x["repository_path"]).lower())
    if not r: errors.append(f"formal asset not registered: {x['repository_path']}")
    elif not str(r.get("Universal Asset Identifier",r.get("UAI",""))).strip(): errors.append(f"formal asset blank UAI: {x['repository_path']}")
 result={"build_number":"0054","owned_path_count":len(owned_paths(m)),"example_count":len(ex),"valid":not errors,"errors":errors,"result":"BUILD_0054_REPOSITORY_VALIDATED" if not errors else "FAIL"}; return result
def main():
 p=argparse.ArgumentParser(); p.add_argument("repository"); p.add_argument("--report"); p.add_argument("--expected-predecessor-commit",default=EXPECTED_COMMIT); a=p.parse_args(); report=Path(a.report).resolve() if a.report else None; result=validate(Path(a.repository).resolve(),report,a.expected_predecessor_commit)
 if report:
  report.parent.mkdir(parents=True,exist_ok=True)
  report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
 print(json.dumps(result,indent=2)); return 0 if result["valid"] else 1
if __name__=="__main__": raise SystemExit(main())
