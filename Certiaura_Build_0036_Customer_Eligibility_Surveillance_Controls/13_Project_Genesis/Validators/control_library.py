from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

AUTOMATION_ACTORS = {'automation','system','ai','algorithm','bot','auto'}

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def is_blank(v):
    return v is None or v == '' or v == [] or v == {}

def human(actor):
    if not isinstance(actor,str) or not actor.strip(): return False
    a=actor.strip().lower()
    return not any(x in a for x in AUTOMATION_ACTORS)

def parse_dt(v):
    if not isinstance(v,str) or not v: return None
    try: return datetime.fromisoformat(v.replace('Z','+00:00'))
    except Exception: return None

def require(errors, condition, code, message):
    if not condition: errors.append({'code':code,'message':message})

def output(record, errors):
    result={'valid':not errors,'breach_count':len(errors),'breaches':errors}
    print(json.dumps(result,indent=2))
    return 0 if not errors else 1
