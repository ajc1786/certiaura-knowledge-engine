from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

AUTOMATION_ACTORS = {'automation', 'system', 'ai', 'algorithm', 'bot', 'auto'}

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def nonempty(value):
    return value is not None and value != '' and value != [] and value != {}

def is_blank(value):
    return not nonempty(value)

def human(actor):
    if not isinstance(actor, str) or not actor.strip():
        return False
    lowered = actor.strip().lower()
    return not any(token in lowered for token in AUTOMATION_ACTORS)

def parse_dt(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None

def distinct_people(items):
    ids = [x.get('person_id') for x in items if isinstance(x, dict) and x.get('person_id')]
    return len(ids) == len(set(ids))

def approvals_ok(items, roles, minimum=2):
    if not isinstance(items, list) or len(items) < minimum or not distinct_people(items):
        return False
    found = {
        x.get('role') for x in items
        if isinstance(x, dict)
        and x.get('decision', 'APPROVE') == 'APPROVE'
        and x.get('conflict_declared') is False
    }
    return set(roles).issubset(found)

def require(errors, condition, code, message):
    if not condition:
        errors.append({'code': code, 'message': message})

def output(record, errors):
    result = {'valid': not errors, 'breach_count': len(errors), 'breaches': errors}
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1

def cli_result(errors):
    if errors:
        print(f'FAIL — {len(errors)} control breaches detected')
        for index, error in enumerate(errors, 1):
            if isinstance(error, dict):
                print(f"{index}. {error.get('code', 'CONTROL')}: {error.get('message', error)}")
            else:
                print(f'{index}. {error}')
        return 1
    print('PASS')
    return 0
