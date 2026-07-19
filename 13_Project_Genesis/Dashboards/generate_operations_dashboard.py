from __future__ import annotations
import json,sys
from pathlib import Path
folder,out=Path(sys.argv[1]),Path(sys.argv[2]); counts={'orders':0,'released':0,'fulfilments':0,'excursions':0,'quarantined':0}
for p in folder.glob('*.json'):
    try:d=json.loads(p.read_text(encoding='utf-8'))
    except Exception:continue
    if d.get('record_type')=='ORDER_ASSURANCE':
        counts['orders']+=1; counts['released']+=int((d.get('release_decision') or {}).get('status')=='RELEASED')
    if d.get('record_type')=='FULFILMENT_RECEIPT':
        counts['fulfilments']+=1; counts['excursions']+=int((d.get('storage') or {}).get('excursion_detected') is True); counts['quarantined']+=int((d.get('disposition') or {}).get('quarantined') is True)
text='# Operations Dashboard\n\n'+''.join(f'- **{k.replace("_"," ").title()}:** {v}\n' for k,v in counts.items())+'\n> Dashboard is informational and creates no approval.\n'
out.write_text(text,encoding='utf-8'); print('DASHBOARD GENERATED')
