from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

POLICY_VERSION = "1.0.0"
ALLOWED_AUDIENCES = {"PUBLIC", "PATIENT_DISCUSSION_SUPPORT", "PROFESSIONAL", "INTERNAL_REVIEW"}
ALLOWED_MODES = {"evidence_summary", "clinical_outcomes", "safety_monitoring", "contraindications", "patient_journey", "source_lookup"}
PSEUDONYM_RE = re.compile(r"^[A-Z0-9_-]{4,40}$")

def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha(value) -> str:
    data = canonical_bytes(value) if isinstance(value, (dict, list)) else str(value).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate_request(request: dict, policy: dict) -> None:
    required = {"schema_version", "session_reference", "audience", "patient_reference", "turns"}
    missing = sorted(required - set(request))
    if missing:
        raise ValueError("Missing request fields: " + ", ".join(missing))
    if request["schema_version"] != "1.0.0":
        raise ValueError("Unsupported schema_version")
    if not PSEUDONYM_RE.fullmatch(str(request["session_reference"])):
        raise ValueError("session_reference is not pseudonymous-format compliant")
    patient_reference = request.get("patient_reference")
    if patient_reference is not None and not PSEUDONYM_RE.fullmatch(str(patient_reference)):
        raise ValueError("patient_reference is not pseudonymous-format compliant")
    if request["audience"] not in ALLOWED_AUDIENCES:
        raise ValueError("Unsupported audience")
    turns = request["turns"]
    if not isinstance(turns, list) or not turns:
        raise ValueError("At least one turn is required")
    if len(turns) > int(policy["max_turns"]):
        raise ValueError("Turn limit exceeded")
    for index, turn in enumerate(turns, 1):
        if set(turn) != {"query_text", "query_mode", "personalised_medical_request"}:
            raise ValueError(f"Turn {index} has invalid fields")
        if not isinstance(turn["query_text"], str) or not 3 <= len(turn["query_text"]) <= 1200:
            raise ValueError(f"Turn {index} query_text length is invalid")
        if turn["query_mode"] not in ALLOWED_MODES:
            raise ValueError(f"Turn {index} query mode is invalid")
        if not isinstance(turn["personalised_medical_request"], bool):
            raise ValueError(f"Turn {index} personalised_medical_request must be boolean")

def detect_identifier(text: str, policy: dict):
    for entry in policy["direct_identifier_patterns"]:
        if re.search(entry["pattern"], text):
            return entry["name"]
    return None

def safe_source(source: dict) -> dict:
    return {
        "repository_path": source.get("repository_path"),
        "uai": source.get("uai"),
        "claim_or_evidence_id": source.get("claim_or_evidence_id"),
        "review_status": source.get("review_status"),
        "source_status": source.get("source_status", "RESOLVED")
    }

def invoke_query_engine(query_script: Path, repository: Path, query: dict) -> dict:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="certiaura_0044_query_") as temp:
        root = Path(temp)
        query_path = root / "query.json"
        output_path = root / "response.json"
        query_path.write_text(json.dumps(query, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        completed = subprocess.run(
            [sys.executable, "-B", str(query_script), str(query_path), "--repository", str(repository), "--output", str(output_path)],
            capture_output=True, text=True, encoding="utf-8", env=env, check=False
        )
        if completed.returncode != 0:
            raise RuntimeError("Build 0043 query engine failed: " + (completed.stderr.strip() or completed.stdout.strip()))
        return load_json(output_path)

def run_session(request: dict, repository: Path, policy: dict) -> dict:
    validate_request(request, policy)
    query_script = repository / "Scripts/query_retatrutide_knowledge.py"
    if not query_script.is_file():
        raise FileNotFoundError("Build 0043 query engine is not installed")
    session_id = "RCW-" + sha(request)[:16].upper()
    exchanges = []
    urgent_lock = False
    session_state = "ACTIVE_WITH_ABSTENTION"
    for turn_number, turn in enumerate(request["turns"], 1):
        query_hash = sha(turn)
        if urgent_lock:
            response = {
                "response_state": "URGENT_CLINICAL_ROUTING",
                "answer": "This session remains locked to urgent clinical routing. Seek urgent professional medical assessment now before continuing with routine educational questions.",
                "warnings": list(policy["mandatory_warnings"]),
                "sources": [], "query_sha256": query_hash, "retrieval_set_sha256": sha([])
            }
            session_state = "LOCKED_URGENT_ROUTING"
        else:
            identifier_type = detect_identifier(turn["query_text"], policy)
            if identifier_type:
                response = {
                    "response_state": "REFUSED_IDENTIFIABLE_INPUT",
                    "answer": "Direct identifying information was detected and was not processed. Remove names, contact details, dates of birth and health-service identifiers, then use a pseudonymous reference.",
                    "warnings": list(policy["mandatory_warnings"]),
                    "sources": [], "query_sha256": query_hash, "retrieval_set_sha256": sha([]),
                    "identifier_type": identifier_type
                }
                session_state = "IDENTIFIABLE_INPUT_REJECTED"
            else:
                query = {
                    "schema_version": "1.0.0", "query_text": turn["query_text"], "query_mode": turn["query_mode"],
                    "request_context": {
                        "audience": request["audience"],
                        "personalised_medical_request": turn["personalised_medical_request"],
                        "patient_reference": request.get("patient_reference")
                    }
                }
                response = invoke_query_engine(query_script, repository, query)
                state = response["response_state"]
                if state == "URGENT_CLINICAL_ROUTING":
                    urgent_lock = True
                    session_state = "LOCKED_URGENT_ROUTING"
                elif state == "REFUSED_SAFETY_BOUNDARY":
                    session_state = "SAFETY_BOUNDARY_ENFORCED"
                elif state == "ABSTAINED_INSUFFICIENT_EVIDENCE":
                    session_state = "ACTIVE_WITH_ABSTENTION"
                else:
                    session_state = "ACTIVE_GROUNDED"
        exchanges.append({
            "turn_number": turn_number, "query_sha256": response.get("query_sha256", query_hash),
            "query_mode": turn["query_mode"], "response_state": response["response_state"],
            "answer": response["answer"], "warnings": response.get("warnings", list(policy["mandatory_warnings"])),
            "retrieval_set_sha256": response.get("retrieval_set_sha256", sha([])),
            "sources": [safe_source(source) for source in response.get("sources", [])]
        })
    if len(request["turns"]) >= int(policy["max_turns"]) and not urgent_lock:
        session_state = "TURN_LIMIT_REACHED"
    return {
        "schema_version": "1.0.0", "session_id": session_id, "policy_version": POLICY_VERSION,
        "session_state": session_state, "urgent_lock": urgent_lock, "turn_count": len(exchanges),
        "exchanges": exchanges, "warnings": list(policy["mandatory_warnings"])
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--policy", default=None)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    repository = Path(args.repository).resolve()
    policy_path = Path(args.policy).resolve() if args.policy else repository / "13_Project_Genesis/AI/retatrutide_controlled_conversation_policy.json"
    result = run_session(load_json(Path(args.request)), repository, load_json(policy_path))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"valid": True, "session_id": result["session_id"], "session_state": result["session_state"], "turn_count": result["turn_count"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
