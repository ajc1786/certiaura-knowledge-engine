from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timedelta, timezone
from pathlib import Path

def parse(value): return datetime.fromisoformat(value.replace("Z","+00:00"))
def iso(value): return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def stable(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def generate(journey, policy, as_of):
    if journey["journey_state"]=="LOCKED_URGENT_ROUTING":
        state="LOCKED_URGENT_ROUTING"; items=[{"rule_id":"URGENT_ROUTING","label":"Immediate clinical assessment routing","due_at":as_of,"state":"URGENT","source_event_id":journey["events"][-1]["event_id"] if journey["events"] else None}]
    else:
        items=[]
        for event in journey["events"]:
            for rule in policy["routine_rules"]:
                if event["event_type"]==rule["source_event_type"]:
                    due=parse(event["observed_at"])+timedelta(days=int(rule["days_after"]))
                    due_s=iso(due); item_state="OVERDUE" if due < parse(as_of) else "DUE"
                    items.append({"rule_id":rule["rule_id"],"label":rule["label"],"due_at":due_s,"state":item_state,"source_event_id":event["event_id"]})
        items.sort(key=lambda x:(x["due_at"],x["rule_id"],x["source_event_id"]))
        state="CLINICIAN_DISCUSSION_REQUIRED" if any(x["state"]=="OVERDUE" for x in items) else "ROUTINE"
    core={"journey_id":journey["journey_id"],"schedule_state":state,"items":items,"source_chain_head":journey["chain_head"],"as_of":as_of}
    return {"schedule_id":"RRS-"+stable(core)[:16].upper(),**core}

def main():
    p=argparse.ArgumentParser(); p.add_argument("journey"); p.add_argument("--policy",required=True); p.add_argument("--as-of",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    result=generate(json.loads(Path(a.journey).read_text()),json.loads(Path(a.policy).read_text()),a.as_of)
    Path(a.output).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"valid":True,"schedule_id":result["schedule_id"],"schedule_state":result["schedule_state"],"item_count":len(result["items"])},indent=2))
if __name__=="__main__": main()
