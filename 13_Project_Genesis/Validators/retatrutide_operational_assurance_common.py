from __future__ import annotations
import json
from pathlib import Path
from typing import Any
REQUIRED=("record_type","build_number","created_at","created_by","peptide_uai","assessment_id")
def load_json(path:str|Path)->dict[str,Any]: return json.loads(Path(path).read_text(encoding="utf-8"))
def nonempty_list(v:Any)->bool: return isinstance(v,list) and len(v)>0
def validate_record(r:dict[str,Any])->list[str]:
 e=[]
 for f in REQUIRED:
  if f not in r or r[f] in (None,""): e.append(f"missing required field: {f}")
 if r.get("build_number")!="0054": e.append("build_number must be 0054")
 if r.get("peptide_uai")!="CERT-PKS-000001": e.append("peptide_uai must be CERT-PKS-000001")
 t=r.get("record_type")
 if t=="operational_assurance_assessment":
  domains=r.get("coverage_domains",[]); flows=r.get("end_to_end_workflows",[]); gaps=r.get("open_critical_gaps",[]); result=r.get("overall_result")
  if len(domains)<8: e.append("operational assurance requires at least 8 coverage domains")
  if not nonempty_list(flows): e.append("at least one end-to-end workflow is required")
  if result not in {"PASS","CONDITIONAL","FAIL"}: e.append("invalid overall_result")
  if result=="PASS" and gaps: e.append("PASS cannot contain open critical gaps")
  if not str(r.get("human_approver","")).strip(): e.append("human approval is required")
 elif t=="failure_mode_coverage_assessment":
  modes=r.get("failure_modes",[]); overall=r.get("overall_coverage")
  if not nonempty_list(modes): e.append("failure_modes are required")
  bad=False
  for m in modes if isinstance(modes,list) else []:
   for f in ("failure_mode_id","trigger","detection_control","containment_control","rollback_control","test_evidence","coverage_status"):
    if not m.get(f): e.append(f"failure mode missing {f}")
   if m.get("coverage_status")!="COVERED": bad=True
  if overall=="PASS" and bad: e.append("PASS requires every failure mode COVERED")
  if overall not in {"PASS","CONDITIONAL","FAIL"}: e.append("invalid overall_coverage")
  if not str(r.get("human_approver","")).strip(): e.append("human approval is required")
 elif t=="platinum_readiness_assessment":
  dims=r.get("dimensions",[]); score=r.get("overall_score"); gaps=r.get("critical_gaps",[]); state=r.get("readiness_state")
  if not nonempty_list(dims): e.append("dimensions are required")
  for d in dims if isinstance(dims,list) else []:
   if not d.get("evidence_links"): e.append("every Platinum dimension requires evidence links")
   if not isinstance(d.get("score"),(int,float)) or not 0<=d.get("score")<=5: e.append("dimension score must be 0-5")
  if state=="PLATINUM_READY" and (not isinstance(score,(int,float)) or score<4.5): e.append("PLATINUM_READY requires score at least 4.5")
  if state=="PLATINUM_READY" and gaps: e.append("critical gaps override Platinum score")
  if state not in {"PLATINUM_READY","CONDITIONAL","NOT_READY"}: e.append("invalid readiness_state")
  if not str(r.get("human_approver","")).strip(): e.append("human approval is required")
 elif t=="controlled_release_readiness_decision":
  for f in ("assurance_assessment_id","failure_mode_assessment_id","platinum_assessment_id","platinum_state","unresolved_critical_gaps","evidence_links","decision","approvers"):
   if f not in r: e.append(f"missing required field: {f}")
  if r.get("decision")=="RELEASE":
   if r.get("platinum_state")!="PLATINUM_READY": e.append("RELEASE requires PLATINUM_READY")
   if r.get("unresolved_critical_gaps"): e.append("RELEASE cannot contain unresolved critical gaps")
   if len(r.get("approvers",[]))<2: e.append("RELEASE requires two human approvers")
   if not r.get("evidence_links"): e.append("RELEASE requires evidence links")
  if r.get("decision") not in {"RELEASE","HOLD","REMEDIATE"}: e.append("invalid release decision")
 elif t=="architecture_reuse_decision":
  for f in ("source_baseline_build","source_readiness_state","target_peptide","decision","reusable_components","excluded_components","prerequisites","approvers"):
   if f not in r: e.append(f"missing required field: {f}")
  if r.get("source_baseline_build")!="0054": e.append("source_baseline_build must be 0054")
  if r.get("decision")=="APPROVE_REUSE":
   if r.get("source_readiness_state")!="PLATINUM_READY": e.append("APPROVE_REUSE requires PLATINUM_READY")
   if r.get("prerequisites"): e.append("APPROVE_REUSE requires no open prerequisites")
   if len(r.get("approvers",[]))<2: e.append("APPROVE_REUSE requires two approvers")
  if r.get("decision") not in {"APPROVE_REUSE","PILOT_ONLY","DO_NOT_REUSE"}: e.append("invalid architecture reuse decision")
 else: e.append("unsupported record_type")
 return e
def validate_bundle(records:list[dict[str,Any]])->list[str]:
 e=[]; by={r.get("record_type"):r for r in records}
 needed={"operational_assurance_assessment","failure_mode_coverage_assessment","platinum_readiness_assessment","controlled_release_readiness_decision","architecture_reuse_decision"}
 missing=sorted(needed-set(by)); e += [f"bundle missing {x}" for x in missing]
 for r in records: e += validate_record(r)
 rel=by.get("controlled_release_readiness_decision",{})
 if rel.get("decision")=="RELEASE" and by.get("platinum_readiness_assessment",{}).get("readiness_state")!="PLATINUM_READY": e.append("release decision conflicts with Platinum assessment")
 reuse=by.get("architecture_reuse_decision",{})
 if reuse.get("decision")=="APPROVE_REUSE" and rel.get("decision")!="RELEASE": e.append("architecture reuse approval requires controlled release")
 return e
