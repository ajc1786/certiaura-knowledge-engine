from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

BEGIN = "<!-- BEGIN AUTO-GENERATED LESSON LEDGER -->"
END = "<!-- END AUTO-GENERATED LESSON LEDGER -->"


def validate(repository: Path, current_build: str) -> list[str]:
    errors = []
    markdown_path = repository / "00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md"
    json_path = repository / "00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json"
    matrix_path = repository / "Documentation" / "Build_Records" / current_build / "LESSONS_LEARNED_CONTROL_MATRIX.json"
    if not markdown_path.is_file() or not json_path.is_file() or not matrix_path.is_file():
        return ["required accumulated lessons source or current matrix missing"]
    markdown = markdown_path.read_text(encoding="utf-8")
    control = json.loads(json_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    for path in (markdown_path, json_path):
        raw = path.read_bytes()
        if b"\r" in raw:
            errors.append("CR byte: " + str(path))
        if not raw.endswith(b"\n"):
            errors.append("final LF missing: " + str(path))
        for number, line in enumerate(raw.split(b"\n"), start=1):
            if line.endswith((b" ", b"\t")):
                errors.append(f"trailing whitespace: {path}:{number}")
    if BEGIN not in markdown or END not in markdown:
        errors.append("ledger markers missing")
    lessons = control.get("lessons")
    if not isinstance(lessons, list):
        errors.append("JSON lesson ledger invalid")
        lessons = []
    ids = [x.get("lesson_id") for x in lessons]
    if len(ids) != len(set(ids)):
        errors.append("duplicate lesson identifier")
    ledger = markdown.split(BEGIN, 1)[1].split(END, 1)[0] if BEGIN in markdown and END in markdown else ""
    for lesson_id in ids:
        if ledger.count("### " + str(lesson_id) + " - ") != 1:
            errors.append("Markdown JSON parity failure: " + str(lesson_id))
    current_items = matrix.get("lessons") or matrix.get("controls") or []
    current_ids = {x.get("lesson_id") for x in current_items if isinstance(x, dict)}
    if not current_ids.issubset(set(ids)):
        errors.append("current build lessons not merged")
    coverage = control.get("coverage", {})
    expected = set(coverage.get("mandatory_expected_builds", []))
    discovered = set(coverage.get("last_discovered_matrix_builds", coverage.get("last_discovered_builds", [])))
    ledger_only = set(coverage.get("last_ledger_only_builds", []))
    covered = set(coverage.get("last_covered_builds", []))
    declared_ledger_only = coverage.get("ledger_only_historical_evidence", {})
    if coverage.get("current_status") != "COMPLETE" or not expected.issubset(covered):
        errors.append("historical lessons coverage incomplete")
    if covered != discovered | ledger_only:
        errors.append("historical lessons coverage partition mismatch")
    for build_number in sorted(ledger_only):
        record = declared_ledger_only.get(build_number) if isinstance(declared_ledger_only, dict) else None
        if not isinstance(record, dict):
            errors.append("ledger-only historical evidence missing: " + build_number)
            continue
        declared_ids = sorted(record.get("lesson_ids", []))
        actual_ids = {
            lesson.get("lesson_id")
            for lesson in lessons
            if build_number in {str(value) for value in lesson.get("origin_builds", [])}
        }
        if not set(declared_ids).issubset(actual_ids):
            errors.append("ledger-only historical evidence set missing after merge: " + build_number)
    if control.get("automatic_update", {}).get("last_updated_build") != current_build:
        errors.append("current build auto-update marker missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--current-build", default="0052")
    parser.add_argument("--report")
    args = parser.parse_args()
    errors = validate(Path(args.repository).resolve(), args.current_build)
    result = {"valid": not errors, "result": "ACCUMULATED_LESSONS_SOURCE_VALIDATED" if not errors else "FAILED", "errors": errors}
    if args.report:
        Path(args.report).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    if not errors:
        print("ACCUMULATED_LESSONS_SOURCE_VALIDATED")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
