from __future__ import annotations
import argparse,json
from pathlib import Path
def main():
 p=argparse.ArgumentParser(); p.add_argument("record"); p.add_argument("--output",required=True); a=p.parse_args(); d=json.loads(Path(a.record).read_text(encoding="utf-8")); lines=["# BPC-157 transition summary",f"Record: {d.get('record_id','')}",f"Decision: {d.get('decision','')}",f"Human evidence: {d.get('human_evidence_state',d.get('human_evidence_gap_severity',''))}",f"Regulatory boundary: {d.get('regulatory_evidence_state',d.get('regulatory_boundary_state',''))}","Clinical recommendation authorised: NO"]; Path(a.output).write_text("\n\n".join(lines)+"\n",encoding="utf-8",newline="\n"); return 0
if __name__=="__main__": raise SystemExit(main())
