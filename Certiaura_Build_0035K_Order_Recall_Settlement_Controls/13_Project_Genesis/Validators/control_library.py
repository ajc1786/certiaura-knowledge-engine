from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def nonempty(value): return value is not None and value != '' and value != [] and value != {}
def distinct_people(items):
    ids=[x.get('person_id') for x in items if x.get('person_id')]
    return len(ids)==len(set(ids))
def approvals_ok(items, roles, minimum=2):
    if not isinstance(items,list) or len(items)<minimum or not distinct_people(items): return False
    found={x.get('role') for x in items if x.get('decision','APPROVE')=='APPROVE' and x.get('conflict_declared') is False}
    return set(roles).issubset(found)
def cli_result(errors):
    if errors:
        print(f'FAIL — {len(errors)} control breaches detected')
        for i,e in enumerate(errors,1): print(f'{i}. {e}')
        return 1
    print('PASS')
    return 0
