from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def stable(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def latest_measurements(events):
    latest={}
    for event in events:
        if event["event_type"] in ("BASELINE","MEASUREMENT","MONITORING"):
            for key,value in event.get("payload",{}).items():
                if isinstance(value,(int,float,str,bool)):
                    latest[key]={"value":value,"observed_at":event["observed_at"],"source_event_id":event["event_id"]}
    return latest

def generate(journey,schedule):
    events=journey["events"]
    symptoms=[{"observed_at":e["observed_at"],"payload":e["payload"],"source_event_id":e["event_id"]} for e in events if e["event_type"]=="SYMPTOM"]
    questions=[{"observed_at":e["observed_at"],"question":e["payload"].get("question"),"source_event_id":e["event_id"]} for e in events if e["event_type"]=="QUESTION"]
    state="URGENT_CLINICAL_ROUTING" if journey["journey_state"]=="LOCKED_URGENT_ROUTING" else "READY_FOR_CLINICIAN_DISCUSSION"
    window={"start":min((e["observed_at"] for e in events),default=None),"end":max((e["observed_at"] for e in events),default=None)}
    core={"journey_id":journey["journey_id"],"handoff_state":state,"reporting_window":window,"summary":{"event_count":len(events),"latest_measurements":latest_measurements(events),"symptoms":symptoms,"questions":questions},"review_status":{"schedule_id":schedule["schedule_id"],"schedule_state":schedule["schedule_state"],"items":schedule["items"]},"provenance":{"journey_chain_head":journey["chain_head"],"source_event_ids":[e["event_id"] for e in events],"source_refs":sorted({r for e in events for r in e.get("source_refs",[])})},"safety_boundary":"For clinician discussion only. This handoff does not diagnose, prescribe, select treatment, calculate dosing or replace urgent clinical assessment."}
    return {"handoff_id":"RCH-"+stable(core)[:16].upper(),**core}

def render_md(result):
    lines=["# Certiaura Retatrutide Clinician Handoff","",f"**Handoff ID:** {result['handoff_id']}",f"**Journey ID:** {result['journey_id']}",f"**State:** {result['handoff_state']}","","## Reporting window","",json.dumps(result['reporting_window'],indent=2),"","## Journey summary","",json.dumps(result['summary'],indent=2),"","## Review status","",json.dumps(result['review_status'],indent=2),"","## Provenance","",json.dumps(result['provenance'],indent=2),"","## Safety boundary","",result['safety_boundary'],""]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser(); p.add_argument("journey"); p.add_argument("schedule"); p.add_argument("--output-json",required=True); p.add_argument("--output-md",required=True); a=p.parse_args()
    result=generate(json.loads(Path(a.journey).read_text()),json.loads(Path(a.schedule).read_text()))
    Path(a.output_json).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n"); Path(a.output_md).write_text(render_md(result),encoding="utf-8",newline="\n")
    print(json.dumps({"valid":True,"handoff_id":result["handoff_id"],"handoff_state":result["handoff_state"],"source_event_count":len(result["provenance"]["source_event_ids"])},indent=2))
if __name__=="__main__": main()
