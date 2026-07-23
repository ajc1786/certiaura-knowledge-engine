from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from tesamorelin_pilot_common import load_json, validate_record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    parser.add_argument("--report")
    args = parser.parse_args()
    errors = validate_record(load_json(args.record))
    result = {
        "valid": not errors,
        "errors": errors,
        "result": "TESAMORELIN_PILOT_RECORD_VALIDATED" if not errors else "FAIL",
    }
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
