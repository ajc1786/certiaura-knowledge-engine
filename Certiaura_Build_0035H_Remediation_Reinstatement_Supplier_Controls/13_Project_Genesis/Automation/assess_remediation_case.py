#!/usr/bin/env python3
"""Read-only readiness, blocker and supplier-score assessment for CERT-BUILD-0035H."""
from __future__ import annotations
import argparse, copy, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

APPROVED_REVIEW={'REINSTATEMENT_APPROVED','CONDITIONAL_REINSTATEMENT'}
APPROVED_SECOND={'APPROVED'}
CLOSED_ALERTS={'CLOSED_RESOLVED','CLOSED_SUPERSEDED','CLOSED_NO_REINSTATEMENT'}


def parse_dt(value):
    if not isinstance(value,str): return None
    try: return datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError: return None


def calculate(case: dict[str,Any], as_of: datetime|None=None) -> dict[str,Any]:
    as_of=as_of or datetime.now(timezone.utc)
    c=case.get('case',{})
    cap=case.get('corrective_action_plan',{})
    refresh=case.get('evidence_refresh',{})
    review=case.get('review',{})
    closures=case.get('alert_closure',[])
    perf=case.get('supplier_performance',{})
    blockers=[]

    if c.get('legal_hold'): blockers.append('LEGAL_HOLD')
    if c.get('data_integrity_hold'): blockers.append('DATA_INTEGRITY_HOLD')

    actions=cap.get('actions',[]) if isinstance(cap.get('actions'),list) else []
    critical=[a for a in actions if a.get('critical') is True]
    if any(a.get('status')!='COMPLETED' for a in critical): blockers.append('CRITICAL_ACTION_INCOMPLETE')
    if any(a.get('effectiveness_result')!='PASS' for a in critical): blockers.append('CRITICAL_ACTION_EFFECTIVENESS_NOT_PASSED')
    if any(not a.get('completion_evidence_ids') for a in critical): blockers.append('CRITICAL_ACTION_EVIDENCE_MISSING')

    items=refresh.get('evidence_items',[]) if isinstance(refresh.get('evidence_items'),list) else []
    critical_items=[x for x in items if x.get('critical') is True]
    if refresh.get('status')!='VERIFIED' or refresh.get('all_critical_evidence_verified') is not True:
        blockers.append('CRITICAL_EVIDENCE_NOT_VERIFIED')
    if any(x.get('review_status')!='VERIFIED' for x in critical_items): blockers.append('CRITICAL_EVIDENCE_ITEM_NOT_VERIFIED')
    if refresh.get('verified_mandatory_count')!=refresh.get('mandatory_item_count'): blockers.append('MANDATORY_EVIDENCE_COUNT_MISMATCH')

    if review.get('primary_reviewer_conflict_free') is not True: blockers.append('PRIMARY_REVIEWER_CONFLICT')
    if review.get('decision') not in APPROVED_REVIEW: blockers.append('PRIMARY_REVIEW_NOT_APPROVED')
    if not review.get('second_approver_id') or review.get('second_approval_decision') not in APPROVED_SECOND: blockers.append('SECOND_APPROVAL_MISSING')
    if review.get('primary_reviewer_id') and review.get('primary_reviewer_id')==review.get('second_approver_id'): blockers.append('APPROVAL_SEPARATION_FAILURE')
    eff=parse_dt(review.get('effective_until'))
    if eff and eff<as_of: blockers.append('APPROVAL_PERIOD_EXPIRED')
    if review.get('residual_risk') in {None,'','NOT_ASSESSED','CRITICAL'}: blockers.append('RESIDUAL_RISK_NOT_ACCEPTABLE')

    source=set(c.get('source_alert_ids',[]) if isinstance(c.get('source_alert_ids'),list) else [])
    closure_map={x.get('alert_id'):x.get('decision') for x in closures if isinstance(x,dict)}
    if any(closure_map.get(a) not in CLOSED_ALERTS for a in source): blockers.append('SOURCE_ALERT_OPEN')

    # Score: retain deductions for audit transparency.
    ded={}
    sev=c.get('severity')
    ded['severity']=20 if sev=='CRITICAL' else 10 if sev=='HIGH' else 0
    ded['repeat_failure']=min(max(int(c.get('repeat_failure_count',0)),0)*8,24)
    overdue=False
    for a in actions:
        due=parse_dt(a.get('due_at'))
        if a.get('status') not in {'COMPLETED','CANCELLED'} and due and due<as_of: overdue=True
    ded['overdue_actions']=15 if overdue else 0
    ded['critical_evidence']=0 if refresh.get('all_critical_evidence_verified') is True and refresh.get('status')=='VERIFIED' else 25
    target=parse_dt(c.get('target_due_at'))
    ded['sla']=10 if target and target<as_of and c.get('status') not in {'REINSTATED','CLOSED_NO_REINSTATEMENT','REJECTED'} else 0
    ded['legal_hold']=40 if c.get('legal_hold') else 0
    ded['data_integrity_hold']=40 if c.get('data_integrity_hold') else 0
    timing=perf.get('response_timeliness_percent',100)
    try: timing=float(timing)
    except (TypeError,ValueError): timing=0
    ded['response_timeliness']=10 if timing<80 else 0
    score=max(0,100-sum(ded.values()))
    tier='A' if score>=90 else 'B' if score>=75 else 'C' if score>=60 else 'D' if score>=40 else 'E'

    if c.get('legal_hold') or c.get('data_integrity_hold') or sev=='CRITICAL' and int(c.get('repeat_failure_count',0))>=2:
        escalation='SUSPENDED'
    elif int(c.get('repeat_failure_count',0))>=3 or tier=='E': escalation='RESTRICTED'
    elif int(c.get('repeat_failure_count',0))>=2 or tier=='D': escalation='FORMAL_IMPROVEMENT'
    elif tier=='C' or int(c.get('repeat_failure_count',0))>=1: escalation='WATCH'
    else: escalation='NONE'

    readiness=not blockers
    if c.get('status') in {'ESCALATED','REJECTED','CLOSED_NO_REINSTATEMENT'} and readiness:
        blockers.append('CASE_STATE_NOT_REINSTATEMENT_ROUTE'); readiness=False
    recommended='REINSTATEMENT_READY' if readiness else ('ESCALATED' if escalation in {'RESTRICTED','SUSPENDED'} else 'UNDER_REVIEW' if review.get('decision')!='NOT_STARTED' else 'REMEDIATION_IN_PROGRESS')
    return {
      'calculated_at':as_of.astimezone(timezone.utc).isoformat().replace('+00:00','Z'),
      'calculated_by':'Project Genesis 0035H',
      'readiness':readiness,
      'recommended_case_status':recommended,
      'blockers':sorted(set(blockers)),
      'recommended_escalation':escalation,
      'calculated_supplier_score':score,
      'calculated_supplier_tier':tier,
      'component_deductions':ded,
      'automatic_reinstatement_prohibited':True
    }


def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('-o','--output')
    a=p.parse_args(argv)
    data=json.loads(Path(a.input).read_text(encoding='utf-8'))
    result=calculate(data)
    text=json.dumps(result,indent=2)+"\n"
    if a.output: Path(a.output).write_text(text,encoding='utf-8')
    else: print(text,end='')
    return 0

if __name__=='__main__': raise SystemExit(main())
