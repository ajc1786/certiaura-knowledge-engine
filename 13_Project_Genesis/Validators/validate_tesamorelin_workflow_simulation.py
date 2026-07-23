from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
from tesamorelin_workflow_simulation_common import load_json,validate_record

def main():
 p=argparse.ArgumentParser(); p.add_argument("record"); p.add_argument("--report"); a=p.parse_args(); errors=validate_record(load_json(a.record)); result={"valid":not errors,"errors":errors,"result":"TESAMORELIN_WORKFLOW_SIMULATION_RECORD_VALIDATED" if not errors else "FAIL"}
 if a.report: Path(a.report).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
 print(json.dumps(result,indent=2)); return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
