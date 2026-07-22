from __future__ import annotations
import argparse, json, sys
from pathlib import Path

REQUIRED={"signal_id","build_provenance","compound","case_count","case_references","classification","human_review_required","autonomous_clinical_action"}
ALLOWED={"NO_SIGNAL","WATCH","ESCALATE","INSUFFICIENT_DATA"}

def validate(data):
    errors=[]
    missing=sorted(REQUIRED-set(data))
    if missing: errors.append("missing fields: "+", ".join(missing))
    if data.get("build_provenance")!="CERT-BUILD-0052": errors.append("build_provenance must be CERT-BUILD-0052")
    if data.get("compound")!="retatrutide": errors.append("compound must be retatrutide")
    refs=data.get("case_references") if isinstance(data.get("case_references"),list) else []
    count=data.get("case_count")
    if not isinstance(count,int) or count<1: errors.append("case_count must be a positive integer")
    if isinstance(count,int) and len(refs)!=count: errors.append("case_count must equal unique case reference count")
    if len(refs)!=len(set(refs)): errors.append("case_references must be unique")
    if data.get("classification") not in ALLOWED: errors.append("invalid classification")
    if data.get("human_review_required") is not True: errors.append("human_review_required must be true")
    if data.get("autonomous_clinical_action") is not False: errors.append("autonomous_clinical_action must be false")
    if data.get("direct_identifiers_present") is not False: errors.append("direct identifiers are prohibited")
    if isinstance(count,int) and count<3 and data.get("classification")!="INSUFFICIENT_DATA": errors.append("cohorts below three must be INSUFFICIENT_DATA")
    if data.get("evidence_feedback_status")=="READY_FOR_REVIEW" and int(data.get("source_count",0))<2: errors.append("READY_FOR_REVIEW requires at least two sources")
    return errors

def main():
    p=argparse.ArgumentParser(); p.add_argument("input"); p.add_argument("--report")
    a=p.parse_args(); data=json.loads(Path(a.input).read_text(encoding="utf-8")); errors=validate(data)
    out={"valid":not errors,"errors":errors,"input":a.input}
    if a.report: Path(a.report).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2)); return 0 if not errors else 1
if __name__=="__main__": sys.exit(main())
