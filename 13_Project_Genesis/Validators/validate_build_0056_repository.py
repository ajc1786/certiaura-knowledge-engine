from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_0056_asset_ownership import load_manifest, owned_paths
from tesamorelin_pilot_common import load_json, validate_record

EXPECTED_COMMIT = "977829a987baf744beab4762478d9f0a88165fb0"
CHECKPOINT_MARKER = "<!-- CERTIAURA_BUILD_0056_CHECKPOINT_START -->"
LESSONS_MARKER = "<!-- CERTIAURA_BUILD_0056_LESSONS_START -->"


def normalise(value):
    return value.replace("\\", "/")


def validate(repository, report_path=None, expected_predecessor_commit=EXPECTED_COMMIT):
    repo = Path(repository).resolve()
    errors = []
    manifest_path = repo / "Documentation/Build_Records/0056/ASSET_INTENT_MANIFEST.json"
    if not manifest_path.exists():
        return {"build_number": "0056", "valid": False, "errors": ["Build 0056 Asset Intent Manifest missing"], "result": "FAIL"}
    manifest = load_manifest(manifest_path)
    skip = None
    if report_path:
        try:
            skip = normalise(str(Path(report_path).resolve().relative_to(repo)))
        except ValueError:
            pass
    for rel in owned_paths(manifest):
        if rel != skip and not (repo / rel).is_file():
            errors.append(f"owned path missing: {rel}")

    example_items = [item for item in manifest.get("files", []) if item.get("classification") == "EXAMPLE"]
    for item in example_items:
        path = repo / item["repository_path"]
        if not path.exists():
            continue
        validation_errors = validate_record(load_json(path))
        if path.name.startswith(("valid_", "conditional_")):
            errors.extend([f"{path.name}: {error}" for error in validation_errors])
        elif path.name.startswith("invalid_") and not validation_errors:
            errors.append(f"{path.name} unexpectedly passed")

    predecessor_path = repo / "Documentation/Build_Records/0056/PREDECESSOR_CANONICAL_EVIDENCE.json"
    if not predecessor_path.exists():
        errors.append("canonical predecessor evidence missing")
    else:
        evidence = json.loads(predecessor_path.read_text(encoding="utf-8"))
        checks = {
            "source": "CANONICAL_GIT_OBJECTS",
            "predecessor_build": "0055",
            "predecessor_candidate": "RC2",
            "predecessor_commit": expected_predecessor_commit,
            "predecessor_path_count": 89,
            "withdrawn_candidates": ["RC1"],
        }
        for key, expected in checks.items():
            if evidence.get(key) != expected:
                errors.append(f"predecessor evidence {key} mismatch")
        if evidence.get("prohibited_intersection"):
            errors.append("prohibited predecessor/current-build intersection exists")
        expected_overlap = ["13_Project_Genesis/Validators/verify_staged_byte_equality.py"]
        if evidence.get("approved_intersection") != expected_overlap:
            errors.append("approved predecessor intersection mismatch")

    for path, marker in [
        (repo / "00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md", CHECKPOINT_MARKER),
        (repo / "00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md", LESSONS_MARKER),
    ]:
        if path.exists() and marker not in path.read_text(encoding="utf-8"):
            errors.append(f"governance marker missing: {marker}")

    register = repo / "Documentation/Master_Asset_Register.csv"
    if not register.exists():
        errors.append("Master Asset Register missing")
    else:
        with register.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        by_path = {normalise(str(row.get("Repository Path", row.get("repository_path", "")))).lower(): row for row in rows}
        for item in manifest.get("files", []) + manifest.get("generated_files", []):
            if item.get("classification") == "FORMAL_ASSET":
                row = by_path.get(normalise(item["repository_path"]).lower())
                if not row:
                    errors.append(f"formal asset not registered: {item['repository_path']}")
                elif not str(row.get("Universal Asset Identifier", row.get("UAI", ""))).strip():
                    errors.append(f"formal asset blank UAI: {item['repository_path']}")

    result = {
        "build_number": "0056",
        "owned_path_count": len(owned_paths(manifest)),
        "example_count": len(example_items),
        "formal_asset_count": len([item for item in manifest.get("files", []) if item.get("classification") == "FORMAL_ASSET"]),
        "valid": not errors,
        "errors": errors,
        "result": "BUILD_0056_REPOSITORY_VALIDATED" if not errors else "FAIL",
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--report")
    parser.add_argument("--expected-predecessor-commit", default=EXPECTED_COMMIT)
    args = parser.parse_args()
    report = Path(args.report).resolve() if args.report else None
    result = validate(Path(args.repository).resolve(), report, args.expected_predecessor_commit)
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
