from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Validators'))
from validate_customer_eligibility import validate
from control_library import load

d=load(sys.argv[1]); breaches=validate(d)
decision=d.get('decision',{}).get('status')
result={'eligibility_id':d.get('eligibility_id'),'validator_valid':not breaches,'breach_count':len(breaches),'human_decision':decision,'automation_recommendation':'ALLOW_EXISTING_DECISION' if not breaches else 'BLOCK_AND_ROUTE_TO_REVIEW','automation_authority':'NO_APPROVAL_AUTHORITY'}
Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
