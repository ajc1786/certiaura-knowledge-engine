import argparse, importlib.util, json, re
from pathlib import Path
from datetime import datetime, timezone

HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
AP=ROOT/'13_Project_Genesis'/'Automation'/'assess_supplier_assurance.py'
spec=importlib.util.spec_from_file_location('assessment_engine',AP); assessment_engine=importlib.util.module_from_spec(spec); spec.loader.exec_module(assessment_engine)

HASH=re.compile(r'^[0-9a-f]{64}$')
POSITIVE_STATUS={'QUALIFIED','CONDITIONAL'}
POSITIVE_DECISION={'APPROVED','CONDITIONAL'}
BLOCKED_STATUS={'SUSPENDED','REJECTED','EXPIRED','WITHDRAWN'}
REQ_EVIDENCE={'LEGAL_REGISTRATION','OWNERSHIP_DECLARATION','QUALITY_SYSTEM','LAB_RELATIONSHIP','SUPPLY_CHAIN_TRACEABILITY','COMPLAINT_RECALL_PROCESS'}
TIER_DAYS={'LOW':365,'MODERATE':180,'HIGH':90,'CRITICAL':30}

def dt(v):
    if not isinstance(v,str) or not v.strip(): return None
    try: return datetime.fromisoformat(v.replace('Z','+00:00'))
    except ValueError: return None

def req(obj,key,path,e):
    if not isinstance(obj,dict) or key not in obj or obj.get(key) in (None,'',[]): e.append(f'{path}.{key}: required')

def validate(data):
    e=[]
    if not isinstance(data,dict): return ['root: object required']
    for k in ['record_id','version','supplier','scope','due_diligence','risk_assessment','qualification','audit','continuous_assurance','restrictions','integration','assessment','audit_trail']:
        req(data,k,'root',e)
    if not isinstance(data.get('record_id'),str) or len(data.get('record_id',''))<8: e.append('record_id: valid identifier required')
    if not re.match(r'^\d+\.\d+\.\d+$',str(data.get('version',''))): e.append('version: semantic version required')

    s=data.get('supplier') if isinstance(data.get('supplier'),dict) else {}
    for k in ['supplier_id','legal_name','registration_country','company_number','roles','primary_contact']:
        req(s,k,'supplier',e)
    if not re.match(r'^[A-Z]{2}$',str(s.get('registration_country',''))): e.append('supplier.registration_country: ISO alpha-2 code required')
    if not isinstance(s.get('roles'),list) or not s.get('roles'): e.append('supplier.roles: at least one role required')
    for k in ['ownership_declared','beneficial_owners_declared','subcontractors_declared']:
        if s.get(k) is not True: e.append(f'supplier.{k}: true declaration required')
    pc=s.get('primary_contact') if isinstance(s.get('primary_contact'),dict) else {}
    req(pc,'name','supplier.primary_contact',e); req(pc,'email','supplier.primary_contact',e)

    scope=data.get('scope') if isinstance(data.get('scope'),dict) else {}
    for k in ['product_categories','activities','regions','sites']:
        if not isinstance(scope.get(k),list) or not scope.get(k): e.append(f'scope.{k}: non-empty array required')
    for i,site in enumerate(scope.get('sites',[]) if isinstance(scope.get('sites'),list) else []):
        if not isinstance(site,dict): e.append(f'scope.sites[{i}]: object required'); continue
        for k in ['site_id','name','country','activities']: req(site,k,f'scope.sites[{i}]',e)

    dd=data.get('due_diligence') if isinstance(data.get('due_diligence'),dict) else {}
    if dd.get('status') not in {'ONBOARDING','INCOMPLETE','COMPLETE','EXPIRED','DISPUTED'}: e.append('due_diligence.status: invalid')
    if dd.get('status')=='COMPLETE' and not dt(dd.get('completed_at')): e.append('due_diligence.completed_at: required when complete')
    items=dd.get('evidence_items') if isinstance(dd.get('evidence_items'),list) else []
    if not items: e.append('due_diligence.evidence_items: non-empty array required')
    current=set()
    for i,x in enumerate(items):
        p=f'due_diligence.evidence_items[{i}]'
        if not isinstance(x,dict): e.append(f'{p}: object required'); continue
        for k in ['evidence_id','type','issuer','issued_at','sha256','status','supplier_provided','verified_by','verified_at','scope']:
            req(x,k,p,e)
        if not dt(x.get('issued_at')): e.append(f'{p}.issued_at: valid date-time required')
        if x.get('expires_at') is not None and not dt(x.get('expires_at')): e.append(f'{p}.expires_at: valid date-time or null required')
        if not HASH.match(str(x.get('sha256',''))): e.append(f'{p}.sha256: lowercase SHA-256 required')
        if x.get('status') not in {'CURRENT','EXPIRING','EXPIRED','WITHDRAWN','DISPUTED','SUPERSEDED'}: e.append(f'{p}.status: invalid')
        if not dt(x.get('verified_at')): e.append(f'{p}.verified_at: valid date-time required')
        if x.get('status')=='CURRENT': current.add(x.get('type'))
    missing=sorted(REQ_EVIDENCE-current)
    if missing: e.append('due_diligence.evidence_items: missing current mandatory categories '+','.join(missing))
    dec=dd.get('declarations') if isinstance(dd.get('declarations'),dict) else {}
    for k in ['conflicts_disclosed','regulatory_actions_disclosed','data_integrity_commitment','subcontractors_disclosed']:
        if dec.get(k) is not True: e.append(f'due_diligence.declarations.{k}: true required')

    r=data.get('risk_assessment') if isinstance(data.get('risk_assessment'),dict) else {}
    if not dt(r.get('as_of')): e.append('risk_assessment.as_of: valid date-time required')
    ded=r.get('component_deductions') if isinstance(r.get('component_deductions'),dict) else {}
    required_components={'identity','quality_system','data_integrity','laboratory_assurance','traceability','incident_handling','responsiveness','resilience'}
    if set(ded)!=required_components: e.append('risk_assessment.component_deductions: exact component set required')
    for k,v in ded.items():
        if not isinstance(v,(int,float)) or v<0 or v>100: e.append(f'risk_assessment.component_deductions.{k}: 0-100 number required')
    calc_score,calc_tier=assessment_engine.score_and_tier(data)
    if r.get('score')!=calc_score: e.append(f'risk_assessment.score: expected {calc_score}')
    if r.get('tier')!=calc_tier: e.append(f'risk_assessment.tier: expected {calc_tier}')
    if not isinstance(r.get('critical_flags'),list): e.append('risk_assessment.critical_flags: array required')
    req(r,'human_confirmed_by','risk_assessment',e)
    if not dt(r.get('confirmed_at')): e.append('risk_assessment.confirmed_at: valid date-time required')
    req(r,'rationale','risk_assessment',e)

    q=data.get('qualification') if isinstance(data.get('qualification'),dict) else {}
    valid_status={'PROSPECT','ONBOARDING','DUE_DILIGENCE','RISK_REVIEW','AUDIT_REQUIRED','CONDITIONAL','QUALIFIED','RESTRICTED','SUSPENDED','REJECTED','EXPIRED','WITHDRAWN'}
    if q.get('status') not in valid_status: e.append('qualification.status: invalid')
    if q.get('decision') not in {'PENDING','APPROVED','CONDITIONAL','RESTRICTED','SUSPENDED','REJECTED','EXPIRED','WITHDRAWN'}: e.append('qualification.decision: invalid')
    if q.get('automatic_positive_action') is not False: e.append('qualification.automatic_positive_action: must be false')
    if q.get('status') in POSITIVE_STATUS or q.get('decision') in POSITIVE_DECISION:
        if dd.get('status')!='COMPLETE': e.append('qualification: complete due diligence required')
        if missing: e.append('qualification: all mandatory evidence categories must be current')
        if calc_tier=='CRITICAL' or r.get('critical_flags'): e.append('qualification: critical risk prohibits positive decision')
        for k in ['primary_reviewer_id','second_approver_id','decided_at','effective_from','effective_until']:
            if k.endswith('_at') or k.startswith('effective_'):
                if not dt(q.get(k)): e.append(f'qualification.{k}: valid date-time required')
            else: req(q,k,'qualification',e)
        if q.get('primary_reviewer_id')==q.get('second_approver_id'): e.append('qualification: primary reviewer and second approver must differ')
        if not isinstance(q.get('scope_approved'),list) or not q.get('scope_approved'): e.append('qualification.scope_approved: non-empty array required')
        if q.get('status')=='CONDITIONAL' and (not isinstance(q.get('conditions'),list) or not q.get('conditions')): e.append('qualification.conditions: conditional status requires conditions')
    if q.get('status') in BLOCKED_STATUS and q.get('decision') in POSITIVE_DECISION: e.append('qualification: blocked status cannot have positive decision')

    a=data.get('audit') if isinstance(data.get('audit'),dict) else {}
    if a.get('required') is not True: e.append('audit.required: must be true')
    if a.get('audit_status') not in {'NOT_STARTED','PLANNED','IN_PROGRESS','CLOSED_ACCEPTABLE','CLOSED_CONDITIONAL','OVERDUE','UNACCEPTABLE'}: e.append('audit.audit_status: invalid')
    for k in ['open_findings','critical_findings','major_findings']:
        if not isinstance(a.get(k),int) or a.get(k)<0: e.append(f'audit.{k}: non-negative integer required')
    if not dt(a.get('next_audit_due')): e.append('audit.next_audit_due: valid date-time required')
    if not isinstance(a.get('cadence_days'),int) or a.get('cadence_days')<1: e.append('audit.cadence_days: positive integer required')
    elif a.get('cadence_days')>TIER_DAYS.get(calc_tier,30): e.append(f'audit.cadence_days: must be <= {TIER_DAYS.get(calc_tier,30)} for tier')
    if q.get('status') in POSITIVE_STATUS:
        if a.get('audit_status') not in {'CLOSED_ACCEPTABLE','CLOSED_CONDITIONAL'}: e.append('qualification: positive status requires acceptable audit status')
        if a.get('critical_findings',0)>0: e.append('qualification: critical audit findings prohibit positive status')
        if q.get('status')=='QUALIFIED' and a.get('major_findings',0)>0: e.append('qualification: major findings prohibit unqualified positive status')
    findings=a.get('findings') if isinstance(a.get('findings'),list) else []
    if len([x for x in findings if isinstance(x,dict) and x.get('status')!='CLOSED']) != a.get('open_findings'): e.append('audit.open_findings: does not reconcile with findings')

    ca=data.get('continuous_assurance') if isinstance(data.get('continuous_assurance'),dict) else {}
    if ca.get('monitoring_status') not in {'PENDING','ACTIVE','ENHANCED','PAUSED','STOPPED'}: e.append('continuous_assurance.monitoring_status: invalid')
    if not dt(ca.get('next_review_due')): e.append('continuous_assurance.next_review_due: valid date-time required')
    if not dt(ca.get('last_monitoring_run')): e.append('continuous_assurance.last_monitoring_run: valid date-time required')
    for k in ['document_expiry_watch','incident_watch','ownership_change_watch','laboratory_change_watch']:
        if ca.get(k) is not True: e.append(f'continuous_assurance.{k}: must be true')
    triggers=ca.get('triggers') if isinstance(ca.get('triggers'),list) else []
    if not isinstance(ca.get('triggers'),list): e.append('continuous_assurance.triggers: array required')
    open_critical=[]
    for i,t in enumerate(triggers):
        p=f'continuous_assurance.triggers[{i}]'
        if not isinstance(t,dict): e.append(f'{p}: object required'); continue
        for k in ['trigger_id','type','severity','status','detected_at','source']: req(t,k,p,e)
        if t.get('severity') not in {'LOW','MODERATE','HIGH','CRITICAL'}: e.append(f'{p}.severity: invalid')
        if t.get('status') not in {'OPEN','UNDER_REVIEW','CLOSED','SUPERSEDED'}: e.append(f'{p}.status: invalid')
        if not dt(t.get('detected_at')): e.append(f'{p}.detected_at: valid date-time required')
        if t.get('severity')=='CRITICAL' and t.get('status') in {'OPEN','UNDER_REVIEW'}: open_critical.append(t)

    restr=data.get('restrictions') if isinstance(data.get('restrictions'),dict) else {}
    for k in ['passport_submission_allowed','marketplace_supplier_eligible','new_products_blocked']:
        if not isinstance(restr.get(k),bool): e.append(f'restrictions.{k}: boolean required')
    if not isinstance(restr.get('active_restrictions'),list): e.append('restrictions.active_restrictions: array required')
    if q.get('status') in BLOCKED_STATUS or open_critical or calc_tier=='CRITICAL':
        if restr.get('passport_submission_allowed') is not False: e.append('restrictions.passport_submission_allowed: must be false for blocked or critical supplier')
        if restr.get('marketplace_supplier_eligible') is not False: e.append('restrictions.marketplace_supplier_eligible: must be false for blocked or critical supplier')
        if restr.get('new_products_blocked') is not True: e.append('restrictions.new_products_blocked: must be true for blocked or critical supplier')
    if q.get('status')=='CONDITIONAL' and restr.get('marketplace_supplier_eligible') is not False: e.append('restrictions.marketplace_supplier_eligible: conditional supplier requires separate negative default')
    if q.get('status') not in POSITIVE_STATUS and restr.get('passport_submission_allowed') is True: e.append('restrictions.passport_submission_allowed: positive supplier status required')

    integ=data.get('integration') if isinstance(data.get('integration'),dict) else {}
    for k in ['supplier_register_status','product_passport_records','downstream_review_required']:
        req(integ,k,'integration',e)
    if not isinstance(integ.get('product_passport_records'),list): e.append('integration.product_passport_records: array required')
    if (open_critical or q.get('status') in {'RESTRICTED','SUSPENDED','REJECTED','EXPIRED'}) and integ.get('downstream_review_required') is not True: e.append('integration.downstream_review_required: true required for adverse status or critical trigger')

    assess=data.get('assessment') if isinstance(data.get('assessment'),dict) else {}
    if not assess: e.append('assessment: object required')
    calc_at=dt(assess.get('calculated_at'))
    if not calc_at: e.append('assessment.calculated_at: valid date-time required'); calc_at=datetime.now(timezone.utc)
    calculated=assessment_engine.calculate(data,as_of=calc_at)
    for k in ['calculated_score','calculated_tier','recommended_qualification_status','recommended_cadence_days','recommended_passport_submission_allowed','recommended_marketplace_supplier_eligible','recommended_new_products_blocked','automatic_approval_prohibited']:
        if assess.get(k)!=calculated.get(k): e.append(f'assessment.{k}: expected {calculated.get(k)!r}')
    if sorted(assess.get('recommended_restrictions',[]))!=sorted(calculated.get('recommended_restrictions',[])): e.append('assessment.recommended_restrictions: does not reconcile')
    if sorted(assess.get('blockers',[]))!=sorted(calculated.get('blockers',[])): e.append('assessment.blockers: does not reconcile')
    if assess.get('recommended_next_review_due')!=calculated.get('recommended_next_review_due'): e.append('assessment.recommended_next_review_due: does not reconcile')

    at=data.get('audit_trail') if isinstance(data.get('audit_trail'),dict) else {}
    for k in ['created_at','updated_at']:
        if not dt(at.get(k)): e.append(f'audit_trail.{k}: valid date-time required')
    for k in ['created_by','updated_by']: req(at,k,'audit_trail',e)
    if at.get('immutable_history') is not True: e.append('audit_trail.immutable_history: must be true')
    if at.get('source_records_hashed') is not True: e.append('audit_trail.source_records_hashed: must be true')
    if at.get('approval_separation_enforced') is not True: e.append('audit_trail.approval_separation_enforced: must be true')
    if not isinstance(at.get('change_history'),list): e.append('audit_trail.change_history: array required')
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
    print('PASS: supplier assurance record satisfies CERT-BUILD-0035I semantic controls')
    return 0

if __name__=='__main__': raise SystemExit(main())
