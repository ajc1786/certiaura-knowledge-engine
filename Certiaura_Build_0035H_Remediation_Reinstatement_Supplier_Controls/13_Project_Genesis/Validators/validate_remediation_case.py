#!/usr/bin/env python3
"""Semantic validator for CERT-BUILD-0035H remediation cases. Standard library only."""
from __future__ import annotations
import argparse, importlib.util, json, re
from datetime import datetime
from pathlib import Path
from typing import Any

HEX64=re.compile(r'^[0-9a-fA-F]{64}$')
CASE_ID=re.compile(r'^PPS-REM-[A-Z0-9-]{3,80}$')
PASSPORT_ID=re.compile(r'^PPS-PAS-[A-Z0-9-]{3,80}$')
SUPPLIER_ID=re.compile(r'^PPS-SUP-[A-Z0-9-]{3,80}$')
ALERT_ID=re.compile(r'^PPS-ALT-[A-Z0-9-]{3,80}$')
ACTIVE_PASSPORT={'PUBLISHED','PARTIALLY_PUBLISHED'}
ACTIVE_MARKET={'ELIGIBLE','CONDITIONALLY_ELIGIBLE'}
CLOSED_ALERTS={'CLOSED_RESOLVED','CLOSED_SUPERSEDED','CLOSED_NO_REINSTATEMENT'}
APPROVED_REVIEW={'REINSTATEMENT_APPROVED','CONDITIONAL_REINSTATEMENT'}

HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
ENGINE=ROOT/'13_Project_Genesis'/'Automation'/'assess_remediation_case.py'
spec=importlib.util.spec_from_file_location('assessment_engine',ENGINE)
assessment_engine=importlib.util.module_from_spec(spec); spec.loader.exec_module(assessment_engine)


def dt(v):
    if not isinstance(v,str): return None
    try: return datetime.fromisoformat(v.replace('Z','+00:00'))
    except ValueError: return None

def req(obj,key,path,e):
    v=obj.get(key)
    if not isinstance(v,str) or not v.strip(): e.append(f'{path}.{key}: non-empty string required')
    return v

def valid_hash(v): return isinstance(v,str) and bool(HEX64.fullmatch(v))

def validate(data:Any)->list[str]:
    e=[]
    if not isinstance(data,dict): return ['root: object required']
    if data.get('schema_version')!='1.0.0': e.append('schema_version: must be 1.0.0')
    c=data.get('case') if isinstance(data.get('case'),dict) else {}; 
    if not c: e.append('case: object required')
    if not CASE_ID.fullmatch(str(c.get('case_id',''))): e.append('case.case_id: invalid')
    if not PASSPORT_ID.fullmatch(str(c.get('passport_id',''))): e.append('case.passport_id: invalid')
    if not SUPPLIER_ID.fullmatch(str(c.get('supplier_id',''))): e.append('case.supplier_id: invalid')
    if not re.fullmatch(r'\d+\.\d+\.\d+',str(c.get('passport_version',''))): e.append('case.passport_version: semantic version required')
    if not valid_hash(c.get('source_record_sha256')): e.append('case.source_record_sha256: 64 hex characters required')
    alerts=c.get('source_alert_ids')
    if not isinstance(alerts,list) or not alerts: e.append('case.source_alert_ids: non-empty array required'); alerts=[]
    if len(alerts)!=len(set(map(str,alerts))): e.append('case.source_alert_ids: duplicates prohibited')
    for i,a in enumerate(alerts):
        if not isinstance(a,str) or not ALERT_ID.fullmatch(a): e.append(f'case.source_alert_ids[{i}]: invalid')
    if c.get('severity') not in {'LOW','MEDIUM','HIGH','CRITICAL'}: e.append('case.severity: invalid')
    if c.get('priority') not in {'P0','P1','P2','P3','P4'}: e.append('case.priority: invalid')
    if c.get('severity')=='CRITICAL' and c.get('priority')!='P0': e.append('case.priority: CRITICAL requires P0')
    states={'OPEN','PLAN_REQUIRED','REMEDIATION_IN_PROGRESS','EVIDENCE_REFRESH_PENDING','UNDER_REVIEW','REINSTATEMENT_READY','PARTIALLY_REINSTATED','REINSTATED','CLOSED_NO_REINSTATEMENT','ESCALATED','REJECTED'}
    if c.get('status') not in states: e.append('case.status: invalid')
    for k in ['opened_at','target_due_at']:
        if not dt(c.get(k)): e.append(f'case.{k}: valid date-time required')
    req(c,'owner','case',e)
    roots=c.get('root_cause_codes')
    if not isinstance(roots,list) or not roots: e.append('case.root_cause_codes: non-empty array required')
    if not isinstance(c.get('repeat_failure_count'),int) or c.get('repeat_failure_count',-1)<0: e.append('case.repeat_failure_count: non-negative integer required')
    if c.get('legal_hold') not in {True,False}: e.append('case.legal_hold: boolean required')
    if c.get('data_integrity_hold') not in {True,False}: e.append('case.data_integrity_hold: boolean required')

    cap=data.get('corrective_action_plan') if isinstance(data.get('corrective_action_plan'),dict) else {}; 
    if not cap: e.append('corrective_action_plan: object required')
    actions=cap.get('actions') if isinstance(cap.get('actions'),list) else []
    seen_actions=set()
    for i,a in enumerate(actions):
        p=f'corrective_action_plan.actions[{i}]'
        if not isinstance(a,dict): e.append(f'{p}: object required'); continue
        aid=req(a,'action_id',p,e)
        if aid in seen_actions: e.append(f'{p}.action_id: duplicate')
        seen_actions.add(aid)
        if a.get('status') not in {'NOT_STARTED','IN_PROGRESS','COMPLETED','OVERDUE','CANCELLED'}: e.append(f'{p}.status: invalid')
        if not dt(a.get('due_at')): e.append(f'{p}.due_at: valid date-time required')
        if a.get('critical') is True and a.get('status')=='COMPLETED':
            if not a.get('completion_evidence_ids'): e.append(f'{p}: critical completion requires objective evidence')
            if a.get('effectiveness_result')!='PASS': e.append(f'{p}: critical completion requires effectiveness PASS')
            if not a.get('effectiveness_reviewer_id') or not dt(a.get('effectiveness_reviewed_at')): e.append(f'{p}: critical completion requires effectiveness reviewer and date')

    refresh=data.get('evidence_refresh') if isinstance(data.get('evidence_refresh'),dict) else {}; 
    if not refresh: e.append('evidence_refresh: object required')
    items=refresh.get('evidence_items') if isinstance(refresh.get('evidence_items'),list) else []
    seen_evidence=set(); verified_mandatory=0
    for i,x in enumerate(items):
        p=f'evidence_refresh.evidence_items[{i}]'
        if not isinstance(x,dict): e.append(f'{p}: object required'); continue
        eid=req(x,'evidence_id',p,e)
        if eid in seen_evidence: e.append(f'{p}.evidence_id: duplicate')
        seen_evidence.add(eid)
        if not valid_hash(x.get('sha256')): e.append(f'{p}.sha256: 64 hex characters required')
        if x.get('review_status') not in {'PENDING','VERIFIED','REJECTED','QUARANTINED'}: e.append(f'{p}.review_status: invalid')
        if x.get('review_status')=='VERIFIED':
            verified_mandatory+=1
            if not x.get('reviewer_id') or not dt(x.get('reviewed_at')): e.append(f'{p}: verified evidence requires reviewer and review date')
        if x.get('batch_specific') is True and not x.get('batch_id'): e.append(f'{p}.batch_id: required for batch-specific evidence')
    if refresh.get('verified_mandatory_count')!=verified_mandatory: e.append(f'evidence_refresh.verified_mandatory_count: expected {verified_mandatory}')
    if refresh.get('all_critical_evidence_verified') is True:
        if refresh.get('status')!='VERIFIED': e.append('evidence_refresh.status: all critical verified requires VERIFIED status')
        if any(x.get('critical') is True and x.get('review_status')!='VERIFIED' for x in items): e.append('evidence_refresh.all_critical_evidence_verified: contradicted by item status')

    review=data.get('review') if isinstance(data.get('review'),dict) else {}; 
    if not review: e.append('review: object required')
    if review.get('decision') not in {'NOT_STARTED','REINSTATEMENT_APPROVED','CONDITIONAL_REINSTATEMENT','MORE_INFORMATION_REQUIRED','REMEDIATION_REJECTED','ESCALATE'}: e.append('review.decision: invalid')
    if review.get('decision') in APPROVED_REVIEW:
        if review.get('primary_reviewer_conflict_free') is not True: e.append('review.primary_reviewer_conflict_free: true required for approval')
        if not review.get('primary_reviewer_id') or not dt(review.get('reviewed_at')): e.append('review: approved decision requires primary reviewer and date')
        if review.get('second_approval_decision')!='APPROVED' or not review.get('second_approver_id') or not dt(review.get('second_approval_at')): e.append('review: approved decision requires independent second approval')
        if review.get('primary_reviewer_id')==review.get('second_approver_id'): e.append('review: primary and second approver must differ')
        if review.get('residual_risk') in {None,'','NOT_ASSESSED','CRITICAL'}: e.append('review.residual_risk: acceptable assessed residual risk required')
        if not dt(review.get('effective_until')): e.append('review.effective_until: valid date-time required for approval')

    rein=data.get('reinstatement') if isinstance(data.get('reinstatement'),dict) else {}; 
    if not rein: e.append('reinstatement: object required')
    if rein.get('automatic_positive_action') is not False: e.append('reinstatement.automatic_positive_action: must be false')
    pp=rein.get('passport') if isinstance(rein.get('passport'),dict) else {}
    mp=rein.get('marketplace') if isinstance(rein.get('marketplace'),dict) else {}
    if pp.get('decision') not in {'NOT_REQUESTED','PENDING','APPROVED','CONDITIONAL','REJECTED'}: e.append('reinstatement.passport.decision: invalid')
    if mp.get('decision') not in {'NOT_REQUESTED','PENDING','APPROVED','CONDITIONAL','REJECTED'}: e.append('reinstatement.marketplace.decision: invalid')
    if pp.get('decision') in {'APPROVED','CONDITIONAL'}:
        if c.get('legal_hold') or c.get('data_integrity_hold'): e.append('reinstatement.passport: holds prohibit approval')
        if review.get('decision') not in APPROVED_REVIEW: e.append('reinstatement.passport: approved review required')
        for k in ['transaction_id','executed_by','executed_at','before_state_sha256','after_state_sha256']:
            v=pp.get(k)
            if k.endswith('sha256'):
                if not valid_hash(v): e.append(f'reinstatement.passport.{k}: valid hash required')
            elif k=='executed_at':
                if not dt(v): e.append('reinstatement.passport.executed_at: valid date-time required')
            elif not isinstance(v,str) or not v.strip(): e.append(f'reinstatement.passport.{k}: required')
    if mp.get('decision') in {'APPROVED','CONDITIONAL'}:
        if pp.get('decision') not in {'APPROVED','CONDITIONAL'} or pp.get('target_state') not in ACTIVE_PASSPORT: e.append('reinstatement.marketplace: active passport decision required first')
        for k in ['transaction_id','executed_by','executed_at']:
            if k=='executed_at':
                if not dt(mp.get(k)): e.append('reinstatement.marketplace.executed_at: valid date-time required')
            elif not isinstance(mp.get(k),str) or not mp.get(k).strip(): e.append(f'reinstatement.marketplace.{k}: required')
        if mp.get('listing_acknowledged') is not True: e.append('reinstatement.marketplace.listing_acknowledged: true required')

    closures=data.get('alert_closure') if isinstance(data.get('alert_closure'),list) else []
    mapped={}
    for i,x in enumerate(closures):
        p=f'alert_closure[{i}]'
        if not isinstance(x,dict): e.append(f'{p}: object required'); continue
        aid=x.get('alert_id'); mapped[aid]=x
        if aid not in alerts: e.append(f'{p}.alert_id: not a source alert')
        if x.get('decision') not in {'CLOSED_RESOLVED','CLOSED_SUPERSEDED','CLOSED_NO_REINSTATEMENT','REMAINS_OPEN','ESCALATED'}: e.append(f'{p}.decision: invalid')
        if x.get('decision') in CLOSED_ALERTS:
            if not x.get('closed_by') or not dt(x.get('closed_at')): e.append(f'{p}: closed decision requires closer and date')
            req(x,'reason',p,e)
            if x.get('residual_risk') in {None,'','NOT_ASSESSED'}: e.append(f'{p}.residual_risk: assessment required')
    if set(mapped)!=set(alerts): e.append('alert_closure: must reconcile exactly to source alerts')
    if c.get('status') in {'REINSTATED','PARTIALLY_REINSTATED'} and any(mapped.get(a,{}).get('decision') not in CLOSED_ALERTS for a in alerts): e.append('case.status: reinstatement requires source-alert closure')

    perf=data.get('supplier_performance') if isinstance(data.get('supplier_performance'),dict) else {}; 
    if not perf: e.append('supplier_performance: object required')
    deductions=perf.get('component_deductions') if isinstance(perf.get('component_deductions'),dict) else {}
    total=max(0,100-sum(v for v in deductions.values() if isinstance(v,(int,float))))
    if perf.get('score')!=total: e.append(f'supplier_performance.score: expected {total}')
    tier='A' if total>=90 else 'B' if total>=75 else 'C' if total>=60 else 'D' if total>=40 else 'E'
    if perf.get('tier')!=tier: e.append(f'supplier_performance.tier: expected {tier}')
    if perf.get('repeat_failure_count')!=c.get('repeat_failure_count'): e.append('supplier_performance.repeat_failure_count: must match case')
    if c.get('data_integrity_hold') and perf.get('escalation_level')!='SUSPENDED': e.append('supplier_performance.escalation_level: integrity hold requires SUSPENDED')

    assessment=data.get('assessment') if isinstance(data.get('assessment'),dict) else {}; 
    if not assessment: e.append('assessment: object required')
    calculated=assessment_engine.calculate(data, as_of=dt(assessment.get('calculated_at')) or datetime.now().astimezone())
    for k in ['readiness','recommended_case_status','recommended_escalation','calculated_supplier_score','calculated_supplier_tier','automatic_reinstatement_prohibited']:
        if assessment.get(k)!=calculated.get(k): e.append(f'assessment.{k}: expected {calculated.get(k)!r}')
    if sorted(assessment.get('blockers',[]))!=sorted(calculated.get('blockers',[])): e.append('assessment.blockers: does not reconcile with control engine')
    if assessment.get('readiness') is True and c.get('status')=='REINSTATED' and pp.get('decision') not in {'APPROVED','CONDITIONAL'}: e.append('assessment.readiness: reinstated state lacks transaction approval')

    audit=data.get('audit') if isinstance(data.get('audit'),dict) else {}; 
    if not audit: e.append('audit: object required')
    for k in ['created_at','updated_at']:
        if not dt(audit.get(k)): e.append(f'audit.{k}: valid date-time required')
    for k in ['created_by','updated_by']: req(audit,k,'audit',e)
    if audit.get('immutable_history') is not True: e.append('audit.immutable_history: must be true')
    if audit.get('source_records_hashed') is not True: e.append('audit.source_records_hashed: must be true')
    if audit.get('approval_separation_enforced') is not True: e.append('audit.approval_separation_enforced: must be true')
    if not isinstance(audit.get('change_history'),list): e.append('audit.change_history: array required')
    return e


def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('file'); a=p.parse_args(argv)
    try: data=json.loads(Path(a.file).read_text(encoding='utf-8'))
    except Exception as ex: print(f'FAIL: unable to read JSON: {ex}'); return 2
    errors=validate(data)
    if errors:
        print(f'FAIL: {len(errors)} control breach(es)')
        for x in errors: print(f'- {x}')
        return 1
    print('PASS: remediation case satisfies CERT-BUILD-0035H semantic controls')
    return 0

if __name__=='__main__': raise SystemExit(main())
