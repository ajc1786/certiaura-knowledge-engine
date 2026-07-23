from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument("records",nargs="+"); p.add_argument("--output",required=True); a=p.parse_args(); records=[json.loads(Path(x).read_text(encoding="utf-8")) for x in a.records]
 out={"build_number":"0057","record_count":len(records),"record_types":sorted({r.get("record_type") for r in records}),"decisions":[r.get("decision") or r.get("action") for r in records],"clinical_boundary":"NON_CLINICAL_ONLY"}
 Path(a.output).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8",newline="\n"); print(json.dumps(out,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
