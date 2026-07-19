import argparse, json
from datetime import datetime
from pathlib import Path

def alerts_for(data, as_of):
    alerts=[]
    for s in data.get('suppliers',[]) if isinstance(data,dict) else []:
        sla=s.get('sla',{}) if isinstance(s,dict) else {}
        sid=s.get('supplier_id')
        otif=sla.get('on_time_in_full_percent')
        response=sla.get('evidence_response_days')
        overdue=sla.get('open_overdue_corrective_actions')
        if isinstance(otif,(int,float)) and otif < 95:
            sev='CRITICAL' if otif < 85 else 'WARNING'
            alerts.append({'supplier_id':sid,'alert_type':'OTIF_BREACH','severity':sev,'actual':otif,'target':95,'automatic_positive_action':False})
        if isinstance(response,(int,float)) and response > 5:
            sev='CRITICAL' if response > 10 else 'WARNING'
            alerts.append({'supplier_id':sid,'alert_type':'EVIDENCE_RESPONSE_BREACH','severity':sev,'actual':response,'target':5,'automatic_positive_action':False})
        if isinstance(overdue,int) and overdue>0:
            sev='CRITICAL' if overdue>2 else 'WARNING'
            alerts.append({'supplier_id':sid,'alert_type':'OVERDUE_CORRECTIVE_ACTION','severity':sev,'actual':overdue,'target':0,'automatic_positive_action':False})
    return alerts

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('input_dir'); p.add_argument('output'); p.add_argument('--as-of',required=True)
    a=p.parse_args(argv); base=Path(a.input_dir); asof=datetime.fromisoformat(a.as_of.replace('Z','+00:00')); out=[]
    for f in sorted(base.glob('*portfolio*.json')):
        try: out.extend(alerts_for(json.loads(f.read_text(encoding='utf-8')),asof))
        except Exception: continue
    Path(a.output).write_text(json.dumps({'as_of':a.as_of,'alerts':out},indent=2)+'\n',encoding='utf-8')
    print(f'Generated {len(out)} service-level alerts')
    return 0
if __name__=='__main__': raise SystemExit(main())
