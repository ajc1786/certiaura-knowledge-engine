from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument("records",nargs="+"); p.add_argument("--output",required=True); a=p.parse_args(); data=[json.loads(Path(x).read_text(encoding="utf-8")) for x in a.records]
 out={"build_number":"0055","record_count":len(data),"record_types":sorted({x.get("record_type") for x in data}),"closure_decisions":[x.get("decision") for x in data if x.get("record_type")=="operational_baseline_closure_decision"],"release_authorisations":[x.get("decision") for x in data if x.get("record_type")=="controlled_release_authorisation"],"selected_pilots":[x.get("selected_peptide") for x in data if x.get("record_type")=="next_peptide_pilot_selection"]}
 Path(a.output).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8",newline="\n"); print(json.dumps(out,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
