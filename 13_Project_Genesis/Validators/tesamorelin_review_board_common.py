from __future__ import annotations
import json,re
from pathlib import Path

REQUIRED_ROLES={"CHAIR","EVIDENCE_REVIEWER","SAFETY_REVIEWER","GOVERNANCE_REVIEWER"}
HEX64=re.compile(r"^[0-9a-fA-F]{64}$")
HEX40=re.compile(r"^[0-9a-f]{40}$")

def load_json(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def need(d,keys): return ["missing required field: "+k for k in keys if k not in d]
def base_errors(d,t):
 e=[]
 if d.get("build_number")!="0059": e.append("build_number must be 0059")
 if d.get("candidate")!="RC1": e.append("candidate must be RC1")
 if t!="certiaura_build_0059_closure_evidence":
  if d.get("clinical_recommendation_authorised") is not False: e.append("clinical recommendation must remain false")
  if d.get("clinical_decision_support_authorised") is not False: e.append("clinical decision support must remain false")
  if d.get("peptide")!="Tesamorelin": e.append("peptide must be Tesamorelin")
 return e

def validate_record(d):
 t=d.get("record_type")
 if t is None and "canonical_commit" in d: t="certiaura_build_0059_closure_evidence"
 e=base_errors(d,t)
 if t=="tesamorelin_review_board_decision":
  e+=need(d,["record_id","evidence_pack_id","evidence_pack_version","decision_id","roles","quorum","conflicts_disclosed","decision","rationale","conditions","approvers"])
  roles=d.get("roles",[]); present={x.get("role") for x in roles}; q=d.get("quorum",{})
  if not REQUIRED_ROLES.issubset(present): e.append("mandatory review-board roles missing")
  if any(x.get("independence_confirmed") is not True for x in roles): e.append("all board members must confirm independence")
  if q.get("required",0)<4 or q.get("present",0)<q.get("required",4): e.append("review-board quorum not met")
  if d.get("conflicts_disclosed") is not True: e.append("conflicts must be disclosed")
  if d.get("decision")=="APPROVE_SIMULATION" and any(x.get("vote")!="APPROVE" for x in roles if x.get("role") in REQUIRED_ROLES): e.append("approval requires all mandatory-role votes to approve")
 elif t=="tesamorelin_evidence_pack_version":
  e+=need(d,["record_id","pack_id","version","source_refs","source_hashes","change_summary","immutable_snapshot_hash","validation_state","status","approvers"])
  refs=d.get("source_refs",[]); hashes=d.get("source_hashes",{})
  if len(refs)<2: e.append("evidence pack requires at least two sources")
  if set(refs)!=set(hashes): e.append("source references and source hashes must match exactly")
  if any(not HEX64.match(str(v)) for v in hashes.values()): e.append("each source hash must be SHA-256")
  if not HEX64.match(str(d.get("immutable_snapshot_hash",""))): e.append("immutable snapshot hash must be SHA-256")
  if d.get("status")=="APPROVED" and d.get("validation_state")!="COMPLETE": e.append("approved pack requires complete validation")
 elif t=="tesamorelin_challenge_appeal_decision":
  e+=need(d,["record_id","challenge_id","original_decision_id","challenge_basis","challenger_role","original_deciders","appeal_panel","independence_confirmed","evidence_pack_version","outcome","rationale","audit_refs","approvers"])
  original=set(d.get("original_deciders",[])); panel=set(d.get("appeal_panel",[]))
  if len(panel)<2: e.append("appeal panel requires at least two members")
  if original & panel: e.append("appeal panel must be independent of original deciders")
  if d.get("independence_confirmed") is not True: e.append("appeal independence must be confirmed")
  if not d.get("audit_refs"): e.append("appeal audit reference required")
 elif t=="tesamorelin_suspension_recovery_decision":
  e+=need(d,["record_id","suspension_id","suspension_reason","recovery_criteria","criteria_results","residual_risks","residual_risk_severity","reentry_decision","approvers"])
  criteria=d.get("recovery_criteria",[]); results=d.get("criteria_results",[])
  if len(criteria)<2 or len(results)<2: e.append("at least two recovery criteria and results are required")
  if set(criteria)!={x.get("criterion") for x in results}: e.append("recovery criteria and results must match")
  if d.get("reentry_decision")=="RECOVER_TO_SIMULATION":
   if any(x.get("state")!="MET" for x in results): e.append("recovery requires every criterion to be met")
   if d.get("residual_risk_severity") in {"HIGH","CRITICAL"}: e.append("recovery prohibited with high or critical residual risk")
 elif t=="tesamorelin_periodic_reassessment":
  e+=need(d,["record_id","review_cycle_id","prior_decision_id","due_date","completed_at","evidence_pack_version","new_signals","open_challenges","suspension_state","outcome","next_review_due","approvers"])
  if d.get("outcome")=="CONTINUE" and d.get("open_challenges",0)>0: e.append("unconditional continuation prohibited with open challenges")
  if d.get("outcome")=="CONTINUE" and d.get("suspension_state")!="NONE": e.append("unconditional continuation prohibited during suspension")
  if d.get("suspension_state")=="ACTIVE" and d.get("outcome") not in {"SUSPEND","TERMINATE"}: e.append("active suspension must remain fail-closed")
 elif t=="peptide_review_operating_model_transition":
  e+=need(d,["record_id","transition_id","source_pilot","reusable_controls","peptide_specific_controls","prohibited_assumptions","validation_state","decision","approvers"])
  if len(d.get("reusable_controls",[]))<5: e.append("reusable model requires at least five controls")
  if not d.get("peptide_specific_controls"): e.append("peptide-specific controls must remain separate")
  prohibited={str(x).lower() for x in d.get("prohibited_assumptions",[])}
  if "cross-peptide clinical equivalence" not in prohibited: e.append("cross-peptide clinical equivalence must be prohibited")
  if d.get("decision")=="APPROVE_REUSABLE_MODEL" and d.get("validation_state")!="COMPLETE": e.append("approved reusable model requires complete validation")
 elif t=="certiaura_build_0059_closure_evidence":
  required=["build_number","candidate","title","canonical_commit","commit_subject","run_id","workflow_name","run_attempt","branch","event","status","conclusion","created_at","updated_at","actions_url","local_origin_aligned","repository_clean","git_noninteractive_guard","no_manual_cleanup_prompts","endpoint","founder_ready_status"]
  e+=need(d,required)
  if d.get("title")!="tesamorelin governed review-board approvals, evidence-pack version control, challenge and appeal resolution, suspension recovery, periodic reassessment and reusable peptide-review operating model baseline": e.append("closure title mismatch")
  if not HEX40.match(str(d.get("canonical_commit",""))): e.append("canonical commit must be lowercase 40-character Git SHA")
  if d.get("commit_subject")!="Add Certiaura Build 0059 tesamorelin governed review-board approvals, evidence-pack version control, challenge and appeal resolution, suspension recovery, periodic reassessment and reusable peptide-review operating model baseline": e.append("commit subject mismatch")
  if not str(d.get("run_id","")).isdigit(): e.append("exact Actions run ID required")
  for k,v in {"workflow_name":"Certiaura Repository Validation","branch":"main","event":"push","status":"completed","conclusion":"success","endpoint":"BUILD_0059_GITHUB_ACTIONS_GREEN","founder_ready_status":"BUILD_0059_READY_FOR_FOUNDER_GREEN"}.items():
   if d.get(k)!=v: e.append(k+" mismatch")
  for k in ["local_origin_aligned","repository_clean","git_noninteractive_guard","no_manual_cleanup_prompts"]:
   if d.get(k) is not True: e.append(k+" must be true")
 else: e.append("unsupported record_type")
 return e
