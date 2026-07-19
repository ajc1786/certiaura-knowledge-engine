from __future__ import annotations
import json, sys
from pathlib import Path
alerts=[]
for p in Path(sys.argv[1]).glob('*.json'):
    try:d=json.loads(p.read_text(encoding='utf-8'))
    except Exception:continue
    if d.get('record_type')=='customer_eligibility':
        pr=d.get('privacy',{})
        for field in ['notice_version','legal_basis','retention_schedule_id']:
            if not pr.get(field): alerts.append({'file':p.name,'record_id':d.get('eligibility_id'),'issue':f'MISSING_{field.upper()}'})
        if pr.get('data_minimised') is not True: alerts.append({'file':p.name,'record_id':d.get('eligibility_id'),'issue':'DATA_MINIMISATION_NOT_CONFIRMED'})
    if d.get('record_type')=='privacy_request' and d.get('decision',{}).get('status') not in {'COMPLETED','REFUSED_WITH_REASONS'}:
        alerts.append({'file':p.name,'record_id':d.get('request_id'),'issue':'OPEN_PRIVACY_REQUEST'})
out={'alert_count':len(alerts),'alerts':alerts,'authority':'ALERT_ONLY'}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
