import argparse, json
from pathlib import Path

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('output'); a=p.parse_args(argv)
    d=json.loads(Path(a.input).read_text(encoding='utf-8'))
    lines=['# Comparative Supplier Performance and Commercial Scorecard','', '> Analytics are non-binding and cannot override assurance, safety, evidence or resilience blockers.', '', '| Supplier | Assurance | Quality | Delivery | Responsiveness | Evidence | OTIF | Total cost | Marketplace |', '|---|---|---:|---:|---:|---:|---:|---:|---|']
    for s in d.get('suppliers',[]):
        p=s.get('performance',{}); sla=s.get('sla',{}); c=s.get('commercial',{}); m=s.get('marketplace',{})
        lines.append(f"| {s.get('legal_name')} | {s.get('assurance_status')} | {p.get('quality_score')} | {p.get('delivery_score')} | {p.get('responsiveness_score')} | {p.get('evidence_score')} | {sla.get('on_time_in_full_percent')}% | {c.get('currency')} {c.get('total_cost'):,.0f} | {'Eligible' if m.get('commercial_eligible') else 'Not eligible'} |")
    Path(a.output).write_text('\n'.join(lines)+'\n',encoding='utf-8'); print(f'Generated scorecard for {len(d.get("suppliers",[]))} suppliers'); return 0
if __name__=='__main__': raise SystemExit(main())
