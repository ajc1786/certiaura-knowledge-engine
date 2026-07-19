#!/usr/bin/env python3
"""Generate a Markdown supplier/remediation dashboard from validated case JSON files."""
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def build_dashboard(cases):
    state=Counter(); severity=Counter(); tier=Counter(); escalation=Counter(); suppliers=defaultdict(list)
    overdue=0; ready=0; open_alerts=0; repeat=0
    now=datetime(2026,7,23,tzinfo=timezone.utc)
    for d in cases:
        c=d.get('case',{}); p=d.get('supplier_performance',{}); a=d.get('assessment',{})
        state[c.get('status','UNKNOWN')]+=1; severity[c.get('severity','UNKNOWN')]+=1; tier[p.get('tier','UNKNOWN')]+=1; escalation[p.get('escalation_level','UNKNOWN')]+=1
        suppliers[c.get('supplier_id','UNKNOWN')].append(d)
        repeat+=int(c.get('repeat_failure_count',0) or 0)
        if a.get('readiness'): ready+=1
        for x in d.get('alert_closure',[]):
            if x.get('decision') in {'REMAINS_OPEN','ESCALATED'}: open_alerts+=1
        for x in d.get('corrective_action_plan',{}).get('actions',[]):
            due=x.get('due_at')
            try: ddt=datetime.fromisoformat(due.replace('Z','+00:00')) if due else None
            except ValueError: ddt=None
            if x.get('status') not in {'COMPLETED','CANCELLED'} and ddt and ddt<now: overdue+=1
    lines=['# Certiaura Supplier Performance and Remediation Dashboard','',f'Generated from {len(cases)} case record(s).','',
      '## Portfolio KPIs','',f'- Reinstatement-ready assessments: **{ready}**',f'- Open or escalated alerts: **{open_alerts}**',f'- Overdue corrective actions: **{overdue}**',f'- Recorded repeat failures: **{repeat}**','']
    def section(title,counter):
        lines.extend([f'## {title}','', '| Category | Count |','|---|---:|'])
        for k,v in sorted(counter.items()): lines.append(f'| {k} | {v} |')
        lines.append('')
    section('Cases by state',state); section('Cases by severity',severity); section('Supplier tiers',tier); section('Escalation levels',escalation)
    lines.extend(['## Supplier summary','', '| Supplier | Cases | Latest score | Tier | Escalation |','|---|---:|---:|---|---|'])
    for sid,rows in sorted(suppliers.items()):
        latest=rows[-1].get('supplier_performance',{})
        lines.append(f"| {sid} | {len(rows)} | {latest.get('score','')} | {latest.get('tier','')} | {latest.get('escalation_level','')} |")
    lines.extend(['','> Dashboard values are management indicators. They do not replace source evidence, review decisions or legal/regulatory assessment.',''])
    return '\n'.join(lines)


def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('input_dir'); p.add_argument('output'); a=p.parse_args(argv)
    files=sorted(Path(a.input_dir).glob('valid_*.json'))
    cases=[json.loads(x.read_text(encoding='utf-8')) for x in files]
    Path(a.output).write_text(build_dashboard(cases),encoding='utf-8')
    print(f'PASS: dashboard generated from {len(cases)} validated example cases')
    return 0

if __name__=='__main__': raise SystemExit(main())
