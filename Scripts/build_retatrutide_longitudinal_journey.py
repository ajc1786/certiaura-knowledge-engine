from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from record_retatrutide_longitudinal_event import append_event

def main():
    p=argparse.ArgumentParser(); p.add_argument("seed"); p.add_argument("--output",required=True); a=p.parse_args()
    seed=json.loads(Path(a.seed).read_text(encoding="utf-8")); journey={"journey_id":seed["journey_id"],"version":"1.0.0","journey_state":"ACTIVE","events":[],"chain_head":"0"*64}
    for event in seed.get("events",[]): journey=append_event(journey,event)
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(journey,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"valid":True,"journey_id":journey["journey_id"],"journey_state":journey["journey_state"],"event_count":len(journey["events"]),"chain_head":journey["chain_head"]},indent=2))
if __name__=="__main__": main()
