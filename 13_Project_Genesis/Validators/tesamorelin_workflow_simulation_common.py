from __future__ import annotations
import json,re
from pathlib import Path

def load_json(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def nonempty(value): return isinstance(value,list) and len(value)>0
def validate_record(r):
    e=[]; t=r.get("record_type")
    if r.get("build_number")!="0057": e.append("build_number must be 0057")
    if r.get("peptide")!="Tesamorelin": e.append("peptide must be Tesamorelin")
    if r.get("clinical_recommendation_authorised") is not False: e.append("clinical recommendation is not authorised")
    if r.get("clinical_decision_support_authorised") is not False: e.append("clinical decision support is not authorised")
    if t=="tesamorelin_evidence_ingestion_record":
        if not r.get("source_id"): e.append("source id is required")
        if not r.get("source_locator"): e.append("source locator is required")
        if not re.fullmatch(r"[0-9a-f]{64}",str(r.get("source_sha256",""))): e.append("source sha256 must be 64 lowercase hex characters")
        if not nonempty(r.get("evidence_scope")): e.append("evidence scope is required")
        scope=" ".join(map(str,r.get("evidence_scope",[]))).lower()
        for term in ["guaranteed treatment","prescribe","dose recommendation"]:
            if term in scope: e.append("unsupported clinical claim in evidence scope")
        if r.get("decision")=="ACCEPT_FOR_SIMULATION":
            if r.get("provenance_state")!="VERIFIED": e.append("accepted ingestion requires verified provenance")
            if r.get("open_gaps"): e.append("accepted ingestion cannot retain open gaps")
            if not nonempty(r.get("approvers")): e.append("accepted ingestion requires human approval")
    elif t=="tesamorelin_monitoring_workflow_event":
        if not r.get("ingestion_record_id"): e.append("ingestion record link is required")
        if not nonempty(r.get("observations")): e.append("observations are required")
        if "no autonomous" not in str(r.get("automation_limit","")).lower(): e.append("autonomous clinical decisions must be prohibited")
        if r.get("event_type")=="SAFETY_SIGNAL" and r.get("action")!="STOP_AND_ESCALATE": e.append("safety signal must stop and escalate")
        if r.get("data_quality")=="INSUFFICIENT" and r.get("action") not in {"DO_NOT_ADVANCE","HOLD_AND_REVIEW"}: e.append("insufficient data cannot advance")
        if not nonempty(r.get("approvers")): e.append("monitoring event requires human review")
    elif t=="tesamorelin_safety_escalation_decision":
        if not r.get("signal_id"): e.append("signal id is required")
        if not nonempty(r.get("evidence_refs")): e.append("safety evidence references are required")
        if not r.get("route"): e.append("safety route is required")
        if r.get("severity")=="CRITICAL":
            if r.get("decision")!="STOP_AND_ESCALATE": e.append("critical signal must stop and escalate")
            if r.get("emergency_route") is not True: e.append("critical signal requires emergency route")
        if not nonempty(r.get("approvers")): e.append("safety decision requires human approval")
    elif t=="tesamorelin_simulation_acceptance_decision":
        if not nonempty(r.get("prohibited_scope")): e.append("prohibited scope is required")
        if r.get("decision")=="ACCEPT_SIMULATION_BASELINE":
            if int(r.get("ingested_source_count",0))<3: e.append("acceptance requires at least three ingested sources")
            if r.get("verified_source_count")!=r.get("ingested_source_count"): e.append("all ingested sources must be verified")
            if r.get("open_critical_gaps"): e.append("acceptance cannot have critical gaps")
            if r.get("unresolved_safety_signals"): e.append("acceptance cannot have unresolved safety signals")
            if r.get("workflow_replay_state")!="COMPLETE": e.append("acceptance requires complete workflow replay")
            if r.get("audit_trail_complete") is not True: e.append("acceptance requires complete audit trail")
            if not nonempty(r.get("approvers")): e.append("acceptance requires human approval")
            text=" ".join(map(str,r.get("prohibited_scope",[]))).lower()
            for term in ["clinical recommendation","dosing","diagnosis","prescribing"]:
                if term not in text: e.append("prohibited scope must include "+term)
    else: e.append("unsupported record_type")
    return e

def validate_bundle(records):
    e=[]; by={x.get("record_type"):x for x in records}
    req={"tesamorelin_evidence_ingestion_record","tesamorelin_monitoring_workflow_event","tesamorelin_safety_escalation_decision","tesamorelin_simulation_acceptance_decision"}
    for x in sorted(req-set(by)): e.append("bundle missing "+x)
    for r in records: e.extend(validate_record(r))
    a=by.get("tesamorelin_simulation_acceptance_decision",{})
    if a.get("decision")=="ACCEPT_SIMULATION_BASELINE":
        if by.get("tesamorelin_evidence_ingestion_record",{}).get("decision")!="ACCEPT_FOR_SIMULATION": e.append("accepted simulation requires accepted ingestion")
        if by.get("tesamorelin_monitoring_workflow_event",{}).get("action")!="CONTINUE_SIMULATION": e.append("accepted simulation requires completed monitoring route")
        if by.get("tesamorelin_safety_escalation_decision",{}).get("severity")=="CRITICAL": e.append("accepted simulation bundle cannot contain active critical signal")
    return e
