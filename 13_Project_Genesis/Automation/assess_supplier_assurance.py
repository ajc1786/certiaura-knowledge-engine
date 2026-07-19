from datetime import datetime, timedelta, timezone

POSITIVE = {'QUALIFIED','CONDITIONAL'}
BLOCKING = {'SUSPENDED','REJECTED','EXPIRED','WITHDRAWN'}
TIER_DAYS = {'LOW':365,'MODERATE':180,'HIGH':90,'CRITICAL':30}

def parse_dt(v):
    if not isinstance(v,str) or not v.strip(): return None
    try:
        return datetime.fromisoformat(v.replace('Z','+00:00'))
    except ValueError:
        return None

def score_and_tier(data):
    risk=data.get('risk_assessment') if isinstance(data.get('risk_assessment'),dict) else {}
    deductions=risk.get('component_deductions') if isinstance(risk.get('component_deductions'),dict) else {}
    total=max(0,min(100,100-sum(v for v in deductions.values() if isinstance(v,(int,float)))))
    critical=bool(risk.get('critical_flags'))
    if critical or total < 50: tier='CRITICAL'
    elif total < 70: tier='HIGH'
    elif total < 85: tier='MODERATE'
    else: tier='LOW'
    return int(total) if float(total).is_integer() else total, tier

def earliest_evidence_expiry(data):
    dd=data.get('due_diligence') if isinstance(data.get('due_diligence'),dict) else {}
    dates=[]
    for item in dd.get('evidence_items',[]) if isinstance(dd.get('evidence_items'),list) else []:
        d=parse_dt(item.get('expires_at')) if isinstance(item,dict) else None
        if d: dates.append(d)
    return min(dates) if dates else None

def calculate(data, as_of=None):
    as_of=as_of or datetime.now(timezone.utc)
    if as_of.tzinfo is None: as_of=as_of.replace(tzinfo=timezone.utc)
    score,tier=score_and_tier(data)
    q=data.get('qualification') if isinstance(data.get('qualification'),dict) else {}
    a=data.get('audit') if isinstance(data.get('audit'),dict) else {}
    ca=data.get('continuous_assurance') if isinstance(data.get('continuous_assurance'),dict) else {}
    dd=data.get('due_diligence') if isinstance(data.get('due_diligence'),dict) else {}
    triggers=ca.get('triggers') if isinstance(ca.get('triggers'),list) else []
    blockers=[]
    required={'LEGAL_REGISTRATION','OWNERSHIP_DECLARATION','QUALITY_SYSTEM','LAB_RELATIONSHIP','SUPPLY_CHAIN_TRACEABILITY','COMPLAINT_RECALL_PROCESS'}
    current=set()
    for item in dd.get('evidence_items',[]) if isinstance(dd.get('evidence_items'),list) else []:
        if isinstance(item,dict) and item.get('status')=='CURRENT': current.add(item.get('type'))
    missing=sorted(required-current)
    if dd.get('status')!='COMPLETE': blockers.append('DUE_DILIGENCE_INCOMPLETE')
    blockers += [f'MISSING_EVIDENCE:{x}' for x in missing]
    if tier=='CRITICAL': blockers.append('CRITICAL_RISK')
    if a.get('critical_findings',0): blockers.append('CRITICAL_AUDIT_FINDING')
    if a.get('major_findings',0): blockers.append('MAJOR_AUDIT_FINDING')
    if a.get('audit_status') in {'NOT_STARTED','OVERDUE','UNACCEPTABLE'}: blockers.append('AUDIT_NOT_ACCEPTABLE')
    open_critical=[t for t in triggers if isinstance(t,dict) and t.get('status')=='OPEN' and t.get('severity')=='CRITICAL']
    if open_critical: blockers.append('OPEN_CRITICAL_TRIGGER')
    if q.get('status') in BLOCKING: blockers.append(f'STATUS_{q.get("status")}')
    positive_ready=not blockers and tier in {'LOW','MODERATE'}
    if tier=='HIGH' and not any(x.startswith(('CRITICAL_','OPEN_CRITICAL')) for x in blockers):
        recommended='CONDITIONAL'
    elif tier=='CRITICAL' or open_critical or a.get('critical_findings',0):
        recommended='SUSPENDED'
    elif positive_ready:
        recommended='QUALIFIED'
    elif dd.get('status')!='COMPLETE':
        recommended='DUE_DILIGENCE'
    else:
        recommended='RESTRICTED'
    max_days=TIER_DAYS[tier]
    candidates=[as_of+timedelta(days=max_days)]
    exp=earliest_evidence_expiry(data)
    if exp: candidates.append(exp)
    eff=parse_dt(q.get('effective_until'))
    if eff: candidates.append(eff)
    next_due=min(candidates).isoformat()
    passport_allowed = recommended in {'QUALIFIED','CONDITIONAL'} and q.get('status') in {'QUALIFIED','CONDITIONAL'} and not open_critical
    marketplace_eligible = recommended=='QUALIFIED' and q.get('status')=='QUALIFIED' and tier in {'LOW','MODERATE'} and not blockers
    new_products_blocked = not passport_allowed or tier in {'HIGH','CRITICAL'}
    restrictions=[]
    if not passport_allowed: restrictions.append('BLOCK_NEW_PASSPORT_SUBMISSIONS')
    if not marketplace_eligible: restrictions.append('MARKETPLACE_NOT_ELIGIBLE')
    if new_products_blocked: restrictions.append('BLOCK_NEW_PRODUCTS')
    if tier in {'HIGH','CRITICAL'}: restrictions.append('ENHANCED_ASSURANCE')
    return {
      'calculated_score':score,
      'calculated_tier':tier,
      'recommended_qualification_status':recommended,
      'recommended_cadence_days':max_days,
      'recommended_next_review_due':next_due,
      'recommended_passport_submission_allowed':passport_allowed,
      'recommended_marketplace_supplier_eligible':marketplace_eligible,
      'recommended_new_products_blocked':new_products_blocked,
      'recommended_restrictions':sorted(set(restrictions)),
      'blockers':sorted(set(blockers)),
      'automatic_approval_prohibited':True,
    }
