#!/usr/bin/env python3
"""Read-only Product Passport monitoring engine for CERT-BUILD-0035G.

Uses only the Python standard library. It reads one JSON record, a JSON array, or
all *.json files in a directory and produces a monitoring-run JSON file. It does
not edit source lifecycle records or apply transactions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from typing import Any

ENGINE_VERSION = '1.0.0'
POLICY_VERSION = '1.0.0'
SEVERITY_RANK = {'NONE':0,'LOW':1,'MEDIUM':2,'HIGH':3,'CRITICAL':4}
ACTIVE_MARKET = {'ELIGIBLE','CONDITIONALLY_ELIGIBLE'}
CRITICAL_TYPES = {
    'EVIDENCE_WITHDRAWN','REPORT_INTEGRITY_DISPUTE','BATCH_MISMATCH',
    'LEGAL_REGULATORY_ALERT','COUNTERFEIT_OR_DUPLICATE_CONCERN'
}
PROHIBITED_POSITIVE_ACTIONS = {'AUTO_PUBLISH','AUTO_VERIFY','AUTO_REINSTATE','AUTO_APPROVE_MARKETPLACE'}


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace('Z','+00:00'))


def parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def canonical_hash(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def safe_token(value: str) -> str:
    token = re.sub(r'[^A-Z0-9]+','-',value.upper()).strip('-')
    return token[:48] or 'UNKNOWN'


def stable_alert_id(dedupe_key: str) -> str:
    return 'PPS-ALT-' + hashlib.sha256(dedupe_key.encode('utf-8')).hexdigest()[:16].upper()


def make_alert(*, run_id: str, as_of: datetime, passport_id: str, passport_version: str,
               alert_type: str, finding_code: str, severity: str, priority: str,
               target_date: date | None, primary_route: str, secondary_routes: list[str],
               required_action: str, proposed_passport_state: str | None,
               proposed_marketplace_state: str | None, source_event_ids: list[str] | None = None,
               due_hours: int = 24, message: str = '') -> dict:
    target = target_date.isoformat() if target_date else 'NO-DATE'
    dedupe_key = f'{passport_id}|{passport_version}|{finding_code}|{target}'
    aid = stable_alert_id(dedupe_key)
    due_at = as_of + timedelta(hours=due_hours)
    return {
      'alert_id': aid,
      'dedupe_key': dedupe_key,
      'passport_id': passport_id,
      'passport_version': passport_version,
      'alert_type': alert_type,
      'severity': severity,
      'priority': priority,
      'detected_at': as_of.isoformat().replace('+00:00','Z'),
      'due_at': due_at.isoformat().replace('+00:00','Z'),
      'target_date': target_date.isoformat() if target_date else None,
      'finding_codes': [finding_code],
      'source_event_ids': source_event_ids or [],
      'primary_route': primary_route,
      'secondary_routes': secondary_routes,
      'required_action': required_action,
      'proposed_passport_state': proposed_passport_state,
      'proposed_marketplace_state': proposed_marketplace_state,
      'status': 'OPEN',
      'first_seen_at': as_of.isoformat().replace('+00:00','Z'),
      'last_seen_at': as_of.isoformat().replace('+00:00','Z'),
      'source_run_id': run_id,
      'message': message or f'{finding_code} requires {required_action}.'
    }


def threshold_finding(prefix: str, target: date | None, as_of_date: date) -> tuple[str,str,str,str] | None:
    """Return finding_code, severity, priority, action for supported thresholds."""
    if not target:
        return ('DATA_QUALITY_MISSING_DATE','HIGH','P1','QUARANTINE_INPUT')
    days = (target - as_of_date).days
    if days < 0:
        mapping = {
          'PASSPORT':('PASSPORT_EXPIRED','HIGH','P1','AUTO_EXPIRE'),
          'REVIEW':('REVIEW_OVERDUE','HIGH','P1','AUTO_SUSPEND_MARKETPLACE'),
          'UPSTREAM':('UPSTREAM_REVIEW_EXPIRED','CRITICAL','P0','AUTO_SUSPEND'),
          'CLAIM':('CLAIM_REVIEW_OVERDUE','HIGH','P1','QUEUE_CLAIM_REVIEW'),
          'MARKET':('MARKETPLACE_REVIEW_OVERDUE','HIGH','P1','AUTO_SUSPEND_MARKETPLACE')
        }
        return mapping[prefix]
    supported = [60,30,14,7,1,0]
    if days not in supported:
        return None
    sev_priority = {
      60:('LOW','P4'), 30:('MEDIUM','P3'), 14:('MEDIUM','P3'),
      7:('HIGH','P2'), 1:('HIGH','P2'), 0:('HIGH','P1')
    }
    severity, priority = sev_priority[days]
    labels = {
      'PASSPORT': f'PASSPORT_EXPIRY_{days}D' if days else 'PASSPORT_EXPIRES_TODAY',
      'REVIEW': f'REVIEW_DUE_{days}D' if days else 'REVIEW_DUE_TODAY',
      'UPSTREAM': f'UPSTREAM_REVIEW_EXPIRY_{days}D' if days else 'UPSTREAM_REVIEW_EXPIRES_TODAY',
      'CLAIM': f'CLAIM_REVIEW_DUE_{days}D' if days else 'CLAIM_REVIEW_DUE_TODAY',
      'MARKET': f'MARKETPLACE_REVIEW_DUE_{days}D' if days else 'MARKETPLACE_REVIEW_DUE_TODAY'
    }
    action = 'QUEUE_EVIDENCE_REFRESH' if prefix in {'PASSPORT','UPSTREAM'} else 'QUEUE_REVIEW'
    if prefix == 'CLAIM': action = 'QUEUE_CLAIM_REVIEW'
    return labels[prefix], severity, priority, action


def evaluate_record(record: dict, *, run_id: str, as_of: datetime) -> tuple[dict,list[dict]]:
    pid = str(record.get('passport_id',''))
    version = str(record.get('passport_version',''))
    state = record.get('lifecycle_state')
    market_obj = record.get('marketplace') if isinstance(record.get('marketplace'),dict) else {}
    market = market_obj.get('marketplace_state')
    source_hash = canonical_hash(record)
    findings: list[tuple[str,str,str,str,date|None,list[str]]] = []

    pub = record.get('publication') if isinstance(record.get('publication'),dict) else {}
    review = record.get('review_decision') if isinstance(record.get('review_decision'),dict) else {}

    for prefix, target in [
      ('PASSPORT',parse_date(pub.get('effective_until'))),
      ('REVIEW',parse_date(pub.get('next_review_date'))),
      ('UPSTREAM',parse_date(review.get('review_effective_until'))),
      ('MARKET',parse_date(market_obj.get('next_review_date')) if market in ACTIVE_MARKET else None),
    ]:
        if prefix == 'MARKET' and market not in ACTIVE_MARKET:
            continue
        result = threshold_finding(prefix,target,as_of.date())
        if result:
            code,sev,pri,action = result
            findings.append((code,sev,pri,action,target,[]))

    claims = record.get('public_claims')
    if isinstance(claims,list):
        for claim in claims:
            if not isinstance(claim,dict):
                continue
            target = parse_date(claim.get('next_review_date'))
            result = threshold_finding('CLAIM',target,as_of.date())
            if result:
                code,sev,pri,action = result
                claim_id = str(claim.get('claim_id','UNKNOWN'))
                findings.append((f'{code}:{claim_id}',sev,pri,action,target,[]))

    events = record.get('lifecycle_events')
    if isinstance(events,list):
        for event in events:
            if not isinstance(event,dict) or event.get('status') not in {'OPEN','IN_REVIEW'}:
                continue
            severity = event.get('severity')
            event_type = str(event.get('event_type','OPEN_EVENT'))
            eid = str(event.get('event_id',''))
            if severity == 'CRITICAL' or event_type in CRITICAL_TYPES:
                findings.append((f'OPEN_CRITICAL_TRIGGER:{event_type}','CRITICAL','P0','AUTO_SUSPEND',None,[eid]))
            elif severity == 'HIGH':
                findings.append((f'OPEN_HIGH_TRIGGER:{event_type}','HIGH','P1','AUTO_SUSPEND_MARKETPLACE',None,[eid]))

    # Deduplicate findings while preserving the strictest occurrence.
    by_code: dict[str,tuple[str,str,str,str,date|None,list[str]]] = {}
    for item in findings:
        code,sev,pri,action,target,event_ids = item
        existing = by_code.get(code)
        if not existing or SEVERITY_RANK[sev] > SEVERITY_RANK[existing[1]]:
            by_code[code] = item
    findings = list(by_code.values())

    alerts: list[dict] = []
    for code,sev,pri,action,target,event_ids in findings:
        base_code = code.split(':',1)[0]
        if base_code.startswith('OPEN_CRITICAL_TRIGGER'):
            alert_type='OPEN_CRITICAL_TRIGGER'; primary='PPS_REVIEW_QUEUE'; secondary=['LEGAL_REGULATORY','MARKETPLACE_OPERATIONS']; due=0
            pstate='SUSPENDED'; mstate='SUSPENDED'
        elif base_code.startswith('OPEN_HIGH_TRIGGER'):
            alert_type='OPEN_HIGH_TRIGGER'; primary='PPS_REVIEW_QUEUE'; secondary=['MARKETPLACE_OPERATIONS']; due=4
            pstate=None; mstate='SUSPENDED'
        elif base_code in {'PASSPORT_EXPIRED'}:
            alert_type='PASSPORT_EXPIRED'; primary='PPS_REVIEW_QUEUE'; secondary=['MARKETPLACE_OPERATIONS']; due=0
            pstate='EXPIRED'; mstate='REMOVED'
        elif base_code in {'UPSTREAM_REVIEW_EXPIRED'}:
            alert_type='UPSTREAM_REVIEW_EXPIRED'; primary='PPS_REVIEW_QUEUE'; secondary=['EKS_REVIEW_QUEUE','MARKETPLACE_OPERATIONS']; due=0
            pstate='SUSPENDED'; mstate='SUSPENDED'
        elif base_code in {'REVIEW_OVERDUE','MARKETPLACE_REVIEW_OVERDUE'}:
            alert_type='REVIEW_DUE_OR_OVERDUE'; primary='PPS_REVIEW_QUEUE'; secondary=['EKS_REFRESH_QUEUE','MARKETPLACE_OPERATIONS']; due=4
            pstate=None; mstate='SUSPENDED'
        elif base_code.startswith('CLAIM_REVIEW_OVERDUE'):
            alert_type='CLAIM_REVIEW_OVERDUE'; primary='PPS_REVIEW_QUEUE'; secondary=['EKS_REVIEW_QUEUE']; due=4
            pstate=None; mstate='SUSPENDED'
        elif base_code.startswith('DATA_QUALITY'):
            alert_type='DATA_QUALITY'; primary='PLATFORM_DATA_QUALITY'; secondary=['PPS_REVIEW_QUEUE']; due=0
            pstate=None; mstate=None
        else:
            alert_type='PASSPORT_EXPIRY' if 'EXPIR' in base_code else 'REVIEW_DUE_OR_OVERDUE'
            primary='PPS_REVIEW_QUEUE'; secondary=['EKS_REFRESH_QUEUE']; due=24
            pstate=None; mstate=None
        alerts.append(make_alert(
          run_id=run_id, as_of=as_of, passport_id=pid, passport_version=version,
          alert_type=alert_type, finding_code=code, severity=sev, priority=pri,
          target_date=target, primary_route=primary, secondary_routes=secondary,
          required_action=action, proposed_passport_state=pstate,
          proposed_marketplace_state=mstate, source_event_ids=event_ids,
          due_hours=due, message=f'{code} detected for {pid} version {version}; required action: {action}.'
        ))

    highest = 'NONE'
    if findings:
        highest = max((item[1] for item in findings), key=lambda s: SEVERITY_RANK[s])

    codes = [x[0] for x in findings]
    action = 'NONE'; proposed_passport=None; proposed_market=None; human_review=False
    if any(c.startswith('OPEN_CRITICAL_TRIGGER') for c in codes) or 'UPSTREAM_REVIEW_EXPIRED' in codes:
        action='AUTO_SUSPEND'; proposed_passport='SUSPENDED'; proposed_market='SUSPENDED'; human_review=True
    elif 'PASSPORT_EXPIRED' in codes:
        action='AUTO_EXPIRE'; proposed_passport='EXPIRED'; proposed_market='REMOVED'; human_review=True
    elif any(c.startswith('OPEN_HIGH_TRIGGER') for c in codes) or 'REVIEW_OVERDUE' in codes or 'MARKETPLACE_REVIEW_OVERDUE' in codes:
        action='AUTO_SUSPEND_MARKETPLACE'; proposed_market='SUSPENDED'; human_review=True
    elif any(c.startswith('CLAIM_REVIEW_OVERDUE') for c in codes):
        action='QUEUE_CLAIM_REVIEW'; proposed_market='SUSPENDED'; human_review=True
    elif codes:
        action='QUEUE_EVIDENCE_REFRESH' if any('EXPIR' in c for c in codes) else 'QUEUE_REVIEW'; human_review=True

    check = {
      'passport_id':pid,
      'passport_version':version,
      'source_sha256':source_hash,
      'lifecycle_state_before':state,
      'marketplace_state_before':market,
      'finding_codes':codes,
      'highest_severity':highest,
      'proposed_passport_state':proposed_passport,
      'proposed_marketplace_state':proposed_market,
      'action_instruction':action,
      'human_review_required':human_review,
      'alert_ids':[a['alert_id'] for a in alerts]
    }
    return check, alerts


def load_records(path: Path) -> list[dict]:
    if path.is_dir():
        records=[]
        for file in sorted(path.glob('*.json')):
            value=json.loads(file.read_text(encoding='utf-8'))
            if isinstance(value,list): records.extend(value)
            elif isinstance(value,dict): records.append(value)
            else: raise ValueError(f'{file}: object or array required')
        return records
    value=json.loads(path.read_text(encoding='utf-8'))
    if isinstance(value,list): return value
    if isinstance(value,dict): return [value]
    raise ValueError('Input must be an object, array or directory of JSON files')


def build_run(records: list[dict], *, run_id: str, run_type: str, as_of: datetime,
              executed_by: str, reason: str | None = None) -> dict:
    started=as_of
    checks=[]; alerts=[]
    for record in records:
        check, record_alerts = evaluate_record(record,run_id=run_id,as_of=as_of)
        checks.append(check); alerts.extend(record_alerts)

    # Alert IDs are deterministic; suppress exact duplicate alert objects within the run.
    unique={}
    for alert in alerts:
        unique.setdefault(alert['dedupe_key'],alert)
    alerts=list(unique.values())

    severity_counts={k:0 for k in ['LOW','MEDIUM','HIGH','CRITICAL']}
    for alert in alerts: severity_counts[alert['severity']]+=1
    protective={'AUTO_EXPIRE','AUTO_SUSPEND','AUTO_SUSPEND_MARKETPLACE','AUTO_REMOVE_MARKETPLACE'}
    finding_count=sum(len(c['finding_codes']) for c in checks)
    status='COMPLETED_WITH_ALERTS' if alerts else 'COMPLETED'
    completed=as_of
    run={
      'schema_version':'1.0.0',
      'run':{
        'run_id':run_id,'run_type':run_type,
        'started_at':started.isoformat().replace('+00:00','Z'),
        'completed_at':completed.isoformat().replace('+00:00','Z'),
        'as_of':as_of.isoformat().replace('+00:00','Z'),
        'policy_version':POLICY_VERSION,'engine_version':ENGINE_VERSION,
        'executed_by':executed_by,'run_status':status,'reason':reason
      },
      'checks':checks,
      'alerts':alerts,
      'summary':{
        'records_scanned':len(checks),
        'records_with_findings':sum(bool(c['finding_codes']) for c in checks),
        'finding_count':finding_count,
        'alert_count':len(alerts),
        'protective_action_count':sum(c['action_instruction'] in protective for c in checks),
        'severity_counts':severity_counts,
        'status_reconciled':True
      },
      'audit':{
        'created_at':completed.isoformat().replace('+00:00','Z'),
        'created_by':executed_by,
        'immutable_record':True,
        'source_records_hashed':True,
        'positive_approval_prohibited':True,
        'validation_status':'NOT_RUN',
        'validation_errors':[]
      }
    }
    return run


def main(argv=None) -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('input_path')
    parser.add_argument('--output',required=True)
    parser.add_argument('--as-of',required=True,help='ISO date-time with timezone, preferably Z')
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--run-type',default='SCHEDULED',choices=['SCHEDULED','EVENT_DRIVEN','MANUAL','REPLAY'])
    parser.add_argument('--executed-by',default='Project Genesis')
    parser.add_argument('--reason')
    args=parser.parse_args(argv)
    try:
        as_of=parse_dt(args.as_of)
        if as_of.tzinfo is None: raise ValueError('as-of must include timezone')
        records=load_records(Path(args.input_path))
        result=build_run(records,run_id=args.run_id,run_type=args.run_type,as_of=as_of,
                         executed_by=args.executed_by,reason=args.reason)
        Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(f"PASS: scanned {result['summary']['records_scanned']} record(s); generated {result['summary']['alert_count']} alert(s)")
        return 0
    except Exception as exc:
        print(f'FAIL: {exc}',file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
