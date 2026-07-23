from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from retatrutide_knowledge_change_common import load_json, validate_bundle, validate_record


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Build 0053 Retatrutide knowledge-change records.")
    parser.add_argument("paths", nargs="+", help="JSON record files")
    parser.add_argument("--bundle", action="store_true", help="Also validate cross-record references")
    parser.add_argument("--report")
    args = parser.parse_args()
    records = []
    errors = []
    for raw in args.paths:
        path = Path(raw)
        try:
            data = load_json(path)
        except Exception as exc:
            errors.append(f"{path}: JSON load failed: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path}: root must be an object")
            continue
        records.append(data)
        errors.extend([f"{path}: {item}" for item in validate_record(data)])
    if args.bundle:
        errors.extend(validate_bundle(records))
    result = {"build_number":"0053","validated_files":[str(Path(p)) for p in args.paths],"bundle":args.bundle,"valid":not errors,"errors":errors,"result":"PASS" if not errors else "FAIL"}
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
