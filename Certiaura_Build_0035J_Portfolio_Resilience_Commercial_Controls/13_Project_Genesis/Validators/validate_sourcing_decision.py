import argparse, importlib.util, json, re
from datetime import datetime
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
P=ROOT/'13_Project_Genesis'/'Automation'/'rank_sourcing_options.py'
spec=importlib.util.spec_from_file_location('ranker',P); ranker=importlib.util.module_from_spec(spec); spec.loader.exec_module(ranker)
REQ_CRITERIA={'assurance','quality','delivery','resilience','total_cost','service'}

def dt(v):
    if not isinstance(v,str) or not v: return None
    try: return datetime.fromisoformat(v.replace('Z','+00:00'))
    except ValueError: return None

def req(o,k,p,e):
    if not isinstance(o,dict) or o.get(k) in (None,'',[]): e.append(f'{p}.{k}: required')

def validate(data):
    e=[]
    if not isinstance(data,dict): return ['root: object required']
    for k in ['decision_id','version','requirement','criteria_weights','candidates','calculated_recommendation','decision','assurance_checks','sole_source_exception','conflicts','audit_trail']: req(data,k,'root',e)
    if len(str(data.get('decision_id','')))<8: e.append('decision_id: valid identifier required')
    if not re.match(r'^\d+\.\d+\.\d+$',str(data.get('version',''))): e.append('version: semantic version required')
    r=data.get('requirement') if isinstance(data.get('requirement'),dict) else {}
    for k in ['category_id','description','quantity','currency','required_by','approved_scope']: req(r,k,'requirement',e)
    if not isinstance(r.get('quantity'),(int,float)) or r.get('quantity',0)<=0: e.append('requirement.quantity: positive number required')
    if not dt(r.get('required_by')): e.append('requirement.required_by: valid date-time required')
    w=data.get('criteria_weights') if isinstance(data.get('criteria_weights'),dict) else {}
    if set(w)!=REQ_CRITERIA: e.append('criteria_weights: exact criteria set required')
    if any(not isinstance(v,(int,float)) or v<=0 for v in w.values()): e.append('criteria_weights: every criterion must have positive weight')
    if abs(sum(v for v in w.values() if isinstance(v,(int,float)))-100)>0.001: e.append('criteria_weights: weights must sum to 100')
    candidates=data.get('candidates') if isinstance(data.get('candidates'),list) else []
    if not candidates: e.append('candidates: non-empty array required')
    sole=data.get('sole_source_exception') if isinstance(data.get('sole_source_exception'),dict) else {}
    if len(candidates)<2:
        if sole.get('applies') is not True: e.append('candidates: at least two required unless approved sole-source exception applies')
        for k in ['reason','market_evidence','mitigation','owner_id','retest_due','approved_by']: req(sole,k,'sole_source_exception',e)
        if not dt(sole.get('retest_due')): e.append('sole_source_exception.retest_due: valid date-time required')
    ids=set()
    for i,c in enumerate(candidates):
        q=f'candidates[{i}]'
        if not isinstance(c,dict): e.append(f'{q}: object required'); continue
        for k in ['supplier_id','assurance_status','scope_current','scores','total_cost','weighted_score']: req(c,k,q,e)
        if not isinstance(c.get('blocking_flags'),list): e.append(f'{q}.blocking_flags: array required')
        if c.get('supplier_id') in ids: e.append(f'{q}.supplier_id: duplicate')
        ids.add(c.get('supplier_id'))
        if c.get('assurance_status') not in {'QUALIFIED','CONDITIONAL','RESTRICTED','SUSPENDED','EXPIRED','REJECTED'}: e.append(f'{q}.assurance_status: invalid')
        scores=c.get('scores') if isinstance(c.get('scores'),dict) else {}
        if set(scores)!=REQ_CRITERIA: e.append(f'{q}.scores: exact criteria set required')
        for k,v in scores.items():
            if not isinstance(v,(int,float)) or not 0<=v<=100: e.append(f'{q}.scores.{k}: 0-100 number required')
        expected=ranker.score_candidate(c,w)
        if c.get('weighted_score')!=expected: e.append(f'{q}.weighted_score: expected {expected}')
        if not isinstance(c.get('total_cost'),(int,float)) or c.get('total_cost',0)<=0: e.append(f'{q}.total_cost: positive number required')
    ranked=ranker.rank(data)
    cr=data.get('calculated_recommendation') if isinstance(data.get('calculated_recommendation'),dict) else {}
    if cr.get('supplier_id')!=ranked.get('recommended_supplier_id'): e.append(f'calculated_recommendation.supplier_id: expected {ranked.get("recommended_supplier_id")}')
    if cr.get('weighted_score')!=ranked.get('recommended_score'): e.append(f'calculated_recommendation.weighted_score: expected {ranked.get("recommended_score")}')
    if cr.get('recommendation_only') is not True: e.append('calculated_recommendation.recommendation_only: must be true')
    if not dt(cr.get('generated_at')): e.append('calculated_recommendation.generated_at: valid date-time required')
    if cr.get('engine_version')!='0035J-1.0.0': e.append('calculated_recommendation.engine_version: 0035J-1.0.0 required')
    d=data.get('decision') if isinstance(data.get('decision'),dict) else {}
    if d.get('status') not in {'PENDING','APPROVED','CONDITIONAL','REJECTED','CANCELLED','EXPIRED'}: e.append('decision.status: invalid')
    if d.get('automatic_award') is not False: e.append('decision.automatic_award: must be false')
    if d.get('price_only') is not False: e.append('decision.price_only: must be false')
    if d.get('status') in {'APPROVED','CONDITIONAL'}:
        for k in ['selected_supplier_id','rationale','reviewer_id','approver_id','decided_at','next_review_due']: req(d,k,'decision',e)
        if d.get('selected_supplier_id') not in ids: e.append('decision.selected_supplier_id: must be a candidate')
        if d.get('reviewer_id')==d.get('approver_id'): e.append('decision: reviewer and approver must differ')
        if not dt(d.get('decided_at')) or not dt(d.get('next_review_due')): e.append('decision: valid decision and review dates required')
        selected=next((c for c in candidates if isinstance(c,dict) and c.get('supplier_id')==d.get('selected_supplier_id')),{})
        if selected.get('assurance_status') not in {'QUALIFIED','CONDITIONAL'} or selected.get('scope_current') is not True or selected.get('blocking_flags'):
            e.append('decision: selected supplier must be current, in scope and free of blockers')
        if len(str(d.get('rationale',''))) < 40: e.append('decision.rationale: substantive multi-factor rationale required')
    checks=data.get('assurance_checks') if isinstance(data.get('assurance_checks'),dict) else {}
    for k in ['all_candidates_scope_checked','selected_supplier_current','product_evidence_separate','marketplace_eligibility_separate']:
        if checks.get(k) is not True: e.append(f'assurance_checks.{k}: true required')
    conflicts=data.get('conflicts') if isinstance(data.get('conflicts'),list) else []
    if not conflicts: e.append('conflicts: declarations required')
    for i,c in enumerate(conflicts):
        if not isinstance(c,dict) or c.get('declared') is not True: e.append(f'conflicts[{i}].declared: true required')
        if isinstance(c,dict) and c.get('conflict') is True and c.get('resolution') in (None,'','NONE'): e.append(f'conflicts[{i}].resolution: required for conflict')
    a=data.get('audit_trail') if isinstance(data.get('audit_trail'),dict) else {}
    if a.get('immutable_history') is not True: e.append('audit_trail.immutable_history: must be true')
    if not isinstance(a.get('events'),list) or not a.get('events'): e.append('audit_trail.events: non-empty array required')
    return e

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('file'); a=p.parse_args(argv); data=json.loads(Path(a.file).read_text(encoding='utf-8')); errors=validate(data)
    if errors:
        print(f'FAIL — {len(errors)} control breaches'); [print('- '+x) for x in errors]; return 1
    print('PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
