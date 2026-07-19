import argparse, importlib.util, json
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
P=ROOT/'13_Project_Genesis'/'Automation'/'portfolio_analytics.py'
spec=importlib.util.spec_from_file_location('analytics',P); analytics=importlib.util.module_from_spec(spec); spec.loader.exec_module(analytics)

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('input_dir'); p.add_argument('output'); a=p.parse_args(argv)
    rows=[]
    for f in sorted(Path(a.input_dir).glob('*portfolio*.json')):
        try:
            d=json.loads(f.read_text(encoding='utf-8'))
            if not isinstance(d.get('portfolio'),dict): continue
            calc=analytics.calculate(d); m=calc['metrics']; rows.append((d,calc))
        except Exception: continue
    lines=['# Supplier Portfolio Risk and Resilience Dashboard','', '> Decision-support output only. No automatic award, qualification or Marketplace approval.', '', '| Portfolio | Suppliers | Annual spend | HHI | Max supplier | Top 3 | Critical single source | Rating |', '|---|---:|---:|---:|---:|---:|---:|---|']
    for d,calc in rows:
        p=d['portfolio']; m=calc['metrics']; lines.append(f"| {p.get('name')} | {len(d.get('suppliers',[]))} | {p.get('currency')} {p.get('annual_spend'):,.0f} | {m['hhi']} | {m['max_supplier_percent']}% | {m['top_three_percent']}% | {m['critical_single_source_count']} | {calc['recommended_resilience_rating']} |")
    lines += ['', '## Open actions', '', '| Portfolio | Action | Category | Owner | Due | Status |','|---|---|---|---|---|---|']
    for d,_ in rows:
        for x in d.get('resilience',{}).get('open_actions',[]): lines.append(f"| {d['portfolio'].get('portfolio_id')} | {x.get('action_id')} | {x.get('category_id')} | {x.get('owner_id')} | {x.get('due_at')} | {x.get('status')} |")
    Path(a.output).write_text('\n'.join(lines)+'\n',encoding='utf-8'); print(f'Generated dashboard for {len(rows)} portfolios'); return 0
if __name__=='__main__': raise SystemExit(main())
