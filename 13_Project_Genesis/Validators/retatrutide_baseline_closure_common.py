from __future__ import annotations
import json
from pathlib import Path

def load_json(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def nonempty_list(value): return isinstance(value,list) and len(value)>0

def validate_record(r):
 e=[]; t=r.get("record_type")
 if r.get("build_number")!="0055": e.append("build_number must be 0055")
 if t=="operational_baseline_closure_decision":
  if r.get("decision") in {"CLOSE_BASELINE","CONDITIONAL_CLOSURE"} and not nonempty_list(r.get("approvers")): e.append("closure requires human approvers")
  if r.get("decision")=="CLOSE_BASELINE" and r.get("open_critical_gaps"): e.append("baseline cannot close with critical gaps")
  if not nonempty_list(r.get("closure_scope")): e.append("closure scope is required")
 elif t=="controlled_release_authorisation":
  if not r.get("closure_decision_id"): e.append("release requires closure decision")
  if r.get("clinical_use_disclaimer") is not True: e.append("clinical-use disclaimer is required")
  if r.get("decision")=="AUTHORISE_CONTROLLED_RELEASE" and (r.get("unresolved_critical_gaps") or not nonempty_list(r.get("approvers"))): e.append("release authorisation requires no critical gaps and human approval")
 elif t=="reusable_architecture_handoff":
  generic=" ".join(map(str,r.get("generic_components",[]))).lower()
  prohibited=["clinical claim","clinical efficacy","monitoring threshold","safety conclusion"]
  if any(x in generic for x in prohibited): e.append("peptide-specific clinical content cannot be generic handoff content")
  if not nonempty_list(r.get("excluded_peptide_specific_components")): e.append("handoff must define excluded peptide-specific components")
  if r.get("handoff_state") in {"APPROVED_FOR_GOVERNED_PILOT","PILOT_ONLY"} and not nonempty_list(r.get("approvers")): e.append("handoff requires human approval")
 elif t=="next_peptide_pilot_selection":
  if r.get("clinical_equivalence_claimed") is not False: e.append("clinical equivalence is prohibited")
  if not nonempty_list(r.get("candidate_assessments")): e.append("candidate assessments are required")
  if r.get("decision") in {"SELECT_GOVERNED_PILOT","CONDITIONAL_PILOT"}:
   if not r.get("selected_peptide"): e.append("selected peptide is required")
   if not nonempty_list(r.get("approvers")): e.append("pilot selection requires human approval")
   selected=[x for x in r.get("candidate_assessments",[]) if x.get("peptide")==r.get("selected_peptide")]
   if not selected: e.append("selected peptide must appear in candidate assessments")
   else:
    s=selected[0]
    if s.get("evidence_mapping_state") in {"NONE","INSUFFICIENT"}: e.append("selected pilot lacks evidence mapping readiness")
    if s.get("safety_boundary_state") in {"NONE","INCOMPLETE"} and r.get("decision")=="SELECT_GOVERNED_PILOT": e.append("selected pilot lacks safety-boundary readiness")
 elif t=="baseline_exception_reopening_decision":
  if r.get("decision")=="REOPEN_CONTROLLED_SCOPE":
   if not r.get("trigger_type") or not nonempty_list(r.get("trigger_evidence")): e.append("reopening requires evidenced trigger")
   if not nonempty_list(r.get("affected_baseline_components")): e.append("reopening requires affected scope")
   if not nonempty_list(r.get("approvers")): e.append("reopening requires human approval")
 else: e.append("unsupported record_type")
 return e

def validate_bundle(records):
 e=[]; by={r.get("record_type"):r for r in records}; needed={"operational_baseline_closure_decision","controlled_release_authorisation","reusable_architecture_handoff","next_peptide_pilot_selection","baseline_exception_reopening_decision"}
 for x in sorted(needed-set(by)): e.append(f"bundle missing {x}")
 for r in records: e.extend(validate_record(r))
 close=by.get("operational_baseline_closure_decision",{}); release=by.get("controlled_release_authorisation",{}); handoff=by.get("reusable_architecture_handoff",{})
 if release.get("decision")=="AUTHORISE_CONTROLLED_RELEASE" and close.get("decision")!="CLOSE_BASELINE": e.append("release requires fully closed baseline")
 if handoff.get("handoff_state")=="APPROVED_FOR_GOVERNED_PILOT" and close.get("decision")!="CLOSE_BASELINE": e.append("approved handoff requires fully closed baseline")
 return e
