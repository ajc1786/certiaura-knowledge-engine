from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone, timedelta
from pathlib import Path

BUILD_PROVENANCE = "CERT-BUILD-0048"
DIRECT_KEYS = {"patient_name","full_name","address","email","telephone","phone","nhs_number","national_identifier","date_of_birth"}

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest().upper()

def scan(value, path="$"):
    hits=[]
    if isinstance(value,dict):
        for k,v in value.items():
            if k.lower() in DIRECT_KEYS: hits.append(path+"."+k)
            hits.extend(scan(v,path+"."+k))
    elif isinstance(value,list):
        for i,v in enumerate(value): hits.extend(scan(v,f"{path}[{i}]") )
    return hits

def write(path: Path, text: str):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text.replace("\r\n","\n").replace("\r","\n").rstrip()+"\n",encoding="utf-8",newline="\n")

def main():
    p=argparse.ArgumentParser(); p.add_argument("export",type=Path); p.add_argument("review",type=Path); p.add_argument("version_chain",type=Path); p.add_argument("--output-dir",required=True,type=Path); p.add_argument("--now",default=None); a=p.parse_args()
    export=json.loads(a.export.read_text(encoding="utf-8")); review=json.loads(a.review.read_text(encoding="utf-8")); chain=json.loads(a.version_chain.read_text(encoding="utf-8"))
    hits=scan(export)+scan(review)+scan(chain)
    if hits: raise SystemExit("direct identifier fields detected: "+", ".join(hits))
    if review.get("build_provenance")!=BUILD_PROVENANCE: raise SystemExit("review build provenance mismatch")
    if review.get("decision")!="APPROVED_FOR_CONTROLLED_HANDOFF" or review.get("state")!="APPROVED_FOR_CONTROLLED_HANDOFF": raise SystemExit("approved human review is required")
    if review.get("reviewer_role_reference")==review.get("generator_actor_reference"): raise SystemExit("reviewer and generator must be different actors")
    versions=chain.get("versions") or []
    matching=[v for v in versions if v.get("export_id")==review.get("export_id") and v.get("state")=="CURRENT_APPROVED"]
    if len(matching)!=1: raise SystemExit("reviewed export must be the unique CURRENT_APPROVED version")
    if matching[0].get("approval_review_id")!=review.get("review_id"): raise SystemExit("version chain approval reference mismatch")
    now=datetime.fromisoformat(a.now.replace("Z","+00:00")) if a.now else datetime.now(timezone.utc)
    out=a.output_dir; out.mkdir(parents=True,exist_ok=True)
    components=[]
    for source,role,name in [(a.export,"CLINICIAN_EXPORT","clinician_export.json"),(a.review,"CLINICIAN_REVIEW","clinician_review.json"),(a.version_chain,"VERSION_CHAIN","export_version_chain.json")]:
        target=out/name; target.write_bytes(source.read_bytes()); components.append({"path":name,"sha256":sha(target),"bytes":target.stat().st_size,"role":role})
    bundle={"schema_version":"1.0.0","build_provenance":BUILD_PROVENANCE,"bundle_id":"RET-HANDOFF-"+review["review_id"].replace("RET-REVIEW-","").upper(),"export_id":review["export_id"],"approval_review_id":review["review_id"],"state":"READY_FOR_AUTHORISED_HANDOFF","created_at":now.isoformat().replace("+00:00","Z"),"expires_at":(now+timedelta(days=7)).isoformat().replace("+00:00","Z"),"components":components,"privacy":{"pseudonymised":True,"direct_identifiers_present":False},"urgent_routing_status":"PRESERVED_FROM_EXPORT","safety_statement":"Research and clinician-review information only; not a prescription, diagnosis, dose instruction or treatment authorisation."}
    write(out/"handoff_bundle.json",json.dumps(bundle,indent=2,ensure_ascii=True))
    manifest={"build_provenance":BUILD_PROVENANCE,"bundle_id":bundle["bundle_id"],"files":components+[{'path':'handoff_bundle.json','sha256':sha(out/'handoff_bundle.json'),'bytes':(out/'handoff_bundle.json').stat().st_size,'role':'BUNDLE_DESCRIPTOR'}]}
    write(out/"bundle_manifest.json",json.dumps(manifest,indent=2,ensure_ascii=True))
    lines=["# Retatrutide Controlled Clinician Handoff",f"Bundle: `{bundle['bundle_id']}`",f"Export: `{bundle['export_id']}`",f"Approval: `{bundle['approval_review_id']}`",f"State: `{bundle['state']}`",f"Expires: `{bundle['expires_at']}`","","This bundle supports authorised review only. It is not a prescription, diagnosis, dose instruction or treatment authorisation."]
    write(out/"handoff_summary.md","\n\n".join(lines))
    print(json.dumps({"valid":True,"bundle_id":bundle["bundle_id"],"manifest_sha256":sha(out/'bundle_manifest.json'),"output_dir":str(out)},indent=2))
if __name__=="__main__": main()
