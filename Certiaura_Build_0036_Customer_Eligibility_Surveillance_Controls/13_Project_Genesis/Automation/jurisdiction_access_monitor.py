from __future__ import annotations
import json, sys
from pathlib import Path
alerts=[]
for p in Path(sys.argv[1]).glob('*.json'):
    try:d=json.loads(p.read_text(encoding='utf-8'))
    except Exception:continue
    if d.get('record_type')!='customer_eligibility':continue
    route=d.get('jurisdiction',{}).get('route_status')
    status=d.get('decision',{}).get('status')
    if route!='APPROVED' and status in {'ELIGIBLE','CONDITIONAL'}:
        alerts.append({'file':p.name,'eligibility_id':d.get('eligibility_id'),'route_status':route,'action':'BLOCK_ACCESS_AND_REVIEW'})
out={'alert_count':len(alerts),'alerts':alerts,'authority':'PROTECTIVE_RESTRICTION_ONLY'}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
