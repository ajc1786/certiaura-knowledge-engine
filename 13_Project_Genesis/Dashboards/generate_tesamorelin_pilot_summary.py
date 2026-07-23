from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", nargs="+")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    records = [json.loads(Path(path).read_text(encoding="utf-8")) for path in args.records]
    by_type = {record.get("record_type"): record for record in records}
    result = {
        "build_number": "0056",
        "peptide": "Tesamorelin",
        "record_count": len(records),
        "evidence_corpus_state": by_type.get("tesamorelin_evidence_corpus_map", {}).get("coverage_state"),
        "biological_boundary_state": by_type.get("tesamorelin_biological_boundary", {}).get("boundary_state"),
        "safety_boundary_state": by_type.get("tesamorelin_safety_boundary", {}).get("boundary_state"),
        "monitoring_model_state": by_type.get("tesamorelin_monitoring_model", {}).get("model_state"),
        "pilot_decision": by_type.get("tesamorelin_controlled_pilot_acceptance", {}).get("decision"),
        "clinical_decision_support_authorised": False,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
