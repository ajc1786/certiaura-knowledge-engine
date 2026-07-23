from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("evidence"); p.add_argument("--report"); a=p.parse_args()
    data=json.loads(Path(a.evidence).read_text(encoding="utf-8")); errors=[]
    if data.get("source") != "CANONICAL_GIT_OBJECTS": errors.append("source must be CANONICAL_GIT_OBJECTS")
    if data.get("predecessor_build") != "0052": errors.append("predecessor_build must be 0052")
    if data.get("predecessor_candidate") != "RC6": errors.append("predecessor_candidate must be RC6")
    if data.get("predecessor_commit") != "890df218b4f4dea92f4ccfa36b8106de59eca1b1": errors.append("canonical predecessor commit mismatch")
    if data.get("predecessor_path_count") != 59: errors.append("predecessor path count must be 59")
    if data.get("prohibited_intersection"): errors.append("prohibited predecessor/current intersection exists")
    if data.get("withdrawn_candidates") != ["RC1","RC2","RC3","RC4","RC5"]: errors.append("withdrawn candidate lineage mismatch")
    result={"valid":not errors,"errors":errors,"result":"PREDECESSOR_ISOLATION_VALIDATED" if not errors else "FAIL"}
    if a.report: Path(a.report).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result,indent=2)); return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
