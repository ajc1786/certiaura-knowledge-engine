from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

URGENT_TERMS = (
    "severe abdominal pain", "chest pain", "difficulty breathing",
    "fainting", "suicidal thoughts", "persistent vomiting",
)
IDENTIFIER_PATTERNS = (
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"(?<!\d)(?:\+?44\s?7\d{3}|07\d{3})[\s-]?\d{3}[\s-]?\d{3}(?!\d)"),
    re.compile(r"\b(?:name|address|postcode|nhs number)\s*[:=]", re.I),
)
EVENT_FIELDS = ("journey_id", "observed_at", "event_type", "payload", "source_refs")

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()

def contains_identifier(value):
    text = canonical(value)
    return any(pattern.search(text) for pattern in IDENTIFIER_PATTERNS)

def urgent(value):
    text = canonical(value).lower()
    return any(term in text for term in URGENT_TERMS)

def normalise_event(event, journey_id):
    if not isinstance(event, dict):
        raise ValueError("Journey event must be an object")
    if contains_identifier(event):
        raise ValueError("IDENTIFIABLE_INPUT_REJECTED")
    if event.get("journey_id") != journey_id:
        raise ValueError("Journey identifier mismatch")
    missing = [field for field in EVENT_FIELDS if field not in event]
    if missing:
        raise ValueError("Journey event missing fields: " + ", ".join(missing))
    core = {field: event[field] for field in EVENT_FIELDS}
    return {**core, "event_id": "RJE-" + digest(core)[:16].upper()}

def append_event(journey, event):
    journey_id = journey.get("journey_id")
    if not journey_id:
        raise ValueError("Journey identifier missing")
    candidates = list(journey.get("events", [])) + [event]
    events = [normalise_event(item, journey_id) for item in candidates]
    events.sort(key=lambda item: (item["observed_at"], item["event_id"]))
    head = "0" * 64
    rebuilt = []
    for item in events:
        base = {field: item[field] for field in EVENT_FIELDS}
        base["event_id"] = item["event_id"]
        base["prior_chain_hash"] = head
        base["event_hash"] = digest(base)
        head = base["event_hash"]
        rebuilt.append(base)
    state = "LOCKED_URGENT_ROUTING" if any(urgent(item) for item in rebuilt) else "ACTIVE"
    return {
        "journey_id": journey_id,
        "version": "1.0.0",
        "journey_state": state,
        "events": rebuilt,
        "chain_head": head,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("event")
    parser.add_argument("--journey")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    journey = (
        json.loads(Path(args.journey).read_text(encoding="utf-8"))
        if args.journey
        else {
            "journey_id": event["journey_id"],
            "version": "1.0.0",
            "journey_state": "ACTIVE",
            "events": [],
            "chain_head": "0" * 64,
        }
    )
    result = append_event(journey, event)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "valid": True,
        "journey_id": result["journey_id"],
        "journey_state": result["journey_state"],
        "event_count": len(result["events"]),
        "chain_head": result["chain_head"],
    }, indent=2))

if __name__ == "__main__":
    main()
