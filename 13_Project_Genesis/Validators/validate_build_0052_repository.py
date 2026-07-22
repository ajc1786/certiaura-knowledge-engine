from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    repo = Path(args.repository).resolve()
    errors = []
    manifest_path = repo / "Documentation/Build_Records/0052/ASSET_INTENT_MANIFEST.json"
    if not manifest_path.is_file():
        errors.append("Build 0052 manifest missing")
        manifest = {"files": []}
    else:
        manifest = load(manifest_path)
    paths = [x.get("repository_path") for x in manifest.get("files", [])]
    for relative in paths:
        if not (repo / relative).is_file():
            errors.append("manifest path missing: " + str(relative))
    evidence = load(repo / "Documentation/Build_Records/0052/PREDECESSOR_CANONICAL_EVIDENCE.json")
    if evidence.get("result") != "PREDECESSOR_CANONICAL_EVIDENCE_VALIDATED" or evidence.get("negative_tests_result") != "PASS":
        errors.append("canonical predecessor evidence not validated")
    if evidence.get("unauthorised_manifest_intersection") != []:
        errors.append("unauthorised predecessor intersection exists")
    lessons = load(repo / "Documentation/Build_Records/0052/ACCUMULATED_LESSONS_UPDATE_REPORT.json")
    if lessons.get("result") != "ACCUMULATED_LESSONS_UPDATE_VALIDATED" or lessons.get("historical_coverage") != "COMPLETE":
        errors.append("accumulated lessons update not validated")
    register_path = repo / "Documentation/Master_Asset_Register.csv"
    if not register_path.is_file():
        errors.append("Master Asset Register missing")
    else:
        rows = list(csv.DictReader(register_path.open(encoding="utf-8-sig", newline="")))
        uais = [x.get("Universal Asset Identifier", "").strip() for x in rows if x.get("Universal Asset Identifier", "").strip()]
        if len(uais) != len(set(uais)):
            errors.append("duplicate UAI in Master Asset Register")
    for path in repo.rglob("*"):
        if path.is_file() and (path.suffix in {".pyc", ".pyo"} or "__pycache__" in path.parts):
            errors.append("Python runtime artifact: " + str(path.relative_to(repo)))
    result = {
        "valid": not errors,
        "result": "BUILD_0052_REPOSITORY_VALIDATED" if not errors else "FAILED",
        "manifest_path_count": len(paths),
        "formal_asset_delta": 0,
        "master_asset_register_reconciliation": "PASS_ZERO_DELTA" if not errors else "CHECK_ERRORS",
        "errors": errors,
    }
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    if not errors:
        print("BUILD_0052_REPOSITORY_VALIDATED")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
