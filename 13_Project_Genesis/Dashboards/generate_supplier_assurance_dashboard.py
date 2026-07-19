import argparse, json
from pathlib import Path
from collections import Counter

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('input_dir'); p.add_argument('output_file'); a=p.parse_args(argv)
    rows=[]
    for f in sorted(Path(a.input_dir).glob('valid_*.json')):
        try: d=json.loads(f.read_text(encoding='utf-8'))
        except Exception: continue
        s=d.get('supplier') or {}; q=d.get('qualification') or {}; r=d.get('risk_assessment') or {}; au=d.get('audit') or {}; ca=d.get('continuous_assurance') or {}; rr=d.get('restrictions') or {}
        rows.append({'id':s.get('supplier_id'),'name':s.get('legal_name'),'status':q.get('status'),'tier':r.get('tier'),'score':r.get('score'),'audit':au.get('audit_status'),'triggers':len([x for x in ca.get('triggers',[]) if isinstance(x,dict) and x.get('status') in {'OPEN','UNDER_REVIEW'}]),'passport':rr.get('passport_submission_allowed'),'marketplace':rr.get('marketplace_supplier_eligible')})
    status=Counter(x['status'] for x in rows); tiers=Counter(x['tier'] for x in rows)
    lines=['# Supplier Assurance Dashboard','','## Portfolio summary','',f'- Suppliers: **{len(rows)}**',f'- Qualified: **{status.get("QUALIFIED",0)}**',f'- Conditional: **{status.get("CONDITIONAL",0)}**',f'- Suspended: **{status.get("SUSPENDED",0)}**',f'- Critical risk: **{tiers.get("CRITICAL",0)}**','','## Supplier status','', '| Supplier | Status | Tier | Score | Audit | Open triggers | Passport submissions | Marketplace |','|---|---|---:|---:|---|---:|---:|---:|']
    for x in rows: lines.append(f"| {x['id']} — {x['name']} | {x['status']} | {x['tier']} | {x['score']} | {x['audit']} | {x['triggers']} | {'Yes' if x['passport'] else 'No'} | {'Yes' if x['marketplace'] else 'No'} |")
    lines += ['','## Control note','','Supplier qualification is an organisation-level prerequisite only. Product, batch and claim verification remain separate.']
    Path(a.output_file).parent.mkdir(parents=True,exist_ok=True); Path(a.output_file).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'PASS: generated supplier assurance dashboard for {len(rows)} supplier(s)')
    return 0
if __name__=='__main__': raise SystemExit(main())
