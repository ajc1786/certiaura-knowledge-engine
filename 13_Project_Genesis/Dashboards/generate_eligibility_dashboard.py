from __future__ import annotations
import json, sys, collections
from pathlib import Path
items=[]
for p in Path(sys.argv[1]).glob('*.json'):
    try: items.append(json.loads(p.read_text(encoding='utf-8')))
    except Exception: pass

rows=[d for d in items if d.get('record_type')=='customer_eligibility']; statuses=collections.Counter(d.get('decision',{}).get('status','UNKNOWN') for d in rows); risks=collections.Counter(d.get('risk',{}).get('tier','UNKNOWN') for d in rows)
out=['# Customer Eligibility Dashboard','',f'- Records: {len(rows)}','', '## Decision status']+[f'- {k}: {v}' for k,v in sorted(statuses.items())]+['','## Risk tiers']+[f'- {k}: {v}' for k,v in sorted(risks.items())]+['','> Dashboard is informational and grants no eligibility.']
Path(sys.argv[2]).write_text('\n'.join(out)+'\n',encoding='utf-8')
