from __future__ import annotations
import json,sys
from pathlib import Path
folder,out=Path(sys.argv[1]),Path(sys.argv[2]); rows=[]
for p in folder.glob('*.json'):
    try:d=json.loads(p.read_text(encoding='utf-8'))
    except Exception:continue
    if d.get('record_type')=='INCIDENT_RECALL_CASE':
        rows.append([d.get('incident_id'),d.get('severity'),d.get('status'),(d.get('traceability') or {}).get('completeness_percent'),(d.get('affected_scope') or {}).get('population')])
text='# Incident and Recall Dashboard\n\n| Incident | Severity | Status | Traceability % | Population |\n|---|---:|---|---:|---:|\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)+'\n> Human incident command retains decision authority.\n'
out.write_text(text,encoding='utf-8'); print('DASHBOARD GENERATED')
