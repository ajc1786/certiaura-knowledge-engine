from __future__ import annotations
import json, re, sys
from pathlib import Path, PurePosixPath

def norm(v): return re.sub(r"\W+","",str(v or "").lower())
def duplicate_key(record):
    ids=record.get("identifiers",{}) if isinstance(record,dict) else {}
    for key in ("doi","pmid","pmcid","nct"):
        if ids.get(key): return f"{key}:{norm(ids[key])}"
    return f"fallback:{norm(record.get('title'))}:{str(record.get('publication_date',''))[:4]}"
def main():
    records=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    seen={}; duplicates=[]
    for record in records:
        key=duplicate_key(record)
        if key in seen: duplicates.append({"key":key,"first":seen[key],"duplicate":record.get("citation_id")})
        else: seen[key]=record.get("citation_id")
    print(json.dumps({"valid":not duplicates,"duplicates":duplicates},indent=2))
    raise SystemExit(1 if duplicates else 0)
if __name__=="__main__": main()
