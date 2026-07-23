from __future__ import annotations
import argparse,json
from pathlib import Path
def main():
 p=argparse.ArgumentParser(); p.add_argument("records",nargs="+"); p.add_argument("--output",required=True); a=p.parse_args(); rows=[]
 for item in a.records:
  d=json.loads(Path(item).read_text(encoding="utf-8")); rows.append({"record_id":d.get("record_id"),"record_type":d.get("record_type"),"decision":d.get("decision") or d.get("outcome") or d.get("reentry_decision") or d.get("status")})
 out={"build_number":"0059","peptide":"Tesamorelin","non_clinical":True,"records":rows}; Path(a.output).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8",newline="\n"); print(json.dumps(out,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
