from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from datetime import datetime, timezone

UAI_RE = re.compile(r"CERT-[A-Z]{3}-\d{6}")
ID_RE = re.compile(r"(?:CLAIM|EVIDENCE|CERT-EKS|CERT-MKS|CERT-SKS|CERT-PKS|CERT-RKS)-[A-Z0-9_-]+", re.I)

def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")

def sha(obj):
    if isinstance(obj, (dict,list)): data=canonical_bytes(obj)
    elif isinstance(obj, bytes): data=obj
    else: data=str(obj).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def discover_sources(repo: Path, mode_terms, max_sources=8, max_excerpt=700):
    roots=[repo/p for p in ["01_Knowledge_Systems","02_Peptides","05_Monitoring","06_Evidence","12_Reports","Standards"]]
    candidates=[]
    for root in roots:
        if not root.exists(): continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in {".md",".json",".csv",".txt"}: continue
            try: text=p.read_text(encoding="utf-8",errors="strict")
            except Exception: continue
            low=text.lower()
            if "retatrutide" not in low: continue
            score=sum(low.count(t.lower()) for t in mode_terms)
            if score <= 0: continue
            excerpt=" ".join(text[:max_excerpt*3].split())[:max_excerpt]
            uai=(UAI_RE.search(text) or UAI_RE.search(p.name))
            ids=ID_RE.findall(text[:5000])
            review=None
            for marker in ["SCIENTIFICALLY_REVIEWED","REVIEWED","BASELINE","DRAFT","INCOMPLETE"]:
                if marker.lower() in low: review=marker; break
            candidates.append((score,str(p.relative_to(repo)).replace("\\","/"),excerpt,uai.group(0) if uai else None,ids[0] if ids else None,review))
    candidates.sort(key=lambda x:(-x[0],x[1]))
    return [{"repository_path":r,"uai":u,"claim_or_evidence_id":i,"review_status":rv,"excerpt":e,"excerpt_sha256":sha(e)} for _,r,e,u,i,rv in candidates[:max_sources]]

import argparse

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("query"); ap.add_argument("--repository",required=True); ap.add_argument("--policy",default=None); ap.add_argument("--output",required=True); a=ap.parse_args()
    q=load_json(a.query); repo=Path(a.repository)
    policy_path=Path(a.policy) if a.policy else repo/"13_Project_Genesis/AI/retatrutide_ai_query_policy.json"
    policy=load_json(policy_path)
    text=q.get("query_text",""); low=text.lower(); qh=sha(q); warnings=list(policy["mandatory_warnings"])
    if any(t in low for t in policy["urgent_terms"]):
        state="URGENT_CLINICAL_ROUTING"; answer="Seek urgent professional medical assessment now. This system cannot assess or rule out an emergency."
        sources=[]
    elif q.get("request_context",{}).get("personalised_medical_request") or any(t in low for t in policy["refusal_terms"]):
        state="REFUSED_SAFETY_BOUNDARY"; answer="I cannot provide personal dosing, titration, diagnosis, procurement or treatment-selection instructions. Use the cited educational material to prepare questions for a qualified clinician."
        sources=[]
    else:
        mode=q.get("query_mode")
        terms=policy["mode_terms"].get(mode,[])+[x for x in re.findall(r"[a-z0-9-]{4,}",low) if x not in {"what","with","that","this","from","retatrutide"}][:8]
        sources=discover_sources(repo,terms,policy["max_sources"],policy["max_excerpt_characters"])
        if not sources:
            state="ABSTAINED_INSUFFICIENT_EVIDENCE"; answer="The canonical repository did not resolve sufficient reviewed retatrutide sources for this query. No answer has been inferred from model memory."
        else:
            state="ANSWERED_GROUNDED"
            bullets=[]
            for s in sources[:5]:
                excerpt=s["excerpt"]
                bullets.append(f"- {excerpt} [source: {s['repository_path']}]")
            answer="Grounded repository extracts:\n"+"\n".join(bullets)+"\n\nThese extracts require interpretation within their recorded review status and do not establish individual clinical suitability."
    retrieval_hash=sha([{k:v for k,v in s.items() if k!="excerpt"} for s in sources])
    result={"schema_version":"1.0.0","query_id":"RAI-"+qh[:16].upper(),"policy_version":policy["policy_version"],"generated_at_utc":now(),"query_sha256":qh,"retrieval_set_sha256":retrieval_hash,"response_state":state,"answer":answer,"warnings":warnings,"sources":sources}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"valid":True,"query_id":result["query_id"],"response_state":state,"source_count":len(sources)},indent=2))
if __name__=="__main__": main()
