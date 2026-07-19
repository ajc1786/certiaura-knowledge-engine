from __future__ import annotations
import sys
from control_library import load, human, parse_dt, require, output

def validate(d):
    e=[]
    require(e,d.get('record_type')=='customer_eligibility','ELG-001','Wrong record type')
    for k in ['eligibility_id','customer_id','customer_type','jurisdiction','identity_verification','intended_use','privacy','access','risk','decision']:
        require(e,k in d,'ELG-002-'+k.upper(),f'Missing {k}')
    j=d.get('jurisdiction',{}); iv=d.get('identity_verification',{}); iu=d.get('intended_use',{}); p=d.get('privacy',{}); a=d.get('access',{}); r=d.get('risk',{}); dec=d.get('decision',{})
    approved=dec.get('status') in {'ELIGIBLE','CONDITIONAL'}
    require(e,j.get('country_code'),'ELG-010','Jurisdiction country code required')
    require(e,j.get('route_status') in {'APPROVED','PENDING','RESTRICTED','PROHIBITED'},'ELG-011','Invalid route status')
    if approved:
        require(e,j.get('route_status')=='APPROVED','ELG-012','Approved eligibility requires APPROVED route')
        require(e,j.get('legal_review_id'),'ELG-013','Legal review identifier required')
        require(e,parse_dt(j.get('review_due')) is not None,'ELG-014','Legal review due date required')
        require(e,iv.get('status')=='VERIFIED','ELG-020','Identity must be verified')
        require(e,human(iv.get('checked_by')),'ELG-021','Identity check must be attributed to a human reviewer')
        require(e,parse_dt(iv.get('checked_at')) is not None,'ELG-022','Identity checked_at required')
        require(e,parse_dt(iv.get('expires_at')) is not None,'ELG-023','Identity expiry required')
        require(e,iu.get('category'),'ELG-030','Intended-use category required')
        require(e,iu.get('declaration'),'ELG-031','Intended-use declaration required')
        require(e,iu.get('responsible_use_version'),'ELG-032','Responsible-use version required')
        require(e,parse_dt(iu.get('acknowledged_at')) is not None,'ELG-033','Responsible-use acknowledgement time required')
        require(e,p.get('notice_accepted') is True,'ELG-040','Privacy notice acceptance required')
        require(e,p.get('notice_version'),'ELG-041','Privacy notice version required')
        require(e,p.get('legal_basis'),'ELG-042','Recorded legal basis required')
        require(e,p.get('retention_schedule_id'),'ELG-043','Retention schedule required')
        require(e,p.get('data_minimised') is True,'ELG-044','Data minimisation must be confirmed')
        require(e,p.get('pseudonymised') is True,'ELG-045','Pseudonymisation must be confirmed')
        require(e,a.get('status')=='APPROVED','ELG-050','Access must be separately approved')
        require(e,human(a.get('approved_by')),'ELG-051','Access approval must be human')
        require(e,a.get('mfa_required') is True,'ELG-052','MFA must be required')
        require(e,parse_dt(a.get('approved_at')) is not None,'ELG-053','Access approval time required')
        require(e,parse_dt(a.get('expires_at')) is not None,'ELG-054','Access expiry required')
        require(e,r.get('review_status')=='COMPLETE','ELG-060','Risk review must be complete')
        require(e,r.get('human_review_required') is True,'ELG-061','Human risk review flag required')
        require(e,r.get('tier')!='PROHIBITED','ELG-062','Prohibited risk cannot be eligible')
        require(e,human(dec.get('decision_by')),'ELG-070','Eligibility decision must be human')
        require(e,parse_dt(dec.get('decision_at')) is not None,'ELG-071','Decision time required')
        require(e,parse_dt(dec.get('expiry_at')) is not None,'ELG-072','Eligibility expiry required')
        if r.get('tier')=='HIGH' or dec.get('status')=='CONDITIONAL':
            require(e,human(dec.get('independent_reviewer')),'ELG-073','High-risk/conditional decision requires independent reviewer')
            require(e,bool(dec.get('conditions')),'ELG-074','High-risk/conditional decision requires conditions')
        if dec.get('reinstatement'):
            require(e,human(dec.get('independent_reviewer')),'ELG-075','Reinstatement requires independent reviewer')
    if d.get('customer_type')=='ORGANISATION':
        oc=d.get('organisation_checks',{})
        require(e,oc.get('legal_name_verified') is True,'ELG-080','Organisation legal name must be verified')
        require(e,oc.get('registration_reference'),'ELG-081','Organisation registration reference required')
        require(e,oc.get('authority_verified') is True,'ELG-082','Organisation authority must be verified')
        require(e,oc.get('beneficial_owner_check')=='COMPLETE','ELG-083','Beneficial-owner check must be complete')
        require(e,oc.get('sanctions_screen_status')=='CLEAR','ELG-084','Organisation screen must be clear')
        require(e,human(oc.get('reviewer')),'ELG-085','Organisation checks require human reviewer')
    if j.get('route_status')=='PROHIBITED':
        require(e,dec.get('status') in {'INELIGIBLE','SUSPENDED','PENDING'},'ELG-090','Prohibited route must not be eligible')
    if r.get('tier')=='PROHIBITED':
        require(e,dec.get('status') in {'INELIGIBLE','SUSPENDED','PENDING'},'ELG-091','Prohibited risk must not be eligible')
    return e

if __name__=='__main__':
    d=load(sys.argv[1]); sys.exit(output(d,validate(d)))
