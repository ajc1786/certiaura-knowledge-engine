#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
ALLOWED_EVIDENCE={f"RET-EVD-{i:04d}" for i in range(1,13)}|{"NCT04881760","NCT04867785","NCT06383390","LILLY-TRIUMPH-4-2025"}
REQUIRED={
"safety":"06_Evidence/Retatrutide/RETATRUTIDE_SAFETY_SIGNAL_MATRIX.json",
"monitoring":"05_Monitoring/Retatrutide/RETATRUTIDE_MONITORING_DOMAIN_MATRIX.json",
"event_model":"05_Monitoring/Retatrutide/RETATRUTIDE_MONITORING_EVENT_MODEL.json",
"contra":"01_Knowledge_Systems/SKS/Retatrutide/RETATRUTIDE_CONTRAINDICATION_PRECAUTION_MATRIX.json",
"outcomes":"06_Evidence/Retatrutide/RETATRUTIDE_CLINICAL_OUTCOME_INTEGRATION.json",
"graph":"06_Evidence/Retatrutide/RETATRUTIDE_SAFETY_CLAIM_GRAPH.json",
"sources":"06_Evidence/Retatrutide/RETATRUTIDE_SAFETY_SOURCE_MAP.json"}
PROHIBITED=[r"recommended dose",r"inject yourself",r"self-administer",r"increase the dose",r"approved contraindication"]
def load(root,key):
 p=root/REQUIRED[key]
 if not p.is_file(): raise ValueError(f"Missing required asset: {REQUIRED[key]}")
 return json.loads(p.read_text(encoding="utf-8"))
def validate(root:Path):
 errors=[]
 try:
  safety=load(root,"safety"); mon=load(root,"monitoring"); event=load(root,"event_model"); contra=load(root,"contra"); outcomes=load(root,"outcomes"); graph=load(root,"graph"); sources=load(root,"sources")
 except Exception as exc:return [str(exc)]
 if contra.get("approved_label_exists") is not False: errors.append("approved_label_exists must be false")
 if not any(e.get("category")=="APPROVED_LABEL_CONTRAINDICATIONS" and e.get("status")=="NOT_ESTABLISHED" for e in contra.get("entries",[])): errors.append("No explicit not-established label contraindication entry")
 ids=set(); refs=[]
 for sig in safety.get("signals",[]):
  sid=sig.get("signal_id");
  if not re.fullmatch(r"RET-SAF-\d{3}",str(sid)): errors.append(f"Invalid safety signal id: {sid}")
  if sid in ids: errors.append(f"Duplicate id: {sid}")
  ids.add(sid); refs+=sig.get("evidence_refs",[])
  if not sig.get("clinical_guardrail"): errors.append(f"Missing guardrail: {sid}")
 for dom in mon.get("domains",[]):
  refs+=dom.get("evidence_refs",[])
  if not dom.get("prohibited_output"): errors.append(f"Monitoring domain lacks prohibited output: {dom.get('domain_id')}")
 for e in contra.get("entries",[]): refs+=e.get("evidence_refs",[])
 for o in outcomes.get("outcomes",[]): refs+=o.get("evidence_refs",[])
 bad=sorted(set(refs)-ALLOWED_EVIDENCE-ids)
 if bad: errors.append(f"Unknown evidence or signal references: {bad}")
 if not event.get("prohibited_fields"): errors.append("Monitoring event model lacks prohibited fields")
 all_text=json.dumps([safety,mon,event,contra,outcomes,graph,sources]).lower()
 for pat in PROHIBITED:
  if re.search(pat,all_text): errors.append(f"Prohibited prescriptive phrase detected: {pat}")
 if "investigational" not in all_text or "not approved for public use" not in all_text: errors.append("Investigational status boundary missing")
 if not any(o.get("evidence_status")=="UNRESOLVED_ONGOING_TRIALS" for o in outcomes.get("outcomes",[])): errors.append("Unresolved cardiovascular/renal outcome state missing")
 return errors
def main():
 ap=argparse.ArgumentParser();ap.add_argument("root");ap.add_argument("--report");a=ap.parse_args();errors=validate(Path(a.root));report={"build_number":"0042","valid":not errors,"safety_signal_count":0,"monitoring_domain_count":0,"outcome_count":0,"errors":errors}
 if not errors:
  report["safety_signal_count"]=len(load(Path(a.root),"safety")["signals"]);report["monitoring_domain_count"]=len(load(Path(a.root),"monitoring")["domains"]);report["outcome_count"]=len(load(Path(a.root),"outcomes")["outcomes"])
 if a.report: Path(a.report).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2));return 0 if not errors else 1
if __name__=="__main__":raise SystemExit(main())
