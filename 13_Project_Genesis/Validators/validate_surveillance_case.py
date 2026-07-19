from __future__ import annotations
import sys
from control_library import load, human, parse_dt, require, output

def validate(d):
    e=[]
    require(e,d.get('record_type')=='surveillance_case','SUR-001','Wrong record type')
    for k in ['case_id','source','severity','traceability','privacy','triage','investigation','protective_actions','reporting_assessment','closure','audit']:
        require(e,k in d,'SUR-002-'+k.upper(),f'Missing {k}')
    sev=d.get('severity'); tr=d.get('traceability',{}); pr=d.get('privacy',{}); tri=d.get('triage',{}); inv=d.get('investigation',{}); pa=d.get('protective_actions',[]); ra=d.get('reporting_assessment',{}); cl=d.get('closure',{})
    require(e,sev in {'LOW','MODERATE','HIGH','CRITICAL'},'SUR-010','Invalid severity')
    require(e,pr.get('sensitive_data_minimised') is True,'SUR-020','Sensitive data must be minimised')
    require(e,pr.get('raw_medical_data_stored') is False,'SUR-021','Raw medical data must not be stored in analytical record')
    require(e,pr.get('customer_id_pseudonym'),'SUR-022','Pseudonymous customer key required')
    require(e,tri.get('status')=='COMPLETE','SUR-030','Triage must be complete')
    require(e,human(tri.get('reviewer')),'SUR-031','Triage reviewer must be human')
    require(e,parse_dt(tri.get('reviewed_at')) is not None,'SUR-032','Triage time required')
    require(e,tri.get('duplicate_check_complete') is True,'SUR-033','Duplicate check required')
    if sev in {'HIGH','CRITICAL'}:
        trace_ok=bool(tr.get('product_id') and tr.get('passport_id') and tr.get('batch_id')) or bool(tr.get('unavailable_reason'))
        require(e,trace_ok,'SUR-040','High/critical case requires traceability or reason unavailable')
        require(e,bool(pa),'SUR-041','High/critical case requires protective action')
        require(e,ra.get('status')=='COMPLETE','SUR-042','High/critical case requires completed reporting assessment')
        require(e,human(ra.get('decision_by')),'SUR-043','Reporting assessment must be human')
        require(e,parse_dt(ra.get('decision_at')) is not None,'SUR-044','Reporting decision time required')
        require(e,ra.get('jurisdiction'),'SUR-045','Reporting jurisdiction required')
        require(e,ra.get('reportability') in {'REQUIRED','NOT_REQUIRED'},'SUR-046','Reportability decision required')
    if sev=='CRITICAL':
        for action in ['BLOCK_BATCH','SUSPEND_LISTING','QUARANTINE_STOCK','NOTIFY_INCIDENT_COMMAND']:
            require(e,action in pa,'SUR-050-'+action, f'Critical case requires {action}')
        require(e,human(ra.get('independent_reviewer')),'SUR-055','Critical reporting assessment requires independent reviewer')
        if ra.get('reportability')=='REQUIRED':
            require(e,parse_dt(ra.get('due_at')) is not None,'SUR-056','Required report needs deadline')
    if cl.get('status')=='CLOSED':
        require(e,inv.get('status')=='COMPLETE','SUR-060','Closed case requires completed investigation')
        require(e,inv.get('root_cause'),'SUR-061','Closed case requires root cause or justified conclusion')
        require(e,bool(inv.get('capa_ids')),'SUR-062','Closed high/critical case requires corrective action')
        require(e,inv.get('effectiveness_check')=='COMPLETE','SUR-063','Closed case requires effectiveness check')
        require(e,human(cl.get('approved_by')),'SUR-064','Closure approval must be human')
        require(e,parse_dt(cl.get('approved_at')) is not None,'SUR-065','Closure approval time required')
        require(e,cl.get('rationale'),'SUR-066','Closure rationale required')
        if sev in {'HIGH','CRITICAL'}:
            require(e,human(cl.get('independent_approver')),'SUR-067','High/critical closure requires independent approver')
        require(e,ra.get('status')=='COMPLETE','SUR-068','Reporting assessment must be complete before closure')
        if ra.get('reportability')=='REQUIRED':
            require(e,ra.get('report_reference'),'SUR-069','Required report reference needed before closure')
    for a in d.get('audit',[]):
        if a.get('action') in {'AUTO_CLOSE','AUTO_REPORTABILITY_DECISION','AUTO_SUBMIT_REPORT'}:
            require(e,False,'SUR-070','Automation performed prohibited surveillance decision')
    return e
if __name__=='__main__':
    d=load(sys.argv[1]); sys.exit(output(d,validate(d)))
