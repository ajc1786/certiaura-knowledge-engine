import argparse, importlib.util, json, re
from datetime import datetime
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
P=ROOT/'13_Project_Genesis'/'Automation'/'portfolio_analytics.py'
spec=importlib.util.spec_from_file_location('analytics',P); analytics=importlib.util.module_from_spec(spec); spec.loader.exec_module(analytics)
POSITIVE={'QUALIFIED','CONDITIONAL'}; BLOCKED={'SUSPENDED','REJECTED','EXPIRED','WITHDRAWN','RESTRICTED'}

def dt(v):
    if not isinstance(v,str) or not v: return None
    try: return datetime.fromisoformat(v.replace('Z','+00:00'))
    except ValueError: return None

def req(o,k,p,e):
    if not isinstance(o,dict) or o.get(k) in (None,'',[]): e.append(f'{p}.{k}: required')

def validate(data):
    e=[]
    if not isinstance(data,dict): return ['root: object required']
    for k in ['record_id','version','as_of','portfolio','suppliers','categories','concentration','resilience','governance','audit_trail']: req(data,k,'root',e)
    if len(str(data.get('record_id','')))<8: e.append('record_id: valid identifier required')
    if not re.match(r'^\d+\.\d+\.\d+$',str(data.get('version',''))): e.append('version: semantic version required')
    if not dt(data.get('as_of')): e.append('as_of: valid date-time required')
    p=data.get('portfolio') if isinstance(data.get('portfolio'),dict) else {}
    for k in ['portfolio_id','name','owner_id','currency','annual_spend','review_frequency_days']: req(p,k,'portfolio',e)
    if not isinstance(p.get('annual_spend'),(int,float)) or p.get('annual_spend',0)<=0: e.append('portfolio.annual_spend: positive number required')
    if not isinstance(p.get('review_frequency_days'),int) or p.get('review_frequency_days',0)<1: e.append('portfolio.review_frequency_days: positive integer required')
    suppliers=data.get('suppliers') if isinstance(data.get('suppliers'),list) else []
    if not suppliers: e.append('suppliers: non-empty array required')
    total_spend=0; total_pct=0; supplier_ids=set()
    for i,s in enumerate(suppliers):
        q=f'suppliers[{i}]'
        if not isinstance(s,dict): e.append(f'{q}: object required'); continue
        for k in ['supplier_id','legal_name','assurance_status','approved_scope_status','panel_status','annual_spend','spend_percent','performance','sla','commercial','continuity','marketplace']: req(s,k,q,e)
        sid=s.get('supplier_id');
        if sid in supplier_ids: e.append(f'{q}.supplier_id: duplicate')
        supplier_ids.add(sid)
        if s.get('assurance_status') not in {'QUALIFIED','CONDITIONAL','RESTRICTED','SUSPENDED','REJECTED','EXPIRED','WITHDRAWN'}: e.append(f'{q}.assurance_status: invalid')
        if not isinstance(s.get('annual_spend'),(int,float)) or s.get('annual_spend',-1)<0: e.append(f'{q}.annual_spend: non-negative number required')
        else: total_spend += s.get('annual_spend')
        if not isinstance(s.get('spend_percent'),(int,float)) or not 0<=s.get('spend_percent',-1)<=100: e.append(f'{q}.spend_percent: 0-100 number required')
        else: total_pct += s.get('spend_percent')
        perf=s.get('performance') if isinstance(s.get('performance'),dict) else {}
        for k in ['quality_score','delivery_score','responsiveness_score','evidence_score']:
            if not isinstance(perf.get(k),(int,float)) or not 0<=perf.get(k,-1)<=100: e.append(f'{q}.performance.{k}: 0-100 number required')
        if not isinstance(perf.get('sample_size'),int) or perf.get('sample_size',0)<1: e.append(f'{q}.performance.sample_size: positive integer required')
        sla=s.get('sla') if isinstance(s.get('sla'),dict) else {}
        for k in ['on_time_in_full_percent','target_on_time_in_full_percent']:
            if not isinstance(sla.get(k),(int,float)) or not 0<=sla.get(k,-1)<=100: e.append(f'{q}.sla.{k}: 0-100 number required')
        com=s.get('commercial') if isinstance(s.get('commercial'),dict) else {}
        cost_keys=['purchase_cost','landed_cost','assurance_cost','operational_cost','risk_adjusted_cost','exit_cost']
        for k in cost_keys+['total_cost']:
            if not isinstance(com.get(k),(int,float)) or com.get(k,-1)<0: e.append(f'{q}.commercial.{k}: non-negative number required')
        calc_total=round(sum(float(com.get(k,0)) for k in cost_keys),2)
        if isinstance(com.get('total_cost'),(int,float)) and abs(com.get('total_cost')-calc_total)>0.02: e.append(f'{q}.commercial.total_cost: expected {calc_total}')
        cont=s.get('continuity') if isinstance(s.get('continuity'),dict) else {}
        if cont.get('bcp_status') not in {'TESTED','DOCUMENTED','NOT_TESTED','FAILED','NOT_APPLICABLE'}: e.append(f'{q}.continuity.bcp_status: invalid')
        if cont.get('bcp_status')=='TESTED' and not dt(cont.get('last_tested_at')): e.append(f'{q}.continuity.last_tested_at: valid date-time required')
        m=s.get('marketplace') if isinstance(s.get('marketplace'),dict) else {}
        if m.get('commercial_eligible') is True:
            if s.get('assurance_status')!='QUALIFIED': e.append(f'{q}.marketplace: eligibility requires QUALIFIED supplier')
            for k in ['decision_id','reviewer_id','approver_id','decided_at']: req(m,k,f'{q}.marketplace',e)
            if m.get('reviewer_id')==m.get('approver_id'): e.append(f'{q}.marketplace: reviewer and approver must differ')
            if not dt(m.get('decided_at')): e.append(f'{q}.marketplace.decided_at: valid date-time required')
        if s.get('assurance_status') in BLOCKED and m.get('commercial_eligible') is True: e.append(f'{q}.marketplace: blocked supplier cannot be eligible')
    if isinstance(p.get('annual_spend'),(int,float)) and abs(total_spend-p.get('annual_spend'))>0.02: e.append(f'suppliers.annual_spend: total {total_spend} must equal portfolio {p.get("annual_spend")}')
    if abs(total_pct-100)>0.05: e.append(f'suppliers.spend_percent: total must equal 100, got {round(total_pct,2)}')
    for s in suppliers:
        if isinstance(p.get('annual_spend'),(int,float)) and p.get('annual_spend',0)>0 and isinstance(s,dict) and isinstance(s.get('annual_spend'),(int,float)) and isinstance(s.get('spend_percent'),(int,float)):
            expected=round(s.get('annual_spend')/p.get('annual_spend')*100,2)
            if abs(expected-s.get('spend_percent'))>0.05: e.append(f'supplier {s.get("supplier_id")}: spend_percent expected {expected}')
    categories=data.get('categories') if isinstance(data.get('categories'),list) else []
    if not categories: e.append('categories: non-empty array required')
    for i,c in enumerate(categories):
        q=f'categories[{i}]'
        if not isinstance(c,dict): e.append(f'{q}: object required'); continue
        for k in ['category_id','name','critical','annual_spend','primary_supplier_id','approved_supplier_ids','sole_source','owner_id','next_review_due']: req(c,k,q,e)
        if not isinstance(c.get('active_alternatives'),list): e.append(f'{q}.active_alternatives: array required')
        if c.get('primary_supplier_id') not in supplier_ids: e.append(f'{q}.primary_supplier_id: unknown supplier')
        for sid in c.get('approved_supplier_ids',[]) if isinstance(c.get('approved_supplier_ids'),list) else []:
            if sid not in supplier_ids: e.append(f'{q}.approved_supplier_ids: unknown supplier {sid}')
        if c.get('critical') is True and not c.get('active_alternatives'):
            mit=c.get('mitigation') if isinstance(c.get('mitigation'),dict) else {}
            for k in ['status','reason','owner_id','due_at','approved_by','market_retest_due']: req(mit,k,f'{q}.mitigation',e)
            if mit.get('status')!='APPROVED': e.append(f'{q}.mitigation.status: APPROVED required')
            if not dt(mit.get('due_at')) or not dt(mit.get('market_retest_due')): e.append(f'{q}.mitigation: valid due dates required')
        if not dt(c.get('next_review_due')): e.append(f'{q}.next_review_due: valid date-time required')
    calc=analytics.calculate_metrics(data)
    conc=data.get('concentration') if isinstance(data.get('concentration'),dict) else {}
    for k,v in calc.items():
        if conc.get(k)!=v: e.append(f'concentration.{k}: expected {v}')
    if not dt(conc.get('calculated_at')): e.append('concentration.calculated_at: valid date-time required')
    if conc.get('calculation_source')!='PROJECT_GENESIS': e.append('concentration.calculation_source: PROJECT_GENESIS required')
    res=data.get('resilience') if isinstance(data.get('resilience'),dict) else {}
    expected_rating=analytics.resilience_rating(data)
    if res.get('rating')!=expected_rating: e.append(f'resilience.rating: expected {expected_rating}')
    req(res,'owner_id','resilience',e)
    if not dt(res.get('next_review_due')): e.append('resilience.next_review_due: valid date-time required')
    if expected_rating=='RED' and not res.get('open_actions'): e.append('resilience.open_actions: RED rating requires actions')
    g=data.get('governance') if isinstance(data.get('governance'),dict) else {}
    if g.get('calculated_only') is not True: e.append('governance.calculated_only: must be true')
    if g.get('human_review_required') is not True: e.append('governance.human_review_required: must be true')
    if g.get('automatic_award') is not False: e.append('governance.automatic_award: must be false')
    for k in ['reviewer_id','approver_id','reviewed_at']: req(g,k,'governance',e)
    if g.get('reviewer_id')==g.get('approver_id'): e.append('governance: reviewer and approver must differ')
    if not dt(g.get('reviewed_at')): e.append('governance.reviewed_at: valid date-time required')
    if g.get('conflicts_declared') is not True: e.append('governance.conflicts_declared: true required')
    a=data.get('audit_trail') if isinstance(data.get('audit_trail'),dict) else {}
    if a.get('immutable_history') is not True: e.append('audit_trail.immutable_history: must be true')
    if not isinstance(a.get('events'),list) or not a.get('events'): e.append('audit_trail.events: non-empty array required')
    return e

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('file'); a=p.parse_args(argv)
    data=json.loads(Path(a.file).read_text(encoding='utf-8')); errors=validate(data)
    if errors:
        print(f'FAIL — {len(errors)} control breaches'); [print('- '+x) for x in errors]; return 1
    print('PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
