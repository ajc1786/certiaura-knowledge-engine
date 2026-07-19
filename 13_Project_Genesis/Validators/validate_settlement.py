from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from control_library import load, nonempty, approvals_ok, cli_result

def validate(d):
    e=[]
    if d.get('record_type')!='SETTLEMENT_CASE': e.append('record_type must be SETTLEMENT_CASE')
    for k in ['settlement_id','supplier_id','linked_incident_id','status']:
        if not nonempty(d.get(k)): e.append(f'{k} is required')
    op=d.get('operational_prerequisites') or {}
    for k in ['incident_closed','recall_reconciled','returns_reconciled','capa_plan_approved']:
        if op.get(k) is not True: e.append(f'operational prerequisite {k} must be true')
    if op.get('open_disputes') is not False: e.append('open disputes must be false before final settlement')
    h=d.get('hold') or {}
    if h.get('status')!='RELEASED': e.append('payment hold must have controlled RELEASED status')
    if h.get('automation_released') is not False: e.append('payment hold cannot be released by automation')
    people=h.get('release_approved_by') or []
    roles={x.get('role') for x in people}
    if len({x.get('person_id') for x in people if x.get('person_id')})<2 or not {'FINANCE','QUALITY'}.issubset(roles): e.append('hold release requires distinct finance and quality approvals')
    if not nonempty(h.get('released_at')): e.append('hold release timestamp required')
    f=d.get('financials') or {}
    if not nonempty(f.get('currency')): e.append('currency required')
    for k in ['gross_exposure','recoveries','credits','write_off','final_settlement']:
        if not isinstance(f.get(k),(int,float)) or f.get(k)<0: e.append(f'{k} must be non-negative number')
    expected=round(f.get('gross_exposure',0)-f.get('recoveries',0)-f.get('credits',0)-f.get('write_off',0),2)
    if round(f.get('final_settlement',-1),2)!=expected: e.append('final settlement calculation does not reconcile')
    if f.get('tax_reviewed') is not True or f.get('calculation_verified') is not True: e.append('tax and calculation review required')
    if d.get('automation_approved') is not False: e.append('settlement cannot be automation-approved')
    if not approvals_ok(d.get('approvals') or [],['COMMERCIAL','FINANCE']): e.append('settlement requires distinct conflict-free commercial and finance approvals')
    if not d.get('continuing_obligations'): e.append('continuing obligations or explicit none statement required')
    if d.get('status')=='SETTLED' and not nonempty(d.get('closed_at')): e.append('settled case requires closed_at')
    return e
if __name__=='__main__': raise SystemExit(cli_result(validate(load(sys.argv[1]))))
