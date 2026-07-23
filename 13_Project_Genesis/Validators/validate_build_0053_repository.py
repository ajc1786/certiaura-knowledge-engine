from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from build_0053_asset_ownership import load_manifest, owned_paths
from retatrutide_knowledge_change_common import load_json, validate_record

EXPECTED_COMMIT = "890df218b4f4dea92f4ccfa36b8106de59eca1b1"
EXPECTED_WITHDRAWN = ["RC1", "RC2", "RC3", "RC4", "RC5"]
CONTINUITY_MARKER = "<!-- CERTIAURA_BUILD_0053_CHECKPOINT_START -->"
LESSONS_MARKER = "<!-- CERTIAURA_BUILD_0053_LESSONS_START -->"


def normalise(value: str) -> str:
    return value.replace("\\", "/")


def find_header(headers: list[str], candidates: set[str]) -> str | None:
    for header in headers:
        if header.strip().lower() in candidates:
            return header
    return None


def validate(
    repo: Path,
    report_path: Path | None = None,
    expected_predecessor_commit: str = EXPECTED_COMMIT,
) -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = repo / "Documentation/Build_Records/0053/ASSET_INTENT_MANIFEST.json"
    if not manifest_path.exists():
        return {
            "build_number": "0053",
            "valid": False,
            "errors": ["Build 0053 Asset Intent Manifest missing"],
            "result": "FAIL",
        }

    manifest = load_manifest(manifest_path)
    skipped_report_rel = None
    if report_path is not None:
        try:
            skipped_report_rel = normalise(str(report_path.resolve().relative_to(repo.resolve())))
        except ValueError:
            skipped_report_rel = None

    for rel in owned_paths(manifest):
        if rel == skipped_report_rel:
            continue
        if not (repo / rel).is_file():
            errors.append(f"owned path missing: {rel}")

    example_items = [
        item
        for item in manifest.get("files", [])
        if item.get("classification") == "EXAMPLE"
    ]
    for item in example_items:
        rel = normalise(str(item["repository_path"]))
        path = repo / rel
        if not path.exists():
            continue
        try:
            validation_errors = validate_record(load_json(path))
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        if path.name.startswith(("valid_", "conditional_")):
            errors.extend(f"{path.name}: {message}" for message in validation_errors)
        elif path.name.startswith("invalid_") and not validation_errors:
            errors.append(f"{path.name}: deliberately defective example unexpectedly passed")

    predecessor_path = (
        repo / "Documentation/Build_Records/0053/PREDECESSOR_CANONICAL_EVIDENCE.json"
    )
    if not predecessor_path.exists():
        errors.append("canonical predecessor evidence missing")
    else:
        try:
            evidence = json.loads(predecessor_path.read_text(encoding="utf-8"))
            checks = {
                "source": "CANONICAL_GIT_OBJECTS",
                "predecessor_build": "0052",
                "predecessor_candidate": "RC6",
                "predecessor_commit": expected_predecessor_commit,
                "predecessor_path_count": 59,
                "withdrawn_candidates": EXPECTED_WITHDRAWN,
            }
            for key, expected in checks.items():
                if evidence.get(key) != expected:
                    errors.append(f"predecessor evidence {key} mismatch")
            if evidence.get("prohibited_intersection"):
                errors.append("prohibited predecessor/current-build intersection exists")
            if evidence.get("result") != "PREDECESSOR_CANONICAL_SOURCE_VERIFIED":
                errors.append("predecessor source was not verified")
        except Exception as exc:
            errors.append(f"canonical predecessor evidence unreadable: {exc}")

    continuity = repo / "00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md"
    lessons = repo / "00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md"
    lessons_control = repo / "00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json"
    if continuity.exists() and CONTINUITY_MARKER not in continuity.read_text(encoding="utf-8"):
        errors.append("Build 0053 continuity checkpoint marker missing")
    if lessons.exists() and LESSONS_MARKER not in lessons.read_text(encoding="utf-8"):
        errors.append("Build 0053 accumulated lessons marker missing")
    if lessons_control.exists():
        try:
            control = json.loads(lessons_control.read_text(encoding="utf-8"))
            updates = control.get("build_updates", [])
            if not any(str(item.get("build_number")) == "0053" for item in updates):
                errors.append("Build 0053 accumulated lessons control update missing")
        except Exception as exc:
            errors.append(f"accumulated lessons control unreadable: {exc}")

    register = repo / "Documentation/Master_Asset_Register.csv"
    if not register.exists():
        errors.append("Master Asset Register missing")
    else:
        with register.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = list(reader.fieldnames or [])
            rows = list(reader)
        path_col = find_header(
            headers,
            {"repository path", "canonical path", "path", "repository_path"},
        )
        uai_col = find_header(
            headers,
            {
                "universal asset identifier",
                "uai",
                "universal_asset_identifier",
            },
        )
        if not path_col or not uai_col:
            errors.append("Master Asset Register path/UAI columns unresolved")
        else:
            by_path = {
                normalise(str(row.get(path_col, ""))).lower(): row
                for row in rows
                if str(row.get(path_col, "")).strip()
            }
            for item in manifest.get("files", []) + manifest.get("generated_files", []):
                if item.get("classification") != "FORMAL_ASSET":
                    continue
                rel = normalise(str(item["repository_path"]))
                row = by_path.get(rel.lower())
                if not row:
                    errors.append(f"formal asset not registered: {rel}")
                elif not str(row.get(uai_col, "")).strip():
                    errors.append(f"formal asset has blank UAI: {rel}")

    result = {
        "build_number": "0053",
        "owned_path_count": len(owned_paths(manifest)),
        "example_count": len(example_items),
        "valid": not errors,
        "errors": errors,
        "result": "BUILD_0053_REPOSITORY_VALIDATED" if not errors else "FAIL",
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository")
    parser.add_argument("--report")
    parser.add_argument(
        "--expected-predecessor-commit",
        default=EXPECTED_COMMIT,
    )
    args = parser.parse_args()
    report = Path(args.report).resolve() if args.report else None
    result = validate(
        Path(args.repository).resolve(),
        report,
        args.expected_predecessor_commit,
    )
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
