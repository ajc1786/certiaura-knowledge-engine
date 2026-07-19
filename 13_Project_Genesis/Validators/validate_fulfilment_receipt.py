from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from control_library import load, nonempty, cli_result

def validate(d):
    e=[]
    if d.get('record_type')!='FULFILMENT_RECEIPT': e.append('record_type must be FULFILMENT_RECEIPT')
    for k in ['shipment_id','order_id','supplier_id','product_passport_id','batch_id','carrier','dispatched_at','delivered_at']:
        if not nonempty(d.get(k)): e.append(f'{k} is required')
    custody=d.get('chain_of_custody') or []
    if len(custody)<2: e.append('at least dispatch and delivery custody events are required')
    seq=[x.get('sequence') for x in custody]
    if seq!=list(range(1,len(custody)+1)): e.append('chain-of-custody sequence must be complete and ordered')
    storage=d.get('storage') or {}; readings=storage.get('readings') or []
    if not readings: e.append('temperature/storage readings are required')
    lo,hi=storage.get('required_min_c'),storage.get('required_max_c')
    if lo is None or hi is None or lo>=hi: e.append('valid required storage range is required')
    detected=any(isinstance(x.get('c'),(int,float)) and (x['c']<lo or x['c']>hi) for x in readings) if lo is not None and hi is not None else False
    if detected != bool(storage.get('excursion_detected')): e.append('excursion flag must match readings')
    receipt=d.get('receipt') or {}
    for k in ['received_at','recipient_id']:
        if not nonempty(receipt.get(k)): e.append(f'receipt {k} is required')
    if receipt.get('identity_match') is not True: e.append('product identity must match')
    if receipt.get('batch_match') is not True: e.append('batch must match')
    if receipt.get('quantity_received')!=receipt.get('quantity_ordered'): e.append('quantity discrepancy requires separate controlled record')
    if (d.get('tamper_evidence') or {}).get('intact') is not True: e.append('tamper evidence must be intact or quarantined with exception control')
    disp=d.get('disposition') or {}
    if disp.get('automation_approved') is not False: e.append('disposition cannot be automation-approved')
    if not nonempty(disp.get('decision_by')) or not nonempty(disp.get('decision_at')): e.append('named human disposition and timestamp are required')
    if detected:
        if disp.get('quarantined') is not True: e.append('excursion requires quarantine')
        if disp.get('status') not in ['ACCEPTED_WITH_JUSTIFICATION','REJECTED','RETURNED','DESTROYED']: e.append('excursion requires controlled disposition')
        if not nonempty(disp.get('rationale')) or not (disp.get('evidence_refs') or []): e.append('excursion disposition requires rationale and evidence')
    return e
if __name__=='__main__': raise SystemExit(cli_result(validate(load(sys.argv[1]))))
