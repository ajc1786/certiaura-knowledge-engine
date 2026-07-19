from __future__ import annotations
import json, sys, collections
from pathlib import Path
items=[]
for p in Path(sys.argv[1]).glob('*.json'):
    try: items.append(json.loads(p.read_text(encoding='utf-8')))
    except Exception: pass

cases=[d for d in items if d.get('record_type')=='surveillance_case']; reps=collections.Counter(d.get('reporting_assessment',{}).get('reportability','UNKNOWN') for d in cases)
out=['# Regulatory Reporting Assessment Dashboard','',f'- Assessed cases: {len(cases)}']+[f'- {k}: {v}' for k,v in sorted(reps.items())]+['','> Dashboard cannot determine legal reportability or submit a report.']
Path(sys.argv[2]).write_text('\n'.join(out)+'\n',encoding='utf-8')
