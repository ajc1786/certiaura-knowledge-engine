from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BUILD = "CERT-BUILD-0050"
MANIFEST_PATH = Path("Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json")
DIRECT = re.compile(
    r"\b(patient name|full name|date of birth|dob|nhs number|email address|phone number)\b",
    re.I,
)
TREATMENT = re.compile(
    r"\b(increase dose|decrease dose|continue treatment|stop treatment|prescribe|diagnose|safe to continue)\b",
    re.I,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text(obj):
    return json.dumps(obj, sort_keys=True)


def owned_example_paths(root: Path) -> tuple[list[Path], list[str]]:
    errors: list[str] = []
    manifest_file = root / MANIFEST_PATH
    if not manifest_file.is_file():
        return [], [f"missing exact Asset Intent Manifest: {MANIFEST_PATH.as_posix()}"]
    manifest = load(manifest_file)
    if manifest.get("build_id") != BUILD:
        errors.append("Asset Intent Manifest build_id mismatch")
    paths: list[Path] = []
    seen: set[str] = set()
    for item in manifest.get("files", []):
        if item.get("classification") != "EXAMPLE":
            continue
        if item.get("build_provenance") != BUILD:
            errors.append(f"example manifest provenance mismatch: {item.get('path')}")
            continue
        rel = str(item.get("path", "")).replace("\\", "/")
        if not rel or rel in seen:
            errors.append(f"invalid or duplicate example manifest path: {rel}")
            continue
        seen.add(rel)
        if not rel.startswith("12_Reports/Retatrutide/Examples/") or not rel.endswith(".json"):
            errors.append(f"example path outside controlled route: {rel}")
            continue
        path = root / rel
        if not path.is_file():
            errors.append(f"manifest-owned example missing: {rel}")
            continue
        paths.append(path)
    if not paths:
        errors.append("no exact Build 0050 example paths resolved from Asset Intent Manifest")
    return sorted(paths), errors


def validate(root: Path):
    errors: list[str] = []
    checked: list[str] = []
    examples, scope_errors = owned_example_paths(root)
    errors.extend(scope_errors)
    for path in examples:
        obj = load(path)
        checked.append(str(path.relative_to(root)).replace("\\", "/"))
        invalid = path.name.startswith("invalid_")
        local: list[str] = []
        if obj.get("build_provenance") != BUILD:
            local.append("build provenance mismatch")
        blob = text(obj)
        if DIRECT.search(blob):
            local.append("direct identifier language prohibited")
        if TREATMENT.search(blob):
            local.append("autonomous treatment language prohibited")
        if "closure_state" in obj:
            if obj.get("closure_state") == "CLOSURE_APPROVED" and (
                obj.get("open_action_count") != 0 or obj.get("urgent_routing_active")
            ):
                local.append("closure approval prerequisites not met")
            if obj.get("decision_actor_role") == "AI_SYSTEM":
                local.append("human closure decision required")
        if "source_hashes" in obj:
            for value in obj["source_hashes"]:
                if not re.fullmatch(r"[A-F0-9]{64}", value):
                    local.append("invalid source hash")
        if (
            "reviewer_actor_role" in obj
            and obj.get("reviewer_actor_role") == obj.get("generator_actor_role")
        ):
            local.append("reviewer separation required")
        if invalid and not local:
            errors.append(f"{path.name}: invalid fixture unexpectedly passed")
        if not invalid and local:
            errors.extend(f"{path.name}: {error}" for error in local)
    return {
        "valid": not errors,
        "errors": errors,
        "checked_paths": checked,
        "owned_path_count": len(checked),
        "build_provenance": BUILD,
        "ownership_scope": "EXACT_ASSET_INTENT_MANIFEST_PATHS",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = validate(args.root.resolve())
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
