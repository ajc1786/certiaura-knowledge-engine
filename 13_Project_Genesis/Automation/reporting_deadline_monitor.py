from __future__ import annotations
import json, sys
from pathlib import Path
from datetime import datetime, timezone
alerts=[]; now=datetime(2026,7,19,tzinfo=timezone.utc)
for p in Path(sys.argv[1]).glob('*.json'):
    try:d=json.loads(p.read_text(encoding='utf-8'))
    except Exception:continue
    if d.get('record_type')!='surveillance_case':continue
    ra=d.get('reporting_assessment',{})
    if ra.get('reportability')=='REQUIRED':
        due=ra.get('due_at'); status='MISSING_DEADLINE'
        if due:
            try: status='OVERDUE_OR_DUE' if datetime.fromisoformat(due.replace('Z','+00:00'))<=now else 'UPCOMING'
            except Exception: status='INVALID_DEADLINE'
        alerts.append({'case_id':d.get('case_id'),'due_at':due,'status':status,'report_reference':ra.get('report_reference')})
out={'alert_count':len(alerts),'alerts':alerts,'authority':'DEADLINE_ALERT_ONLY'}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
