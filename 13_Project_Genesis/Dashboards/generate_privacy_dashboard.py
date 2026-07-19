from __future__ import annotations
import json, sys, collections
from pathlib import Path
items=[]
for p in Path(sys.argv[1]).glob('*.json'):
    try: items.append(json.loads(p.read_text(encoding='utf-8')))
    except Exception: pass

req=[d for d in items if d.get('record_type')=='privacy_request']; statuses=collections.Counter(d.get('decision',{}).get('status','UNKNOWN') for d in req)
out=['# Privacy Operations Dashboard','',f'- Rights requests: {len(req)}']+[f'- {k}: {v}' for k,v in sorted(statuses.items())]+['','> Dashboard cannot close or refuse a request.']
Path(sys.argv[2]).write_text('\n'.join(out)+'\n',encoding='utf-8')
