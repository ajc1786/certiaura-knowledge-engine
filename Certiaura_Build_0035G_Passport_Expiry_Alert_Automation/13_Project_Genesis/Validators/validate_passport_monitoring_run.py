#!/usr/bin/env python3
"""Semantic validator for CERT-BUILD-0035G monitoring runs.
Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

HEX64=re.compile(r'^[0-9a-fA-F]{64}$')
RUN_ID=re.compile(r'^PPS-MON-[A-Z0-9-]{3,80}$')
PASSPORT_ID=re.compile(r'^PPS-PAS-[A-Z0-9-]{3,80}$')
ALERT_ID=re.compile(r'^PPS-ALT-[A-Z0-9-]{3,80}$')
SEVERITY={'NONE':0,'LOW':1,'MEDIUM':2,'HIGH':3,'CRITICAL':4}
PROTECTIVE={'AUTO_EXPIRE','AUTO_SUSPEND','AUTO_SUSPEND_MARKETPLACE','AUTO_REMOVE_MARKETPLACE'}
PROHIBITED={'AUTO_PUBLISH','AUTO_VERIFY','AUTO_REINSTATE','AUTO_APPROVE_MARKETPLACE'}
ACTIVE_MARKET={'ELIGIBLE','CONDITIONALLY_ELIGIBLE'}


def parse_dt(value: Any):
    if not isinstance(value,str): return None
    try: return datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError: return None


def req_str(obj: dict, key: str, path: str, errors: list[str]) -> str:
    value=obj.get(key)
    if not isinstance(value,str) or not value.strip():
        errors.append(f'{path}.{key}: non-empty string required')
        return ''
    return value.strip()


def validate(data: Any) -> list[str]:
    e=[]
    if not isinstance(data,dict): return ['root: object required']
    if data.get('schema_version')!='1.0.0': e.append('schema_version: must be 1.0.0')
    run=data.get('run')
    if not isinstance(run,dict): e.append('run: object required'); run={}
    rid=run.get('run_id')
    if not isinstance(rid,str) or not RUN_ID.fullmatch(rid): e.append('run.run_id: invalid')
    if run.get('run_type') not in {'SCHEDULED','EVENT_DRIVEN','MANUAL','REPLAY'}: e.append('run.run_type: invalid')
    started=parse_dt(run.get('started_at')); completed=parse_dt(run.get('completed_at')); as_of=parse_dt(run.get('as_of'))
    if not started: e.append('run.started_at: valid date-time required')
    if not completed: e.append('run.completed_at: valid date-time required')
    if not as_of: e.append('run.as_of: valid date-time required')
    if started and completed and completed<started: e.append('run.completed_at: cannot precede started_at')
    if not re.fullmatch(r'\d+\.\d+\.\d+',str(run.get('policy_version',''))): e.append('run.policy_version: semantic version required')
    if not re.fullmatch(r'\d+\.\d+\.\d+',str(run.get('engine_version',''))): e.append('run.engine_version: semantic version required')
    req_str(run,'executed_by','run',e)
    status=run.get('run_status')
    if status not in {'STARTED','COMPLETED','COMPLETED_WITH_ALERTS','PARTIAL','FAILED','STALE_INPUT'}: e.append('run.run_status: invalid')

    checks=data.get('checks')
    if not isinstance(checks,list): e.append('checks: array required'); checks=[]
    alert_ids_from_checks=[]; finding_count=0; record_findings=0; protective_count=0
    for i,check in enumerate(checks):
        p=f'checks[{i}]'
        if not isinstance(check,dict): e.append(f'{p}: object required'); continue
        pid=check.get('passport_id')
        if not isinstance(pid,str) or not PASSPORT_ID.fullmatch(pid): e.append(f'{p}.passport_id: invalid')
        if not re.fullmatch(r'\d+\.\d+\.\d+',str(check.get('passport_version',''))): e.append(f'{p}.passport_version: semantic version required')
        if not isinstance(check.get('source_sha256'),str) or not HEX64.fullmatch(check.get('source_sha256','')): e.append(f'{p}.source_sha256: 64 hex characters required')
        findings=check.get('finding_codes')
        if not isinstance(findings,list): e.append(f'{p}.finding_codes: array required'); findings=[]
        if len(findings)!=len(set(map(str,findings))): e.append(f'{p}.finding_codes: duplicates prohibited')
        finding_count+=len(findings); record_findings+=bool(findings)
        action=check.get('action_instruction')
        if action in PROHIBITED: e.append(f'{p}.action_instruction: positive automatic action prohibited')
        if action not in {'NONE','QUEUE_REVIEW','QUEUE_EVIDENCE_REFRESH','QUEUE_CLAIM_REVIEW','AUTO_EXPIRE','AUTO_SUSPEND','AUTO_SUSPEND_MARKETPLACE','AUTO_REMOVE_MARKETPLACE','QUARANTINE_INPUT'}: e.append(f'{p}.action_instruction: invalid')
        if action in PROTECTIVE: protective_count+=1
        if action!='NONE' and check.get('human_review_required') is not True: e.append(f'{p}.human_review_required: true required when action exists')
        highest=check.get('highest_severity')
        if highest not in SEVERITY: e.append(f'{p}.highest_severity: invalid')
        ids=check.get('alert_ids')
        if not isinstance(ids,list): e.append(f'{p}.alert_ids: array required'); ids=[]
        if len(ids)!=len(set(ids)): e.append(f'{p}.alert_ids: duplicates prohibited')
        alert_ids_from_checks.extend(ids)
        if 'PASSPORT_EXPIRED' in findings:
            expiry_ok = (
                (action=='AUTO_EXPIRE' and check.get('proposed_passport_state')=='EXPIRED' and check.get('proposed_marketplace_state')=='REMOVED')
                or
                (action=='AUTO_SUSPEND' and check.get('proposed_passport_state')=='SUSPENDED' and check.get('proposed_marketplace_state') in {'SUSPENDED','REMOVED'})
            )
            if not expiry_ok:
                e.append(f'{p}: PASSPORT_EXPIRED requires AUTO_EXPIRE or stricter AUTO_SUSPEND with restrictive states')
        if any(str(x).startswith('OPEN_CRITICAL_TRIGGER') for x in findings) or 'UPSTREAM_REVIEW_EXPIRED' in findings:
            if action!='AUTO_SUSPEND' or check.get('proposed_passport_state')!='SUSPENDED' or check.get('proposed_marketplace_state') not in {'SUSPENDED','REMOVED'}:
                e.append(f'{p}: critical trigger requires AUTO_SUSPEND and restrictive states')
        if check.get('proposed_marketplace_state') in ACTIVE_MARKET:
            e.append(f'{p}.proposed_marketplace_state: automation cannot grant active marketplace state')
        if check.get('proposed_passport_state') in {'PUBLISHED','READY_FOR_PUBLICATION'}:
            e.append(f'{p}.proposed_passport_state: automation cannot grant positive publication state')

    alerts=data.get('alerts')
    if not isinstance(alerts,list): e.append('alerts: array required'); alerts=[]
    seen_ids=set(); seen_keys=set(); severity_counts={k:0 for k in ['LOW','MEDIUM','HIGH','CRITICAL']}
    for i,alert in enumerate(alerts):
        p=f'alerts[{i}]'
        if not isinstance(alert,dict): e.append(f'{p}: object required'); continue
        aid=alert.get('alert_id')
        if not isinstance(aid,str) or not ALERT_ID.fullmatch(aid): e.append(f'{p}.alert_id: invalid')
        elif aid in seen_ids: e.append(f'{p}.alert_id: duplicate')
        else: seen_ids.add(aid)
        key=req_str(alert,'dedupe_key',p,e)
        if key in seen_keys: e.append(f'{p}.dedupe_key: duplicate')
        seen_keys.add(key)
        sev=alert.get('severity')
        if sev not in severity_counts: e.append(f'{p}.severity: invalid')
        else: severity_counts[sev]+=1
        pri=alert.get('priority')
        if pri not in {'P0','P1','P2','P3','P4'}: e.append(f'{p}.priority: invalid')
        detected=parse_dt(alert.get('detected_at')); due=parse_dt(alert.get('due_at'))
        if not detected: e.append(f'{p}.detected_at: valid date-time required')
        if not due: e.append(f'{p}.due_at: valid date-time required')
        if detected and due and due<detected: e.append(f'{p}.due_at: cannot precede detection')
        if alert.get('source_run_id')!=rid: e.append(f'{p}.source_run_id: must match run identifier')
        if sev=='CRITICAL':
            if pri!='P0': e.append(f'{p}.priority: CRITICAL requires P0')
            secondary=alert.get('secondary_routes')
            if not isinstance(secondary,list) or not secondary: e.append(f'{p}.secondary_routes: CRITICAL requires secondary route')
        if alert.get('proposed_marketplace_state') in ACTIVE_MARKET: e.append(f'{p}.proposed_marketplace_state: positive state prohibited')
        if alert.get('proposed_passport_state') in {'PUBLISHED','READY_FOR_PUBLICATION'}: e.append(f'{p}.proposed_passport_state: positive state prohibited')
        req_str(alert,'primary_route',p,e); req_str(alert,'required_action',p,e); req_str(alert,'message',p,e)

    if set(alert_ids_from_checks)!=seen_ids: e.append('checks.alert_ids: must reconcile exactly to alerts')

    summary=data.get('summary')
    if not isinstance(summary,dict): e.append('summary: object required'); summary={}
    expected={
      'records_scanned':len(checks),
      'records_with_findings':record_findings,
      'finding_count':finding_count,
      'alert_count':len(alerts),
      'protective_action_count':protective_count
    }
    for key,value in expected.items():
        if summary.get(key)!=value: e.append(f'summary.{key}: expected {value}')
    if summary.get('severity_counts')!=severity_counts: e.append('summary.severity_counts: does not reconcile to alerts')
    if summary.get('status_reconciled') is not True: e.append('summary.status_reconciled: must be true')
    if status=='COMPLETED' and alerts: e.append('run.run_status: alerts require COMPLETED_WITH_ALERTS')
    if status=='COMPLETED_WITH_ALERTS' and not alerts: e.append('run.run_status: no alerts requires COMPLETED')

    audit=data.get('audit')
    if not isinstance(audit,dict): e.append('audit: object required'); audit={}
    if not parse_dt(audit.get('created_at')): e.append('audit.created_at: valid date-time required')
    req_str(audit,'created_by','audit',e)
    if audit.get('immutable_record') is not True: e.append('audit.immutable_record: must be true')
    if audit.get('source_records_hashed') is not True: e.append('audit.source_records_hashed: must be true')
    if audit.get('positive_approval_prohibited') is not True: e.append('audit.positive_approval_prohibited: must be true')
    if audit.get('validation_status') not in {'PASS','FAIL','NOT_RUN'}: e.append('audit.validation_status: invalid')
    return e


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('file')
    args=parser.parse_args(argv)
    try:
        data=json.loads(Path(args.file).read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'FAIL: unable to read JSON: {exc}')
        return 2
    errors=validate(data)
    if errors:
        print(f'FAIL: {len(errors)} control breach(es)')
        for item in errors: print(f'- {item}')
        return 1
    print('PASS: monitoring run satisfies CERT-BUILD-0035G semantic controls')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
