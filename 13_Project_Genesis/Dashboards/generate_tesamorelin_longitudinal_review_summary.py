from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument("records",nargs="+"); p.add_argument("--output",required=True); a=p.parse_args(); rows=[json.loads(Path(x).read_text(encoding="utf-8")) for x in a.records]
 summary={"build_number":"0058","peptide":"Tesamorelin","record_count":len(rows),"record_types":sorted({r.get("record_type") for r in rows}),"decisions":[r.get("decision") for r in rows if r.get("decision")],"clinical_recommendation_authorised":False,"result":"TESAMORELIN_LONGITUDINAL_REVIEW_SUMMARY_GENERATED"}
 Path(a.output).write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8",newline="\n"); print(json.dumps(summary,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
