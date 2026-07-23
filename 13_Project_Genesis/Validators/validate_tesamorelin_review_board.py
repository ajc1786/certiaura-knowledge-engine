from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
from tesamorelin_review_board_common import load_json,validate_record
def main():
 p=argparse.ArgumentParser(); p.add_argument("record"); a=p.parse_args(); e=validate_record(load_json(a.record)); print(json.dumps({"valid":not e,"errors":e},indent=2)); return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
