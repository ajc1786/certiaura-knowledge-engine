#!/usr/bin/env python3
"""Semantic validator for CERT-BUILD-0035F lifecycle records.
Uses only the Python standard library.
"""
from __future__ import annotations
import argparse, json, re, sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
PASSPORT_ID = re.compile(r"^PPS-PAS-[A-Z0-9-]{3,80}$")
CLAIM_ID = re.compile(r"^CLM-[A-Z0-9-]{3,80}$")
EVENT_ID = re.compile(r"^PPS-EVT-[A-Z0-9-]{3,80}$")
STATES = {"DRAFT","READY_FOR_PUBLICATION","PUBLISHED","SUSPENDED","EXPIRED","WITHDRAWN","SUPERSEDED","ARCHIVED"}
MARKET = {"NOT_ASSESSED","ELIGIBLE","CONDITIONALLY_ELIGIBLE","INELIGIBLE","SUSPENDED","REMOVED"}
ACTIVE_MARKET = {"ELIGIBLE","CONDITIONALLY_ELIGIBLE"}


def parse_date(v: Any):
    if not isinstance(v, str): return None
    try: return date.fromisoformat(v)
    except ValueError: return None

def parse_dt(v: Any):
    if not isinstance(v, str): return None
    try: return datetime.fromisoformat(v.replace('Z','+00:00'))
    except ValueError: return None

def req_str(obj: dict, key: str, path: str, errors: list[str]) -> str:
    v=obj.get(key)
    if not isinstance(v,str) or not v.strip():
        errors.append(f"{path}.{key}: non-empty string required")
        return ''
    return v.strip()

def validate(data: Any) -> list[str]:
    e: list[str] = []
    if not isinstance(data, dict): return ['root: object required']
    if data.get('schema_version') != '1.0.0': e.append('schema_version: must be 1.0.0')
    pid=data.get('passport_id')
    if not isinstance(pid,str) or not PASSPORT_ID.fullmatch(pid): e.append('passport_id: invalid')
    if not isinstance(data.get('passport_version'),str) or not re.fullmatch(r'\d+\.\d+\.\d+',data.get('passport_version','')): e.append('passport_version: semantic version required')

    review=data.get('review_decision')
    if not isinstance(review,dict):
        e.append('review_decision: object required'); review={}
    rid=req_str(review,'review_decision_id','review_decision',e)
    if review.get('decision_status')!='VERIFIED': e.append('review_decision.decision_status: publication requires VERIFIED')
    if review.get('public_passport_eligibility')!='ELIGIBLE': e.append('review_decision.public_passport_eligibility: publication requires ELIGIBLE')
    if not isinstance(review.get('review_decision_sha256'),str) or not HEX64.fullmatch(review.get('review_decision_sha256','')): e.append('review_decision.review_decision_sha256: 64 hex characters required')
    review_until=parse_date(review.get('review_effective_until'))
    if not review_until: e.append('review_decision.review_effective_until: valid date required')

    state=data.get('lifecycle_state')
    if state not in STATES: e.append('lifecycle_state: invalid')
    pub=data.get('publication')
    if not isinstance(pub,dict): e.append('publication: object required'); pub={}
    req_str(pub,'public_slug','publication',e)
    eff_from=parse_date(pub.get('effective_from')); eff_until=parse_date(pub.get('effective_until')); next_review=parse_date(pub.get('next_review_date'))
    if not eff_from: e.append('publication.effective_from: valid date required')
    if not eff_until: e.append('publication.effective_until: valid date required')
    if not next_review: e.append('publication.next_review_date: valid date required')
    if eff_from and eff_until and eff_from>eff_until: e.append('publication: effective_from cannot be after effective_until')
    if next_review and eff_until and next_review>eff_until: e.append('publication.next_review_date: cannot be after effective_until')
    if review_until and eff_until and eff_until>review_until: e.append('publication.effective_until: cannot exceed controlling review effective date')
    disclaimer=req_str(pub,'mandatory_disclaimer','publication',e)
    if len(disclaimer)<20: e.append('publication.mandatory_disclaimer: too short')

    claims=data.get('public_claims')
    if not isinstance(claims,list): e.append('public_claims: array required'); claims=[]
    claim_ids=set()
    for i,c in enumerate(claims):
        p=f'public_claims[{i}]'
        if not isinstance(c,dict): e.append(f'{p}: object required'); continue
        cid=c.get('claim_id')
        if not isinstance(cid,str) or not CLAIM_ID.fullmatch(cid): e.append(f'{p}.claim_id: invalid')
        elif cid in claim_ids: e.append(f'{p}.claim_id: duplicate')
        else: claim_ids.add(cid)
        if c.get('evidence_class') not in {'E4','E5'}: e.append(f'{p}.evidence_class: public claim requires E4 or E5')
        if c.get('upstream_verified') is not True: e.append(f'{p}.upstream_verified: must be true')
        if c.get('upstream_public_display_approved') is not True: e.append(f'{p}.upstream_public_display_approved: must be true')
        if rid and c.get('source_review_decision_id')!=rid: e.append(f'{p}.source_review_decision_id: must match controlling review')
        if c.get('visibility')!='PUBLIC': e.append(f'{p}.visibility: must be PUBLIC')
        if len(str(c.get('scope_statement','')).strip())<10: e.append(f'{p}.scope_statement: required')
        if len(str(c.get('limitations','')).strip())<10: e.append(f'{p}.limitations: required')
        if not parse_date(c.get('last_verified_date')): e.append(f'{p}.last_verified_date: valid date required')
        cnext=parse_date(c.get('next_review_date'))
        if not cnext: e.append(f'{p}.next_review_date: valid date required')
        elif next_review and cnext>next_review: e.append(f'{p}.next_review_date: cannot exceed passport next review date')

    events=data.get('lifecycle_events')
    if not isinstance(events,list): e.append('lifecycle_events: array required'); events=[]
    unresolved_critical=False; unresolved_high=False; event_ids=set()
    for i,ev in enumerate(events):
        p=f'lifecycle_events[{i}]'
        if not isinstance(ev,dict): e.append(f'{p}: object required'); continue
        eid=ev.get('event_id')
        if not isinstance(eid,str) or not EVENT_ID.fullmatch(eid): e.append(f'{p}.event_id: invalid')
        elif eid in event_ids: e.append(f'{p}.event_id: duplicate')
        else: event_ids.add(eid)
        if not parse_dt(ev.get('detected_at')): e.append(f'{p}.detected_at: valid date-time required')
        sev=ev.get('severity'); status=ev.get('status')
        if sev not in {'LOW','MEDIUM','HIGH','CRITICAL'}: e.append(f'{p}.severity: invalid')
        if status not in {'OPEN','IN_REVIEW','RESOLVED','CLOSED'}: e.append(f'{p}.status: invalid')
        if status in {'RESOLVED','CLOSED'} and not parse_dt(ev.get('resolved_at')): e.append(f'{p}.resolved_at: required when resolved or closed')
        if status in {'OPEN','IN_REVIEW'}:
            if sev=='CRITICAL': unresolved_critical=True
            if sev=='HIGH': unresolved_high=True

    market=data.get('marketplace')
    if not isinstance(market,dict): e.append('marketplace: object required'); market={}
    mstate=market.get('marketplace_state')
    if mstate not in MARKET: e.append('marketplace.marketplace_state: invalid')
    if market.get('unresolved_high_or_critical_trigger') is not (unresolved_critical or unresolved_high): e.append('marketplace.unresolved_high_or_critical_trigger: must match open high/critical events')

    if state=='PUBLISHED':
        if pub.get('publication_gate_passed') is not True: e.append('publication.publication_gate_passed: must be true for PUBLISHED')
        if not parse_dt(pub.get('published_at')): e.append('publication.published_at: required for PUBLISHED')
        req_str(pub,'published_by','publication',e)
        if not claims: e.append('public_claims: at least one required for PUBLISHED')
        if unresolved_critical: e.append('lifecycle_state: PUBLISHED prohibited with unresolved CRITICAL event')
    if state=='SUSPENDED':
        req_str(pub,'suspension_reason','publication',e)
        if not parse_dt(pub.get('suspended_at')): e.append('publication.suspended_at: required for SUSPENDED')
        if mstate not in {'SUSPENDED','REMOVED','INELIGIBLE'}: e.append('marketplace.marketplace_state: suspended passport cannot have active marketplace state')
    if state=='WITHDRAWN' and not str(pub.get('withdrawal_reason','')).strip(): e.append('publication.withdrawal_reason: required for WITHDRAWN')
    if state=='SUPERSEDED':
        if not str(pub.get('successor_passport_id','')).strip(): e.append('publication.successor_passport_id: required for SUPERSEDED')
        if not parse_dt(pub.get('superseded_at')): e.append('publication.superseded_at: required for SUPERSEDED')
    if state in {'EXPIRED','WITHDRAWN','SUPERSEDED','ARCHIVED'} and mstate in ACTIVE_MARKET: e.append('marketplace.marketplace_state: inactive passport cannot be marketplace active')

    if mstate in ACTIVE_MARKET:
        if state!='PUBLISHED': e.append('marketplace.marketplace_state: active marketplace requires PUBLISHED passport')
        if market.get('legal_review_status')!='COMPLETE': e.append('marketplace.legal_review_status: COMPLETE required')
        if market.get('regulatory_review_status')!='COMPLETE': e.append('marketplace.regulatory_review_status: COMPLETE required')
        if market.get('commercial_review_status')!='COMPLETE': e.append('marketplace.commercial_review_status: COMPLETE required')
        if market.get('supplier_authority_current') is not True: e.append('marketplace.supplier_authority_current: must be true')
        if unresolved_critical or unresolved_high: e.append('marketplace.marketplace_state: active state prohibited with unresolved high/critical event')
        req_str(market,'marketplace_decision_id','marketplace',e)
        req_str(market,'decided_by','marketplace',e)
        if not parse_dt(market.get('decided_at')): e.append('marketplace.decided_at: required for active state')
        if not parse_date(market.get('next_review_date')): e.append('marketplace.next_review_date: required for active state')
    if mstate=='CONDITIONALLY_ELIGIBLE':
        if not market.get('conditions'): e.append('marketplace.conditions: required for conditional eligibility')
        if not market.get('required_actions'): e.append('marketplace.required_actions: required for conditional eligibility')

    audit=data.get('audit')
    if not isinstance(audit,dict): e.append('audit: object required'); audit={}
    if not parse_dt(audit.get('created_at')): e.append('audit.created_at: valid date-time required')
    req_str(audit,'created_by','audit',e)
    if audit.get('immutable_record') is not True: e.append('audit.immutable_record: must be true')
    if audit.get('change_requires_new_version_or_event') is not True: e.append('audit.change_requires_new_version_or_event: must be true')
    return e

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('file')
    args=ap.parse_args(argv)
    try: data=json.loads(Path(args.file).read_text(encoding='utf-8'))
    except Exception as ex:
        print(f'FAIL: unable to read JSON: {ex}')
        return 2
    errors=validate(data)
    if errors:
        print(f'FAIL: {len(errors)} control breach(es)')
        for x in errors: print(f'- {x}')
        return 1
    print('PASS: lifecycle record satisfies CERT-BUILD-0035F semantic controls')
    return 0
if __name__=='__main__': raise SystemExit(main())
