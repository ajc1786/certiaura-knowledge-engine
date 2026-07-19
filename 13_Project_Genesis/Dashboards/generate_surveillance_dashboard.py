from __future__ import annotations
import json, sys, collections
from pathlib import Path
items=[]
for p in Path(sys.argv[1]).glob('*.json'):
    try: items.append(json.loads(p.read_text(encoding='utf-8')))
    except Exception: pass

cases=[d for d in items if d.get('record_type')=='surveillance_case']; sevs=collections.Counter(d.get('severity','UNKNOWN') for d in cases); states=collections.Counter(d.get('closure',{}).get('status','UNKNOWN') for d in cases)
out=['# Post-Market Surveillance Dashboard','',f'- Cases: {len(cases)}','','## Severity']+[f'- {k}: {v}' for k,v in sorted(sevs.items())]+['','## Case state']+[f'- {k}: {v}' for k,v in sorted(states.items())]+['','> Dashboard cannot diagnose, decide reportability or close cases.']
Path(sys.argv[2]).write_text('\n'.join(out)+'\n',encoding='utf-8')
