from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

FORBIDDEN_KEYS={"name","full_name","patient_name","email","phone","telephone","address","postcode","date_of_birth","dob","nhs_number","direct_identifiers"}
EMAIL=re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I)
PHONE=re.compile(r"(?<!\d)(?:\+?44\s?7\d{3}|0?7\d{3})[\s-]?\d{3}[\s-]?\d{3}(?!\d)")

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)

def reject_identifiers(value,path="root"):
    if isinstance(value,dict):
        for key,item in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                raise ValueError("IDENTIFIABLE_INPUT_REJECTED: forbidden key at "+path+"."+str(key))
            reject_identifiers(item,path+"."+str(key))
    elif isinstance(value,list):
        for index,item in enumerate(value): reject_identifiers(item,f"{path}[{index}]")
    elif isinstance(value,str) and (EMAIL.search(value) or PHONE.search(value)):
        raise ValueError("IDENTIFIABLE_INPUT_REJECTED: direct identifier pattern at "+path)

def direction(delta,tolerance=1e-9):
    if delta>tolerance: return "INCREASE"
    if delta<-tolerance: return "DECREASE"
    return "STABLE"

def analyze(journey,policy):
    reject_identifiers(journey)
    events=journey.get("events")
    if not isinstance(events,list): raise ValueError("Journey events must be an array")
    ordered=sorted(events,key=lambda e:(str(e.get("observed_at","")),str(e.get("event_id",""))))
    metrics=[]
    all_sources=set()
    for event in ordered:
        all_sources.update(str(x) for x in event.get("source_refs",[]) if str(x))
    for metric,config in policy.get("tracked_metrics",{}).items():
        observations=[]
        for event in ordered:
            payload=event.get("payload") or {}
            value=payload.get(metric)
            if isinstance(value,(int,float)) and not isinstance(value,bool):
                observations.append({"observed_at":event.get("observed_at"),"value":float(value),"event_id":event.get("event_id"),"source_refs":event.get("source_refs",[])})
        if observations:
            first=observations[0]["value"]; latest=observations[-1]["value"]; delta=latest-first
            percent=None if abs(first)<1e-12 else round((delta/first)*100.0,4)
            state="SUFFICIENT" if len(observations)>=int(config.get("minimum_observations",2)) else "INSUFFICIENT"
            metrics.append({
              "metric":metric,"label":config.get("label",metric),"unit":config.get("unit",""),"observation_count":len(observations),
              "data_state":state,"first_value":first,"latest_value":latest,"absolute_change":round(delta,4),"percentage_change":percent,
              "direction":direction(delta),"first_observed_at":observations[0]["observed_at"],"latest_observed_at":observations[-1]["observed_at"],
              "source_event_ids":[x["event_id"] for x in observations if x.get("event_id")],
              "source_refs":sorted({str(r) for x in observations for r in x.get("source_refs",[]) if str(r)}),
              "evidence_refs":sorted({str(r) for r in config.get("evidence_refs",[]) if str(r)})
            })
    sufficient=[m for m in metrics if m["data_state"]=="SUFFICIENT"]
    state="LOCKED_URGENT_ROUTING" if journey.get("journey_state")=="LOCKED_URGENT_ROUTING" else ("READY_FOR_REVIEW" if sufficient else "INSUFFICIENT_DATA")
    core={"journey_id":journey.get("journey_id"),"journey_state":journey.get("journey_state","ACTIVE"),"analytics_state":state,"event_count":len(ordered),"metrics":metrics,"provenance":{"chain_head":journey.get("chain_head"),"source_refs":sorted(all_sources),"policy_id":policy.get("policy_id")},"safety_boundary":"Descriptive analytics only. This output does not diagnose, recommend treatment, select a dose or alter titration."}
    result={"analytics_id":"RLA-"+hashlib.sha256(canonical(core).encode()).hexdigest()[:16].upper(),**core}
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("journey");p.add_argument("--policy",required=True);p.add_argument("--output",required=True);a=p.parse_args()
    journey=json.loads(Path(a.journey).read_text(encoding="utf-8"));policy=json.loads(Path(a.policy).read_text(encoding="utf-8"))
    result=analyze(journey,policy);Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n");print(json.dumps({"valid":True,"analytics_id":result["analytics_id"],"analytics_state":result["analytics_state"],"metric_count":len(result["metrics"])},indent=2));return 0
if __name__=="__main__": raise SystemExit(main())
