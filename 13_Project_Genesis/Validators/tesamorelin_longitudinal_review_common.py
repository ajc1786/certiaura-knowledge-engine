from __future__ import annotations
import json
from pathlib import Path

def load_json(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def nonempty(value): return isinstance(value,list) and len(value)>0
def validate_record(r):
    e=[]; t=r.get("record_type")
    if r.get("build_number")!="0058": e.append("build_number must be 0058")
    if r.get("peptide")!="Tesamorelin": e.append("peptide must be Tesamorelin")
    if r.get("clinical_recommendation_authorised") is not False: e.append("clinical recommendation is not authorised")
    if r.get("clinical_decision_support_authorised") is not False: e.append("clinical decision support is not authorised")
    if not r.get("record_id"): e.append("record_id is required")
    if t=="tesamorelin_source_quality_assessment":
        sources=r.get("source_assessments",[])
        if not isinstance(sources,list) or len(sources)<2: e.append("at least two source assessments are required")
        ids=[x.get("source_id") for x in sources if isinstance(x,dict)]
        if len(ids)!=len(set(ids)): e.append("source identifiers must be unique")
        for x in sources:
            if not isinstance(x,dict): e.append("source assessment must be an object"); continue
            if not x.get("source_id"): e.append("source id is required")
            score=x.get("quality_score")
            if not isinstance(score,int) or not 0<=score<=100: e.append("quality score must be 0 to 100")
            if x.get("relevance_state")=="OUT_OF_SCOPE" and x.get("evidence_position")!="NEUTRAL": e.append("out-of-scope evidence must be neutral")
        if r.get("decision")=="ACCEPT_FOR_REVIEW":
            if len(sources)<3: e.append("acceptance requires at least three sources")
            if any(x.get("provenance_state")!="VERIFIED" for x in sources if isinstance(x,dict)): e.append("accepted sources require verified provenance")
            if any(x.get("relevance_state")=="OUT_OF_SCOPE" for x in sources if isinstance(x,dict)): e.append("out-of-scope evidence cannot be accepted")
            if int(r.get("aggregate_score",0))<70: e.append("acceptance requires aggregate score of at least 70")
            if any(int(x.get("quality_score",0))<50 for x in sources if isinstance(x,dict)): e.append("acceptance cannot include a source below 50")
            if r.get("critical_quality_gaps"): e.append("acceptance cannot retain critical quality gaps")
            if not nonempty(r.get("approvers")): e.append("acceptance requires human approval")
    elif t=="tesamorelin_conflicting_evidence_decision":
        if not r.get("assessment_record_id"): e.append("assessment link is required")
        if not r.get("conflict_id"): e.append("conflict id is required")
        if r.get("decision")=="RESOLVED_FOR_SIMULATION":
            if not nonempty(r.get("supporting_source_ids")): e.append("resolved conflict requires supporting sources")
            if not nonempty(r.get("contradicting_source_ids")): e.append("resolved conflict requires contradicting sources")
            if r.get("adjudication_method")!="HUMAN_REVIEW": e.append("resolved conflict requires human review")
            if not str(r.get("rationale","")).strip(): e.append("resolved conflict requires rationale")
            if r.get("conflict_severity") in {"HIGH","CRITICAL"}: e.append("high or critical conflict cannot be resolved for simulation")
            if not nonempty(r.get("approvers")): e.append("resolved conflict requires human approval")
        if r.get("conflict_severity")=="CRITICAL" and r.get("decision")=="RESOLVED_FOR_SIMULATION": e.append("critical conflict must remain held or rejected")
    elif t=="tesamorelin_longitudinal_signal_review":
        count=r.get("occurrence_count",0); state=r.get("recurrence_state")
        if not nonempty(r.get("event_ids")): e.append("event identifiers are required")
        if not nonempty(r.get("evidence_refs")): e.append("evidence references are required")
        if state=="FIRST_OCCURRENCE" and count!=1: e.append("first occurrence count must equal one")
        if state=="ISOLATED_REPEAT" and count!=2: e.append("isolated repeat count must equal two")
        if state=="RECURRENT" and count<3: e.append("recurrent signal requires at least three occurrences")
        if state=="PERSISTENT" and count<4: e.append("persistent signal requires at least four occurrences")
        if r.get("severity")=="CRITICAL" and r.get("action")!="SUSPEND_PILOT": e.append("critical signal must suspend the pilot")
        if state in {"RECURRENT","PERSISTENT"} and r.get("severity") in {"HIGH","CRITICAL"} and r.get("action") not in {"HOLD_AND_ESCALATE","SUSPEND_PILOT"}: e.append("recurrent high-severity signal must hold or suspend")
        if not nonempty(r.get("approvers")): e.append("longitudinal review requires human approval")
    elif t=="tesamorelin_controlled_amendment_decision":
        if not r.get("amendment_id"): e.append("amendment id is required")
        if not nonempty(r.get("trigger_record_ids")): e.append("amendment triggers are required")
        if r.get("decision")=="APPROVE_FOR_SIMULATION":
            if r.get("current_version")==r.get("proposed_version"): e.append("approved amendment requires a new version")
            if not nonempty(r.get("changed_controls")): e.append("approved amendment requires changed controls")
            if r.get("validation_state")!="COMPLETE": e.append("approved amendment requires complete validation")
            if not str(r.get("rollback_plan","")).strip(): e.append("approved amendment requires rollback plan")
            if not nonempty(r.get("approvers")): e.append("approved amendment requires human approval")
    elif t=="tesamorelin_pilot_continuation_decision":
        prohibited=" ".join(map(str,r.get("prohibited_scope",[]))).lower()
        for term in ["clinical recommendation","dosing","diagnosis","prescribing"]:
            if term not in prohibited: e.append("prohibited scope must include "+term)
        if r.get("decision")=="CONTINUE_PILOT":
            if r.get("source_quality_state")!="ACCEPTABLE": e.append("continuation requires acceptable source quality")
            if int(r.get("unresolved_conflicts",0))!=0: e.append("continuation requires zero unresolved conflicts")
            if int(r.get("recurrent_signals",0))!=0: e.append("continuation requires zero uncontrolled recurrent signals")
            if r.get("open_critical_gaps"): e.append("continuation cannot have critical gaps")
            if r.get("amendment_state") not in {"NOT_REQUIRED","VALIDATED"}: e.append("continuation requires no pending or failed amendment")
            if r.get("audit_replay_state")!="COMPLETE": e.append("continuation requires complete audit replay")
            if not nonempty(r.get("approvers")): e.append("continuation requires human approval")
        if r.get("decision")=="CONTINUE_WITH_CONDITIONS" and not nonempty(r.get("conditions")): e.append("conditional continuation requires conditions")
        if r.get("open_critical_gaps") and r.get("decision") not in {"SUSPEND_PILOT","TERMINATE_PILOT"}: e.append("critical gaps require suspension or termination")
    else: e.append("unsupported record_type")
    return e

def validate_bundle(records):
    e=[]; by={x.get("record_type"):x for x in records}
    req={"tesamorelin_source_quality_assessment","tesamorelin_conflicting_evidence_decision","tesamorelin_longitudinal_signal_review","tesamorelin_controlled_amendment_decision","tesamorelin_pilot_continuation_decision"}
    for x in sorted(req-set(by)): e.append("bundle missing "+x)
    for r in records: e.extend(validate_record(r))
    p=by.get("tesamorelin_pilot_continuation_decision",{})
    if p.get("decision")=="CONTINUE_PILOT":
        if by.get("tesamorelin_source_quality_assessment",{}).get("decision")!="ACCEPT_FOR_REVIEW": e.append("continued pilot requires accepted source quality")
        if by.get("tesamorelin_conflicting_evidence_decision",{}).get("decision")!="RESOLVED_FOR_SIMULATION": e.append("continued pilot requires resolved conflict state")
        signal=by.get("tesamorelin_longitudinal_signal_review",{})
        if signal.get("action") not in {"CONTINUE_MONITORING","AMEND_AND_MONITOR"}: e.append("continued pilot requires controlled signal action")
        if signal.get("action")=="AMEND_AND_MONITOR" and by.get("tesamorelin_controlled_amendment_decision",{}).get("decision")!="APPROVE_FOR_SIMULATION": e.append("amend-and-monitor route requires approved amendment")
    return e
