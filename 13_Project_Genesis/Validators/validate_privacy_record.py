from __future__ import annotations
import sys
from control_library import load, human, parse_dt, require, output

def validate(d):
    e=[]
    require(e,d.get('record_type')=='privacy_request','PRV-001','Wrong record type')
    for k in ['request_id','customer_id','request_type','received_at','identity_confirmed','legal_review','decision','audit']:
        require(e,k in d,'PRV-002-'+k.upper(),f'Missing {k}')
    dec=d.get('decision',{}); lr=d.get('legal_review',{})
    require(e,parse_dt(d.get('received_at')) is not None,'PRV-010','Received time required')
    if dec.get('status') in {'COMPLETED','REFUSED_WITH_REASONS'}:
        require(e,d.get('identity_confirmed') is True,'PRV-020','Identity must be confirmed before closure')
        require(e,human(dec.get('decision_by')),'PRV-021','Privacy decision must be human')
        require(e,parse_dt(dec.get('decision_at')) is not None,'PRV-022','Decision time required')
        require(e,parse_dt(dec.get('closed_at')) is not None,'PRV-023','Closure time required')
        require(e,dec.get('reason'),'PRV-024','Closure reason required')
        require(e,parse_dt(dec.get('due_at')) is not None,'PRV-025','Due date required')
    if lr.get('required'):
        require(e,human(lr.get('reviewer')),'PRV-030','Required legal/privacy review must be human')
        require(e,parse_dt(lr.get('reviewed_at')) is not None,'PRV-031','Review date required')
        require(e,lr.get('basis'),'PRV-032','Review basis required')
    for a in d.get('audit',[]):
        if a.get('action') in {'AUTO_CLOSE','AUTO_REFUSE','AUTO_DELETE'} or not human(a.get('actor')):
            require(e,False,'PRV-040','Automation must not close, refuse or delete')
    return e
if __name__=='__main__':
    d=load(sys.argv[1]); sys.exit(output(d,validate(d)))
