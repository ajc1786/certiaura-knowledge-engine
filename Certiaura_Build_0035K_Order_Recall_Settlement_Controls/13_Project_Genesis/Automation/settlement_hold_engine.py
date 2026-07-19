from __future__ import annotations
import json,sys
from pathlib import Path
folder,out=Path(sys.argv[1]),Path(sys.argv[2]); holds=[]
for p in folder.glob('*.json'):
    try:d=json.loads(p.read_text(encoding='utf-8'))
    except Exception:continue
    if d.get('record_type')!='SETTLEMENT_CASE':continue
    op=d.get('operational_prerequisites') or {}
    reasons=[k for k,v in op.items() if (k=='open_disputes' and v is True) or (k!='open_disputes' and v is not True)]
    holds.append({'settlement_id':d.get('settlement_id'),'recommended_hold':'ACTIVE' if reasons else 'ELIGIBLE_FOR_HUMAN_RELEASE_REVIEW','reasons':reasons,'automation_authority':'NO_HOLD_RELEASE_AUTHORITY'})
Path(out).write_text(json.dumps({'holds':holds},indent=2)+'\n',encoding='utf-8'); print(f'{len(holds)} cases assessed')
