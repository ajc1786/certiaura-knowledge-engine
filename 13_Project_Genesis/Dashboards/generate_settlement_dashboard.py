from __future__ import annotations
import json,sys
from pathlib import Path
folder,out=Path(sys.argv[1]),Path(sys.argv[2]); rows=[]
for p in folder.glob('*.json'):
    try:d=json.loads(p.read_text(encoding='utf-8'))
    except Exception:continue
    if d.get('record_type')=='SETTLEMENT_CASE':
        f=d.get('financials') or {}; rows.append([d.get('settlement_id'),d.get('status'),(d.get('hold') or {}).get('status'),f.get('currency'),f.get('gross_exposure'),f.get('final_settlement')])
text='# Settlement Dashboard\n\n| Settlement | Status | Hold | Currency | Gross exposure | Final settlement |\n|---|---|---|---|---:|---:|\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)+'\n> Dashboard output cannot release holds or approve settlement.\n'
out.write_text(text,encoding='utf-8'); print('DASHBOARD GENERATED')
