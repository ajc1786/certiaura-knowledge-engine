from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from datetime import datetime, timezone

UAI_RE = re.compile(r"CERT-[A-Z]{3}-\d{6}")
ID_RE = re.compile(r"(?:CLAIM|EVIDENCE|CERT-EKS|CERT-MKS|CERT-SKS|CERT-PKS|CERT-RKS)-[A-Z0-9_-]+", re.I)

def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")

def sha(obj):
    if isinstance(obj, (dict,list)): data=canonical_bytes(obj)
    elif isinstance(obj, bytes): data=obj
    else: data=str(obj).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def discover_sources(repo: Path, mode_terms, max_sources=8, max_excerpt=700):
    roots=[repo/p for p in ["01_Knowledge_Systems","02_Peptides","05_Monitoring","06_Evidence","12_Reports","Standards"]]
    candidates=[]
    for root in roots:
        if not root.exists(): continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in {".md",".json",".csv",".txt"}: continue
            try: text=p.read_text(encoding="utf-8",errors="strict")
            except Exception: continue
            low=text.lower()
            if "retatrutide" not in low: continue
            score=sum(low.count(t.lower()) for t in mode_terms)
            if score <= 0: continue
            excerpt=" ".join(text[:max_excerpt*3].split())[:max_excerpt]
            uai=(UAI_RE.search(text) or UAI_RE.search(p.name))
            ids=ID_RE.findall(text[:5000])
            review=None
            for marker in ["SCIENTIFICALLY_REVIEWED","REVIEWED","BASELINE","DRAFT","INCOMPLETE"]:
                if marker.lower() in low: review=marker; break
            candidates.append((score,str(p.relative_to(repo)).replace("\\","/"),excerpt,uai.group(0) if uai else None,ids[0] if ids else None,review))
    candidates.sort(key=lambda x:(-x[0],x[1]))
    return [{"repository_path":r,"uai":u,"claim_or_evidence_id":i,"review_status":rv,"excerpt":e,"excerpt_sha256":sha(e)} for _,r,e,u,i,rv in candidates[:max_sources]]

import argparse

def validate_profile(d):
    required={"schema_version","patient_reference","journey_phase","clinical_supervision","baseline","monitoring_inputs","symptom_flags","consent"}
    missing=sorted(required-set(d))
    if missing: raise ValueError("Missing required fields: "+", ".join(missing))
    if d["schema_version"]!="1.0.0": raise ValueError("Unsupported schema_version")
    if not re.match(r"^[A-Z0-9_-]{4,40}$",d["patient_reference"]): raise ValueError("patient_reference is not pseudonymous-format compliant")
    if not d["consent"].get("pseudonymised_processing_confirmed"): raise ValueError("Pseudonymised processing confirmation is required")
    if not d["consent"].get("educational_use_acknowledged"): raise ValueError("Educational-use acknowledgement is required")

def render_markdown(r):
    lines=["# Certiaura Retatrutide Patient Journey Report","","> Evidence. Clarity. Confidence.","","## Report control",f"- Report ID: `{r['report_id']}`",f"- Patient reference: `{r['patient_reference']}`",f"- State: `{r['report_state']}`",f"- Generated: `{r['generated_at_utc']}`",f"- Input SHA-256: `{r['input_sha256']}`","","## Scope and boundaries"]
    lines += [f"- {x}" for x in r["scope_notice"]]
    lines += ["","## Baseline context",json.dumps(r["baseline_summary"],indent=2),"","## Journey phase",r["journey_phase"],"","## Monitoring"]
    lines += [f"- Status: {r['monitoring']['status']}"]+[f"- {x.get('repository_path')}: {x.get('source_status')}" for x in r['monitoring']['items']]
    lines += ["","## Safety and contraindication context",f"- Routing: {r['safety']['routing']}"]+[f"- Flag: {x}" for x in r['safety']['flags']]+[f"- Caution: {x}" for x in r['safety']['cautions']]
    lines += ["","## Clinical-outcome context",f"- Status: {r['clinical_outcomes']['status']}"]+[f"- {x.get('repository_path')}" for x in r['clinical_outcomes']['claims']]
    lines += ["","## Uncertainty and missing information"]+[f"- {x}" for x in r['uncertainty']]
    lines += ["","## Clinician-discussion prompts"]+[f"- {x}" for x in r['clinician_discussion_prompts']]
    lines += ["","## Source provenance"]+[f"- `{x['repository_path']}` — {x['source_status']}" for x in r['sources']]
    return "\n".join(lines)+"\n"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("profile"); ap.add_argument("--repository",required=True); ap.add_argument("--output-json",required=True); ap.add_argument("--output-md",required=True); a=ap.parse_args()
    profile=load_json(a.profile); validate_profile(profile); repo=Path(a.repository)
    h=sha(profile); urgent=[x for x in profile["symptom_flags"] if x!="NONE"]
    data=profile["monitoring_inputs"]
    if urgent: state="URGENT_CLINICAL_ROUTING"
    elif not profile["clinical_supervision"]: state="BLOCKED_UNSAFE_OR_UNSUPPORTED"
    elif data["data_completeness"]!="COMPLETE_FOR_BASELINE" or not data["current_medicines_discussed_with_clinician"]: state="CONDITIONAL_MISSING_DATA"
    else: state="READY_FOR_CLINICIAN_DISCUSSION"
    mon=discover_sources(repo,["monitor","safety","adverse","contraindication"],8)
    out=discover_sources(repo,["outcome","trial","endpoint","evidence","weight"],8)
    src=[]
    for s in mon+out:
        if s["repository_path"] not in {x["repository_path"] for x in src}: src.append(s)
    if not src:
        src=[{"repository_path":"Build 0041/0042 canonical retatrutide assets","uai":None,"claim_or_evidence_id":None,"review_status":None,"source_status":"SOURCE_NOT_RESOLVED"}]
    else:
        for s in src: s["source_status"]="RESOLVED"; s.pop("excerpt",None); s.pop("excerpt_sha256",None)
    report={
      "schema_version":"1.0.0","report_id":"RPJ-"+h[:16].upper(),"generated_at_utc":now(),"input_sha256":h,"patient_reference":profile["patient_reference"],"report_state":state,
      "scope_notice":["Retatrutide is treated as investigational in this baseline.","This report is educational and supports clinician discussion; it is not diagnosis, prescribing or dosing advice.","Only canonical repository sources are used; unresolved sources are disclosed rather than invented."],
      "journey_phase":profile["journey_phase"],"baseline_summary":{"age_band":profile["baseline"]["age_band"],"height_cm":profile["baseline"]["height_cm"],"weight_kg":profile["baseline"]["weight_kg"],"goals":profile["baseline"]["goals"],"clinical_supervision":profile["clinical_supervision"]},
      "monitoring":{"status":"SOURCE_RESOLVED" if mon else "SOURCE_NOT_RESOLVED","items":[dict(x,source_status="RESOLVED") for x in mon]},
      "safety":{"routing":"Seek urgent professional assessment now" if urgent else "Routine clinician discussion required","flags":urgent,"cautions":([] if data["current_medicines_discussed_with_clinician"] else ["Current medicines have not been confirmed as discussed with a clinician"])},
      "clinical_outcomes":{"status":"SOURCE_RESOLVED" if out else "SOURCE_NOT_RESOLVED","claims":[dict(x,source_status="RESOLVED") for x in out]},
      "uncertainty":["The engine does not predict an individual response.","Repository evidence and review status may change through living-evidence controls."] + (["Monitoring input is incomplete."] if state=="CONDITIONAL_MISSING_DATA" else []) + (["Routine journey interpretation is suppressed because urgent symptom flags are present."] if urgent else []),
      "clinician_discussion_prompts":["What baseline assessment is clinically appropriate?","Which contraindications or cautions apply to my circumstances?","What monitoring and review schedule is appropriate?","What symptoms require urgent assessment?"],"sources":src
    }
    Path(a.output_json).parent.mkdir(parents=True,exist_ok=True); Path(a.output_json).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    Path(a.output_md).parent.mkdir(parents=True,exist_ok=True); Path(a.output_md).write_text(render_markdown(report),encoding="utf-8")
    print(json.dumps({"valid":True,"report_id":report["report_id"],"report_state":state,"source_count":len(src)},indent=2))
if __name__=="__main__": main()
