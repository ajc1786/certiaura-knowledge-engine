from __future__ import annotations
import json,sys
from pathlib import Path
folder,out=Path(sys.argv[1]),Path(sys.argv[2]); alerts=[]
for p in folder.glob('*.json'):
    try: d=json.loads(p.read_text(encoding='utf-8'))
    except Exception: continue
    if d.get('record_type')!='FULFILMENT_RECEIPT': continue
    s=d.get('storage') or {}; disp=d.get('disposition') or {}; rec=d.get('receipt') or {}
    if s.get('excursion_detected'):
        alerts.append({'shipment_id':d.get('shipment_id'),'type':'TEMPERATURE_EXCURSION','protective_action':'QUARANTINE','human_disposition':disp.get('status')})
    if rec.get('quantity_ordered')!=rec.get('quantity_received'):
        alerts.append({'shipment_id':d.get('shipment_id'),'type':'QUANTITY_MISMATCH','protective_action':'RECONCILE'})
Path(out).write_text(json.dumps({'automation_authority':'ALERT_AND_RESTRICT_ONLY','alerts':alerts},indent=2)+'\n',encoding='utf-8')
print(f'{len(alerts)} alerts')
