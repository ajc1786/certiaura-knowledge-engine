from __future__ import annotations
import sys
from control_library import load, human, parse_dt, require, output

def validate(d):
    e=[]
    require(e,d.get('record_type')=='reporting_assessment','RPT-001','Wrong record type')
    require(e,d.get('jurisdiction'),'RPT-010','Jurisdiction required')
    require(e,d.get('authority_route'),'RPT-011','Authority/route required')
    require(e,d.get('reportability') in {'REQUIRED','NOT_REQUIRED','PENDING'},'RPT-012','Invalid reportability')
    if d.get('reportability')!='PENDING':
        require(e,human(d.get('decision_by')),'RPT-020','Reportability decision must be human')
        require(e,parse_dt(d.get('decision_at')) is not None,'RPT-021','Decision date required')
    if d.get('reportability')=='REQUIRED':
        require(e,parse_dt(d.get('due_at')) is not None,'RPT-030','Required report needs deadline')
    return e
if __name__=='__main__':
    d=load(sys.argv[1]); sys.exit(output(d,validate(d)))
