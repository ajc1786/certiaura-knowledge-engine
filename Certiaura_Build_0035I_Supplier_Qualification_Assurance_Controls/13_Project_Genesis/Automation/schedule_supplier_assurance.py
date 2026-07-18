import argparse, json
from pathlib import Path
from datetime import datetime, timezone

def dt(v):
    try: return datetime.fromisoformat(str(v).replace('Z','+00:00'))
    except Exception: return None

def alerts_for(data, as_of):
    out=[]; sid=(data.get('supplier') or {}).get('supplier_id','UNKNOWN')
    q=data.get('qualification') or {}; ca=data.get('continuous_assurance') or {}; a=data.get('audit') or {}
    def add(kind,severity,due,action,source): out.append({'supplier_id':sid,'alert_type':kind,'severity':severity,'due_at':due,'recommended_action':action,'source':source,'automatic_positive_action':False})
    nd=dt(ca.get('next_review_due'))
    if nd and nd<=as_of: add('ASSURANCE_REVIEW_DUE','HIGH',nd.isoformat(),'OPEN_REVIEW_AND_RESTRICT_NEW_ACTIVITY','continuous_assurance.next_review_due')
    ad=dt(a.get('next_audit_due'))
    if ad and ad<=as_of: add('AUDIT_DUE','HIGH',ad.isoformat(),'OPEN_AUDIT_AND_REVIEW_QUALIFICATION','audit.next_audit_due')
    eu=dt(q.get('effective_until'))
    if eu and eu<=as_of: add('QUALIFICATION_EXPIRED','CRITICAL',eu.isoformat(),'EXPIRE_STATUS_AND_BLOCK_POSITIVE_ACTIVITY','qualification.effective_until')
    for item in (data.get('due_diligence') or {}).get('evidence_items',[]):
        ex=dt(item.get('expires_at')) if isinstance(item,dict) else None
        if ex and ex<=as_of: add('EVIDENCE_EXPIRED','HIGH',ex.isoformat(),'BLOCK_AFFECTED_SCOPE_AND_REQUEST_REFRESH',f'evidence:{item.get("evidence_id")}')
    for t in ca.get('triggers',[]) if isinstance(ca.get('triggers'),list) else []:
        if isinstance(t,dict) and t.get('status') in {'OPEN','UNDER_REVIEW'}:
            add('OPEN_ASSURANCE_TRIGGER',t.get('severity','MODERATE'),t.get('due_at') or as_of.isoformat(),'MAINTAIN_PROTECTIVE_RESTRICTIONS',f'trigger:{t.get("trigger_id")}')
    return out

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('input_dir'); p.add_argument('output_file'); p.add_argument('--as-of',required=True); a=p.parse_args(argv)
    as_of=dt(a.as_of)
    if not as_of: print('FAIL: invalid --as-of'); return 2
    alerts=[]
    for f in sorted(Path(a.input_dir).glob('*.json')):
        try: data=json.loads(f.read_text(encoding='utf-8'))
        except Exception: continue
        alerts.extend(alerts_for(data,as_of))
    out={'generated_at':as_of.isoformat(),'alert_count':len(alerts),'alerts':alerts}
    Path(a.output_file).parent.mkdir(parents=True,exist_ok=True); Path(a.output_file).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: generated {len(alerts)} supplier assurance alert(s)')
    return 0
if __name__=='__main__': raise SystemExit(main())
