from __future__ import annotations
import argparse, json, re
from pathlib import Path
BUILD="CERT-BUILD-0051"
MANIFEST_PATH=Path("Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json")
DIRECT=re.compile(r"\b(patient name|full name|date of birth|dob|nhs number|email address|phone number)\b",re.I)
TREATMENT=re.compile(r"\b(increase dose|decrease dose|continue treatment|stop treatment|prescribe|diagnose|safe to continue)\b",re.I)
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def owned_example_paths(root):
 errors=[]; mf=root/MANIFEST_PATH
 if not mf.is_file(): return [],[f"missing exact Asset Intent Manifest: {MANIFEST_PATH.as_posix()}"]
 manifest=load(mf)
 if manifest.get("build_id")!=BUILD: errors.append("Asset Intent Manifest build_id mismatch")
 paths=[]; seen=set()
 for item in manifest.get("files",[]):
  if item.get("classification")!="EXAMPLE": continue
  if item.get("build_provenance")!=BUILD: errors.append(f"example manifest provenance mismatch: {item.get('path')}"); continue
  rel=str(item.get("path","")).replace("\\","/")
  if not rel or rel in seen: errors.append(f"invalid or duplicate example manifest path: {rel}"); continue
  seen.add(rel)
  if not rel.startswith("12_Reports/Retatrutide/Examples/") or not rel.endswith(".json"): errors.append(f"example path outside controlled route: {rel}"); continue
  p=root/rel
  if not p.is_file(): errors.append(f"manifest-owned example missing: {rel}"); continue
  paths.append(p)
 if not paths: errors.append("no exact Build 0051 example paths resolved from Asset Intent Manifest")
 return sorted(paths),errors
def validate(root):
 errors=[]; checked=[]; examples,scope=owned_example_paths(root); errors.extend(scope)
 for p in examples:
  obj=load(p); checked.append(str(p.relative_to(root)).replace("\\","/")); invalid=p.name.startswith("invalid_"); local=[]
  if obj.get("build_provenance")!=BUILD: local.append("build provenance mismatch")
  blob=json.dumps(obj,sort_keys=True)
  if DIRECT.search(blob): local.append("direct identifier language prohibited")
  if TREATMENT.search(blob): local.append("autonomous treatment language prohibited")
  if "surveillance_state" in obj and obj.get("urgent_routing_active") and obj.get("surveillance_state")!="LOCKED_URGENT_ROUTING": local.append("urgent routing precedence violated")
  if "decision" in obj:
   if obj.get("reviewer_actor_role") in {"AI_SYSTEM","AUTOMATED_SYSTEM"}: local.append("human reopening decision required")
   if obj.get("reviewer_actor_role")==obj.get("generator_actor_role"): local.append("reviewer separation required")
   if obj.get("decision")=="REOPEN_APPROVED" and not str(obj.get("trigger_id","")).strip(): local.append("reopening trigger required")
   if obj.get("urgent_routing_active") and obj.get("decision")!="LOCKED_URGENT_ROUTING": local.append("urgent reopening state required")
  for value in obj.get("source_hashes",[]):
   if not re.fullmatch(r"[A-F0-9]{64}",value): local.append("invalid source hash")
  if "recurrence_state" in obj and obj.get("recurrence_state")=="RECURRENCE_SIGNAL_REVIEW_REQUIRED" and not obj.get("human_review_required"): local.append("human review required")
  if invalid and not local: errors.append(f"{p.name}: invalid fixture unexpectedly passed")
  if not invalid and local: errors.extend(f"{p.name}: {e}" for e in local)
 return {"valid":not errors,"errors":errors,"checked_paths":checked,"owned_path_count":len(checked),"build_provenance":BUILD,"ownership_scope":"EXACT_ASSET_INTENT_MANIFEST_PATHS"}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("root",type=Path); ap.add_argument("--report",type=Path); a=ap.parse_args(); r=validate(a.root.resolve())
 if a.report: a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8",newline="\n")
 print(json.dumps(r,indent=2)); return 0 if r["valid"] else 1
if __name__=="__main__": raise SystemExit(main())
