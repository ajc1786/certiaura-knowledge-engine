from __future__ import annotations
import json
from pathlib import Path

BUILD="0060"; CAND="RC1"; PEPTIDE="BPC-157"

def load_json(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def nonempty(value): return isinstance(value,str) and bool(value.strip())
def overlap(a,b): return bool(set(a)&set(b))

def base_errors(d):
 e=[]
 if d.get("build_number")!=BUILD: e.append("build_number")
 if d.get("candidate")!=CAND: e.append("candidate")
 if d.get("peptide")!=PEPTIDE: e.append("peptide")
 if d.get("clinical_recommendation_authorised") is not False: e.append("clinical recommendation prohibited")
 if d.get("clinical_decision_support_authorised") is not False: e.append("clinical decision support prohibited")
 if d.get("tesamorelin_assumptions_transferred") is not False: e.append("Tesamorelin assumptions transferred")
 if not nonempty(d.get("record_id")): e.append("record_id")
 return e

def validate_record(d):
 e=base_errors(d); rt=d.get("record_type")
 if rt=="bpc157_evidence_reconstruction":
  refs=d.get("source_refs",[]); tiers=set(d.get("source_tiers",[])); gaps=d.get("critical_gaps",[])
  if len(refs)<4: e.append("four authoritative source references required")
  if not {"REGULATOR","SPORT_AUTHORITY","TRIAL_REGISTRY"}.issubset(tiers): e.append("mandatory evidence tiers missing")
  if d.get("reconstruction_state")=="COMPLETE_WITH_CRITICAL_GAPS" and not gaps: e.append("critical gaps required")
  if d.get("decision")=="READY_FOR_REVIEW_BOARD" and (d.get("human_evidence_state") in {"ABSENT","VERY_LIMITED"} or d.get("regulatory_evidence_state")!="CLEAR"): e.append("readiness overclaim")
 elif rt=="bpc157_regulatory_sport_boundary":
  if len(d.get("source_refs",[]))<2: e.append("regulatory and sport sources required")
  if d.get("wada_state")!="S0_PROHIBITED_AT_ALL_TIMES": e.append("2026 WADA boundary mismatch")
  if d.get("fda_state")=="PROPOSED_NOT_INCLUDE_503A" and "proposal" not in str(d.get("fda_basis","")).lower() and "briefing" not in str(d.get("fda_basis","")).lower(): e.append("FDA proposal not labelled")
  if d.get("boundary_decision")!="INCOMPLETE" and d.get("human_therapeutic_approval_state")=="UNKNOWN": e.append("approval state unresolved")
 elif rt=="bpc157_human_evidence_gap":
  if d.get("completed_trials_with_results",0)==0 and d.get("human_evidence_state")=="ADEQUATE": e.append("human evidence overclaim")
  if not d.get("critical_gaps") and d.get("human_evidence_state")!="ADEQUATE": e.append("critical gaps missing")
  if d.get("decision")=="READY" and d.get("gap_severity") in {"HIGH","CRITICAL"}: e.append("ready despite severe gaps")
 elif rt=="bpc157_safety_quality_boundary":
  if len(d.get("quality_domains",[]))<4: e.append("quality domains incomplete")
  if not d.get("critical_unknowns"): e.append("critical unknowns required")
  if d.get("boundary_decision")=="CONTROLLED_FOR_SIMULATION_ONLY" and any(d.get(k) in {"CONCERN_IDENTIFIED","UNSTANDARDISED","SOURCE_DEPENDENT","UNKNOWN"} for k in ["immunogenicity_state","impurity_state","formulation_state","manufacturing_state"]): e.append("controlled state overclaim")
 elif rt=="bpc157_review_board_transition":
  roles=d.get("roles",[]); role_names={x.get("role") for x in roles}; ids=[x.get("reviewer_id") for x in roles]
  required={"CHAIR","EVIDENCE_REVIEWER","SAFETY_REVIEWER","REGULATORY_REVIEWER","GOVERNANCE_REVIEWER"}
  if not required.issubset(role_names): e.append("mandatory board roles missing")
  if len(ids)!=len(set(ids)): e.append("duplicate reviewer")
  if not all(x.get("independence_confirmed") is True for x in roles): e.append("independence not confirmed")
  q=d.get("quorum",{})
  if q.get("present",0)<q.get("required",5): e.append("quorum not met")
  if d.get("conflicts_disclosed") is not True: e.append("conflicts not disclosed")
  if d.get("decision")=="APPROVE_ONBOARDING_SIMULATION" and (d.get("regulatory_boundary_state")!="BOUNDARY_COMPLETE_RESTRICTED" or d.get("human_evidence_gap_severity") in {"HIGH","CRITICAL"} or d.get("sport_boundary_state")=="PROHIBITED_AT_ALL_TIMES"): e.append("transition approval violates fail-closed boundaries")
 elif rt=="bpc157_transition_appeal":
  if d.get("independence_confirmed") is not True: e.append("appeal independence")
  if overlap(d.get("original_deciders",[]),d.get("appeal_panel",[])): e.append("appeal panel overlaps original deciders")
  if len(d.get("appeal_panel",[]))<2: e.append("appeal panel")
 elif rt=="multi_peptide_onboarding_readiness":
  if d.get("source_pilot")!="Tesamorelin" or d.get("transition_candidate")!="BPC-157": e.append("transition lineage")
  if len(d.get("reusable_controls",[]))<6 or len(d.get("target_specific_controls",[]))<5: e.append("control coverage")
  if len(d.get("prohibited_transfers",[]))<3: e.append("prohibited transfers")
  if d.get("readiness_state")=="READY" and d.get("decision")!="APPROVE_REPEATABLE_ONBOARDING_MODEL": e.append("readiness decision mismatch")
 elif rt=="certiaura_build_0060_closure_evidence":
  required=["canonical_commit","commit_subject","run_id","workflow_name","run_attempt","branch","event","status","conclusion","actions_url","endpoint","founder_ready_status"]
  for k in required:
   if k not in d or d[k] in (None,""): e.append("closure "+k)
  if d.get("status")!="completed" or d.get("conclusion")!="success": e.append("closure not green")
  if d.get("endpoint")!="BUILD_0060_GITHUB_ACTIONS_GREEN": e.append("closure endpoint")
 else: e.append("unknown record_type")
 return e

def main():
 import argparse
 p=argparse.ArgumentParser(); p.add_argument("record"); a=p.parse_args(); d=load_json(a.record); e=validate_record(d)
 print(json.dumps({"valid":not e,"errors":e},indent=2)); return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
