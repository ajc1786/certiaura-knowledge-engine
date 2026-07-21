from __future__ import annotations
import argparse, datetime as dt, hashlib, json, re, sys
from pathlib import Path
from build_0048_asset_ownership import BUILD_PROVENANCE, owned_paths
DIRECT_KEYS={"patient_name","full_name","address","email","telephone","phone","nhs_number","national_identifier","date_of_birth"}
PROHIBITED=("INCREASE DOSE","DECREASE DOSE","START MEDICINE","STOP MEDICINE","DIAGNOSIS CONFIRMED","NO CLINICAL REVIEW NEEDED","SAFE TO USE")
def scan(value,path="$"):
    errors=[]
    if isinstance(value,dict):
        for k,v in value.items():
            if k.lower() in DIRECT_KEYS: errors.append(f"direct identifier field prohibited: {path}.{k}")
            errors.extend(scan(v,path+"."+k))
    elif isinstance(value,list):
        for i,v in enumerate(value): errors.extend(scan(v,f"{path}[{i}]") )
    return errors

def prohibited(value):
    t=json.dumps(value,ensure_ascii=True).upper(); return [x for x in PROHIBITED if x in t]
def iso(value): dt.datetime.fromisoformat(value.replace("Z","+00:00"))
def validate_review(d):
    e=[]
    for k in ("schema_version","build_provenance","review_id","export_id","export_sha256","reviewer_role_reference","generator_actor_reference","state","decision","reviewed_at","rationale","attestation"):
        if k not in d: e.append("missing required field: "+k)
    if d.get("build_provenance")!=BUILD_PROVENANCE:e.append("build_provenance mismatch")
    if not re.fullmatch(r"[A-F0-9]{64}",str(d.get("export_sha256",""))):e.append("export_sha256 must be uppercase SHA-256")
    if d.get("reviewer_role_reference")==d.get("generator_actor_reference"):e.append("reviewer and generator must be different actors")
    try: iso(str(d.get("reviewed_at","")))
    except Exception:e.append("reviewed_at must be ISO date-time")
    att=d.get("attestation") or {}
    for k in ("human_review_confirmed","autonomous_treatment_prohibited","direct_identifiers_absent"):
        if att.get(k) is not True:e.append("attestation must confirm "+k)
    e.extend(scan(d)); e.extend("prohibited autonomous clinical language: "+x for x in prohibited(d))
    return e

def validate_chain(d):
    e=[]
    if d.get("build_provenance")!=BUILD_PROVENANCE:e.append("version chain build_provenance mismatch")
    versions=d.get("versions") or []
    ids=[v.get("export_id") for v in versions]
    if len(ids)!=len(set(ids)):e.append("duplicate export_id in version chain")
    current=[v for v in versions if v.get("state")=="CURRENT_APPROVED"]
    if len(current)>1:e.append("more than one CURRENT_APPROVED version")
    idset=set(ids)
    for v in versions:
        pred=v.get("predecessor_export_id")
        if pred is not None and pred not in idset:e.append("missing predecessor: "+str(pred))
        if pred==v.get("export_id"):e.append("self-cycle in version chain")
        if not re.fullmatch(r"[A-F0-9]{64}",str(v.get("sha256",""))):e.append("invalid version sha256")
    # general cycle detection
    predmap={v.get("export_id"):v.get("predecessor_export_id") for v in versions}
    for start in ids:
        seen=set(); cur=start
        while cur:
            if cur in seen:e.append("cycle detected in version chain");break
            seen.add(cur); cur=predmap.get(cur)
    e.extend(scan(d)); return sorted(set(e))
def validate_bundle(d):
    e=[]
    if d.get("build_provenance")!=BUILD_PROVENANCE:e.append("bundle build_provenance mismatch")
    if d.get("state") not in {"BUNDLE_DRAFT","READY_FOR_AUTHORISED_HANDOFF","HANDED_OFF","ACKNOWLEDGED","EXPIRED","WITHDRAWN"}:e.append("invalid bundle state")
    privacy=d.get("privacy") or {}
    if privacy.get("pseudonymised") is not True or privacy.get("direct_identifiers_present") is not False:e.append("bundle privacy controls invalid")
    for c in d.get("components") or []:
        if not re.fullmatch(r"[A-F0-9]{64}",str(c.get("sha256",""))):e.append("invalid component sha256")
        if int(c.get("bytes",0))<1:e.append("component bytes must be positive")
    e.extend(scan(d)); e.extend("prohibited autonomous clinical language: "+x for x in prohibited(d)); return e

def main():
    p=argparse.ArgumentParser();p.add_argument("repository",type=Path);p.add_argument("--report",type=Path);a=p.parse_args(); repo=a.repository.resolve(); errors=[]
    expected=owned_paths(repo); missing=[x for x in expected if not (repo/x).is_file()]
    if missing: errors.extend("missing owned path: "+x for x in missing)
    checks=[("review",repo/"12_Reports/Retatrutide/Examples/valid_clinician_review_approval.example.json",validate_review,True),("changes",repo/"12_Reports/Retatrutide/Examples/conditional_clinician_review_changes_required.example.json",validate_review,True),("self",repo/"12_Reports/Retatrutide/Examples/invalid_self_approval.example.json",validate_review,False),("identifier",repo/"12_Reports/Retatrutide/Examples/invalid_direct_identifier_review.example.json",validate_review,False),("chain",repo/"12_Reports/Retatrutide/Examples/valid_export_version_chain.example.json",validate_chain,True),("broken",repo/"12_Reports/Retatrutide/Examples/invalid_broken_supersession_chain.example.json",validate_chain,False)]
    outcomes=[]
    for name,path,fn,should_pass in checks:
        try:data=json.loads(path.read_text(encoding="utf-8")); found=fn(data)
        except Exception as exc:found=[str(exc)]
        passed=not found; outcomes.append({"fixture":name,"passed":passed,"errors":found})
        if passed!=should_pass:errors.append(f"fixture {name} expected pass={should_pass} got pass={passed}")
    result={"valid":not errors,"errors":errors,"checked_paths":expected,"owned_path_count":len(expected),"build_provenance":BUILD_PROVENANCE,"fixture_outcomes":outcomes}
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result,indent=2));return 0 if result["valid"] else 1
if __name__=="__main__":raise SystemExit(main())
