from __future__ import annotations
import json, sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); sev=d.get('severity')
actions={'LOW':['LOG'],'MODERATE':['OPEN_INVESTIGATION'],'HIGH':['RESTRICT_AND_ESCALATE'],'CRITICAL':['BLOCK_BATCH','SUSPEND_LISTING','QUARANTINE_STOCK','NOTIFY_INCIDENT_COMMAND']}.get(sev,['ROUTE_TO_REVIEW'])
out={'case_id':d.get('case_id'),'severity':sev,'recommended_actions':actions,'authority':'PROTECTIVE_ACTIONS_AND_RECOMMENDATION_ONLY','may_close_case':False,'may_decide_reportability':False}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
