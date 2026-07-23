from __future__ import annotations
import argparse,json
from pathlib import Path
from retatrutide_operational_assurance_common import load_json,validate_record
def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("record"); p.add_argument("--report"); a=p.parse_args(); errors=validate_record(load_json(a.record)); result={"valid":not errors,"errors":errors,"result":"RETATRUTIDE_OPERATIONAL_ASSURANCE_VALIDATED" if not errors else "FAIL"}
 if a.report: Path(a.report).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
 print(json.dumps(result,indent=2)); return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
