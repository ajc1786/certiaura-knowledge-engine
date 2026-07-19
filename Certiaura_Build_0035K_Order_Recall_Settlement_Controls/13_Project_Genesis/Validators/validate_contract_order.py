from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from control_library import load, nonempty, approvals_ok, cli_result
PASS_GATES={'supplier_assurance':'QUALIFIED','contract':'APPROVED','legal_route':'APPROVED','passport':'ACTIVE','marketplace':'ELIGIBLE','batch_evidence':'VERIFIED','incident_block':'CLEAR'}

def validate(d):
    e=[]
    if d.get('record_type')!='ORDER_ASSURANCE': e.append('record_type must be ORDER_ASSURANCE')
    for k in ['order_id','supplier_id','contract_id','product_passport_id','batch_id','jurisdiction']:
        if not nonempty(d.get(k)): e.append(f'{k} is required')
    c=d.get('contract') or {}
    if c.get('record_type')!='MARKETPLACE_CONTRACT': e.append('embedded approved contract record is required')
    if c.get('contract_id')!=d.get('contract_id'): e.append('contract_id mismatch')
    if c.get('supplier_id')!=d.get('supplier_id'): e.append('contract supplier mismatch')
    if c.get('status')!='APPROVED': e.append('contract must be APPROVED')
    if c.get('automation_approved') is not False: e.append('contract cannot be automation-approved')
    legal=(c.get('legal_route') or {})
    if legal.get('sale_route_status')!='APPROVED': e.append('jurisdiction-specific legal route must be APPROVED')
    for k in ['approval_reference','approved_by','approved_at']:
        if not nonempty(legal.get(k)): e.append(f'legal route {k} is required')
    terms=c.get('terms') or {}
    for k in ['quality_agreement','audit_rights','evidence_access','traceability_duties','recall_cooperation','payment_hold_rights','termination_rights']:
        if terms.get(k) is not True: e.append(f'contract term {k} must be true')
    if not approvals_ok(c.get('approvals') or [],['COMMERCIAL','QUALITY']): e.append('contract requires distinct conflict-free commercial and quality approvals')
    gates=d.get('gates') or {}
    for k,v in PASS_GATES.items():
        if gates.get(k)!=v: e.append(f'gate {k} must be {v}')
    lines=d.get('line_items') or []
    if not lines: e.append('at least one line item is required')
    for line in lines:
        if line.get('batch_id')!=d.get('batch_id'): e.append('line item batch must match order batch')
        if not isinstance(line.get('quantity'),(int,float)) or line.get('quantity',0)<=0: e.append('line quantity must be positive')
    price=d.get('pricing') or {}
    if not nonempty(price.get('currency')): e.append('pricing currency is required')
    if not isinstance(price.get('total'),(int,float)) or price.get('total',0)<0: e.append('pricing total must be non-negative')
    r=d.get('release_decision') or {}
    if r.get('status')!='RELEASED': e.append('valid example must record human RELEASED decision')
    if r.get('automation_approved') is not False: e.append('order release cannot be automation-approved')
    if not approvals_ok(r.get('approved_by') or [],['COMMERCIAL','QUALITY']): e.append('release requires distinct conflict-free commercial and quality approvals')
    if not nonempty(r.get('approved_at')): e.append('release timestamp is required')
    if not nonempty(r.get('gate_snapshot_hash')): e.append('gate snapshot hash is required')
    if (d.get('substitution') or {}).get('requested') and not (d.get('substitution') or {}).get('approved'): e.append('unapproved substitution voids release')
    if d.get('open_incidents'): e.append('open blocking incidents must be empty')
    return e
if __name__=='__main__': raise SystemExit(cli_result(validate(load(sys.argv[1]))))
