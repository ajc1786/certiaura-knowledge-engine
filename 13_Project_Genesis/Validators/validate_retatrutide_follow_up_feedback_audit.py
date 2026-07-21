from __future__ import annotations
import argparse, datetime as dt, json, re, sys
from pathlib import Path
from build_0049_asset_ownership import BUILD_PROVENANCE, owned_paths
DIRECT_KEYS={"patient_name","full_name","address","email","telephone","phone","nhs_number","national_identifier","date_of_birth"}
PROHIBITED=("INCREASE DOSE","DECREASE DOSE","START MEDICINE","STOP MEDICINE","DIAGNOSIS CONFIRMED","NO CLINICAL REVIEW NEEDED","SAFE TO USE")
def scan(value,path="$"):
    errors=[]
    if isinstance(value,dict):
        for k,v in value.items():
            if k.lower() in DIRECT_KEYS: errors.append(f"direct identifier field prohibited: {path}.{k}")
            errors.extend(scan(v,path+"."+k))
    elif isinstance(value,list):
        for i,v in enumerate(value): errors.extend(scan(v,f"{path}[{i}]"))
    return errors
def prohibited(value):
    text=json.dumps(value,ensure_ascii=True).upper(); return [x for x in PROHIBITED if x in text]
def iso(value): dt.datetime.fromisoformat(str(value).replace("Z","+00:00"))
def base(d,required):
    e=[]
    for k in required:
        if k not in d: e.append("missing required field: "+k)
    if d.get("build_provenance")!=BUILD_PROVENANCE:e.append("build_provenance mismatch")
    e.extend(scan(d))
    for phrase in prohibited(d):e.append("prohibited autonomous clinical language: "+phrase)
    return e
def validate_acknowledgement(d):
    e=base(d,("schema_version","build_provenance","acknowledgement_id","handoff_bundle_id","handoff_bundle_sha256","subject_reference","state","recorded_at","actor_role_reference","meaning_boundary"))
    if not re.fullmatch(r"[A-F0-9]{64}",str(d.get("handoff_bundle_sha256",""))):e.append("handoff_bundle_sha256 must be uppercase SHA-256")
    if d.get("meaning_boundary")!="RECEIPT_ONLY_NOT_CLINICAL_AGREEMENT":e.append("acknowledgement meaning boundary mismatch")
    try: iso(d.get("recorded_at"))
    except Exception:e.append("recorded_at must be ISO 8601")
    return e
def validate_follow_up(d):
    e=base(d,("schema_version","build_provenance","follow_up_id","handoff_bundle_id","acknowledgement_id","subject_reference","state","due_at","reviewer_role_reference","urgent_routing_locked","rationale"))
    try: iso(d.get("due_at"))
    except Exception:e.append("due_at must be ISO 8601")
    if d.get("state")=="LOCKED_URGENT_ROUTING" and d.get("urgent_routing_locked") is not True:e.append("urgent routing state must remain locked")
    if d.get("urgent_routing_locked") is True and d.get("state")!="LOCKED_URGENT_ROUTING":e.append("locked urgent routing cannot be downgraded")
    if d.get("state")=="FOLLOW_UP_COMPLETED" and not d.get("completed_at"):e.append("completed follow-up requires completed_at")
    return e
def validate_feedback(d):
    e=base(d,("schema_version","build_provenance","feedback_id","handoff_bundle_id","subject_reference","clinician_role_reference","received_at","disposition","summary","requires_export_amendment"))
    try: iso(d.get("received_at"))
    except Exception:e.append("received_at must be ISO 8601")
    if d.get("disposition")=="EXPORT_AMENDMENT_REQUIRED" and d.get("requires_export_amendment") is not True:e.append("amendment disposition must require export amendment")
    return e
def validate_amendment(d):
    e=base(d,("schema_version","build_provenance","amendment_id","reason","feedback_id","predecessor_export_id","predecessor_export_sha256","replacement_export_id","replacement_export_sha256","author_role_reference","reviewer_role_reference","created_at","approved_at","state","current_approved"))
    for key in ("predecessor_export_sha256","replacement_export_sha256"):
        if not re.fullmatch(r"[A-F0-9]{64}",str(d.get(key,""))):e.append(key+" must be uppercase SHA-256")
    if d.get("predecessor_export_id")==d.get("replacement_export_id"):e.append("amendment must create a new export identifier")
    if d.get("predecessor_export_sha256")==d.get("replacement_export_sha256"):e.append("amendment must create a new export SHA-256")
    if d.get("author_role_reference")==d.get("reviewer_role_reference"):e.append("author and reviewer must be different actors")
    if d.get("supersedes_amendment_id")==d.get("amendment_id"):e.append("amendment chain cycle detected")
    return e
def main():
    p=argparse.ArgumentParser();p.add_argument("repository");p.add_argument("--report");a=p.parse_args();root=Path(a.repository)
    checks=[
      ("12_Reports/Retatrutide/Examples/valid_handoff_acknowledgement.example.json",validate_acknowledgement,True),
      ("12_Reports/Retatrutide/Examples/conditional_no_response_acknowledgement.example.json",validate_acknowledgement,True),
      ("12_Reports/Retatrutide/Examples/valid_follow_up_review.example.json",validate_follow_up,True),
      ("12_Reports/Retatrutide/Examples/valid_locked_urgent_follow_up.example.json",validate_follow_up,True),
      ("12_Reports/Retatrutide/Examples/valid_clinician_feedback_requires_amendment.example.json",validate_feedback,True),
      ("12_Reports/Retatrutide/Examples/invalid_direct_identifier_feedback.example.json",validate_feedback,False),
      ("12_Reports/Retatrutide/Examples/invalid_autonomous_treatment_feedback.example.json",validate_feedback,False),
      ("12_Reports/Retatrutide/Examples/valid_export_amendment_audit.example.json",validate_amendment,True),
      ("12_Reports/Retatrutide/Examples/invalid_amendment_chain.example.json",validate_amendment,False),
    ]
    errors=[];checked=[]
    for rel,fn,should_pass in checks:
        data=json.loads((root/rel).read_text(encoding="utf-8"));result=fn(data);checked.append(rel)
        if should_pass and result:errors.append(rel+": "+"; ".join(result))
        if not should_pass and not result:errors.append(rel+": defective example unexpectedly passed")
    try: paths=owned_paths(root)
    except Exception as exc:errors.append(str(exc));paths=[]
    payload={"valid":not errors,"errors":errors,"checked_paths":checked,"owned_path_count":len(paths),"build_provenance":BUILD_PROVENANCE}
    text=json.dumps(payload,indent=2);print(text)
    if a.report: Path(a.report).write_text(text+"\n",encoding="utf-8",newline="\n")
    return 0 if payload["valid"] else 1
if __name__=="__main__":raise SystemExit(main())
