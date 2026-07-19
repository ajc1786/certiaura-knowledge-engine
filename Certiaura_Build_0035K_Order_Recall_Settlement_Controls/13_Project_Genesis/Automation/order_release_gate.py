from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Validators'))
from control_library import load
from validate_contract_order import validate
inp,out=sys.argv[1],sys.argv[2]
d=load(inp); errors=validate(d)
result={'order_id':d.get('order_id'),'generated_decision':'BLOCKED' if errors else 'READY_FOR_HUMAN_RELEASE','automation_authority':'NO_RELEASE_AUTHORITY','control_breaches':errors}
Path(out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(result['generated_decision'])
