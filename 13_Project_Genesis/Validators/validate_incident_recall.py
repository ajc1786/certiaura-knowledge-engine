from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from control_library import load, nonempty, approvals_ok, cli_result

def validate(d):
    e=[]
    if d.get('record_type')!='INCIDENT_RECALL_CASE': e.append('record_type must be INCIDENT_RECALL_CASE')
    for k in ['incident_id','severity','status','source']:
        if not nonempty(d.get(k)): e.append(f'{k} is required')
    if d.get('severity') not in ['LOW','MEDIUM','HIGH','CRITICAL']: e.append('severity is invalid')
    scope=d.get('affected_scope') or {}
    if d.get('severity') in ['HIGH','CRITICAL']:
        for k in ['products','batches','orders','recipients']:
            if not scope.get(k): e.append(f'high/critical incident requires affected {k}')
        if not isinstance(scope.get('population'),int) or scope.get('population',0)<=0: e.append('affected population must be positive')
    trace=d.get('traceability') or {}
    if trace.get('upstream_complete') is not True: e.append('upstream traceability must be complete')
    if trace.get('downstream_complete') is not True: e.append('downstream traceability must be complete')
    if trace.get('completeness_percent')!=100: e.append('traceability completeness must be 100% or recall scope expanded protectively')
    actions=d.get('protective_actions') or {}
    if d.get('severity')=='CRITICAL':
        for k in ['passport_restricted','marketplace_suspended','order_blocked','payment_hold','stock_quarantined']:
            if actions.get(k) is not True: e.append(f'critical incident requires protective action {k}')
    cmd=d.get('incident_command') or {}
    if not nonempty(cmd.get('commander_id')) or not nonempty(cmd.get('appointed_at')): e.append('incident commander and appointment time required')
    r=d.get('recall_decision') or {}
    if r.get('automation_initiated') is not False: e.append('recall cannot be initiated or controlled by automation')
    if r.get('status') not in ['INITIATED','ACTIVE','COMPLETED_PENDING_CLOSURE']: e.append('recall decision status is invalid for open case')
    if not nonempty(r.get('scope')) or r.get('depth')=='NONE': e.append('recall scope and depth are required')
    if not approvals_ok(r.get('approved_by') or [],['INCIDENT_COMMAND','QUALITY']): e.append('recall requires distinct conflict-free incident command and quality approvals')
    if not nonempty(r.get('approved_at')): e.append('recall approval timestamp required')
    reg=d.get('regulatory_assessment') or {}
    if reg.get('required') and reg.get('status')!='COMPLETED': e.append('required regulatory assessment must be completed')
    notes=d.get('notifications') or []
    if len(notes)<scope.get('population',0): e.append('notifications must cover affected population')
    if not d.get('effectiveness_checks'): e.append('effectiveness checks are required')
    if not d.get('capa_ids'): e.append('corrective/preventive action linkage is required')
    closure=d.get('closure') or {}
    if closure.get('automation_closed') is not False: e.append('incident/recall cannot be automation-closed')
    if d.get('status')=='CLOSED' and not approvals_ok(closure.get('approved_by') or [],['INCIDENT_COMMAND','QUALITY']): e.append('closure requires human approvals')
    return e
if __name__=='__main__': raise SystemExit(cli_result(validate(load(sys.argv[1]))))
