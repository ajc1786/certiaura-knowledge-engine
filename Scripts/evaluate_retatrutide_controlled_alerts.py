from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from analyze_retatrutide_longitudinal_outcomes import reject_identifiers

def canonical(value): return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)

def evaluate(journey,analytics,schedule,policy):
    reject_identifiers(journey);reject_identifiers(analytics);reject_identifiers(schedule)
    state="NO_ALERT";reasons=[];refs=set()
    if journey.get("journey_state") in policy.get("urgent_journey_states",[]):
        state="LOCKED_URGENT_ROUTING";reasons.append("Journey already contains an urgent-routing lock.")
    elif schedule.get("schedule_state") in policy.get("review_states_triggering_discussion",[]):
        state="CLINICIAN_DISCUSSION_REQUIRED";reasons.append("The administrative review schedule requires clinician discussion.")
    elif analytics.get("analytics_state")=="INSUFFICIENT_DATA":
        state="INSUFFICIENT_DATA";reasons.append("No tracked metric has enough observations for controlled evaluation.")
    else:
        for metric in analytics.get("metrics",[]):
            config=policy.get("tracked_metrics",{}).get(metric.get("metric"),{})
            pct=metric.get("percentage_change");threshold=config.get("review_change_percent")
            if metric.get("data_state")=="SUFFICIENT" and isinstance(pct,(int,float)) and isinstance(threshold,(int,float)) and abs(float(pct))>=float(threshold):
                state="CLINICIAN_DISCUSSION_REQUIRED";reasons.append(f"{metric.get('label')} reached the configured descriptive review threshold.");refs.update(metric.get("evidence_refs",[]))
    message=policy.get("alert_messages",{}).get(state,"Controlled alert state generated.")
    core={"journey_id":journey.get("journey_id"),"analytics_id":analytics.get("analytics_id"),"schedule_id":schedule.get("schedule_id"),"alert_state":state,"reasons":reasons,"message":message,"evidence_refs":sorted(str(x) for x in refs),"safety_boundary":"This alert does not diagnose, prescribe, recommend a dose, alter titration or select treatment."}
    return {"alert_id":"RCA-"+hashlib.sha256(canonical(core).encode()).hexdigest()[:16].upper(),**core}

def main():
    p=argparse.ArgumentParser();p.add_argument("journey");p.add_argument("analytics");p.add_argument("schedule");p.add_argument("--policy",required=True);p.add_argument("--output",required=True);a=p.parse_args()
    journey=json.loads(Path(a.journey).read_text(encoding="utf-8"));analytics=json.loads(Path(a.analytics).read_text(encoding="utf-8"));schedule=json.loads(Path(a.schedule).read_text(encoding="utf-8"));policy=json.loads(Path(a.policy).read_text(encoding="utf-8"))
    result=evaluate(journey,analytics,schedule,policy);Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n");print(json.dumps({"valid":True,"alert_id":result["alert_id"],"alert_state":result["alert_state"]},indent=2));return 0
if __name__=="__main__": raise SystemExit(main())
