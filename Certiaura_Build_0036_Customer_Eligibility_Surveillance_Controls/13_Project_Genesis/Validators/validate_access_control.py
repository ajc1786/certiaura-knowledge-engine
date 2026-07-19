from __future__ import annotations
import sys
from control_library import load, human, parse_dt, require, output

def validate(d):
    e=[]
    require(e,d.get('record_type')=='access_control','ACS-001','Wrong record type')
    if d.get('status')=='APPROVED':
        require(e,human(d.get('approved_by')),'ACS-010','Access approval must be human')
        require(e,d.get('mfa_required') is True,'ACS-011','MFA required')
        require(e,parse_dt(d.get('approved_at')) is not None,'ACS-012','Approval time required')
        require(e,parse_dt(d.get('expires_at')) is not None,'ACS-013','Expiry required')
    return e
if __name__=='__main__':
    d=load(sys.argv[1]); sys.exit(output(d,validate(d)))
