from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from asset_register_reconciler import (
    CANONICAL_REGISTER_RELATIVE_PATH,
    UAI_RE,
    load_register,
    norm_path,
    resolve_register,
)
from historical_asset_backfill import reconcile_full_historical_repository, _deserialise_paths

BUILD_RECORD = Path("Documentation/Build_Records/0038")
MANIFEST = BUILD_RECORD / "ASSET_INTENT_MANIFEST.json"
POLICY = BUILD_RECORD / "HISTORICAL_ASSET_BACKFILL_POLICY.json"
REPAIR_REPORT = BUILD_RECORD / "MASTER_ASSET_REGISTER_REPAIR_REPORT.json"
CENSUS_REPORT = BUILD_RECORD / "HISTORICAL_ASSET_CENSUS_REPORT.json"
VERIFY_REPORT = BUILD_RECORD / "MASTER_ASSET_REGISTER_BUTTON_VERIFICATION.json"


def verify(repo: Path) -> dict:
    register = resolve_register(repo, CANONICAL_REGISTER_RELATIVE_PATH)
    rows, meta = load_register(register)
    valid_rows = []
    placeholders = []
    invalid = []
    duplicate_uai = []
    duplicate_paths = []
    missing_supporting_files = []
    seen_uai: dict[str, int] = {}
    seen_path: dict[str, int] = {}
    for index, row in enumerate(rows):
        uai = row.get("Universal Asset Identifier", "").strip()
        path = norm_path(row.get("Repository Path"))
        title = row.get("Asset Title") or row.get("Asset Name", "")
        if "NO NEW UAI" in uai.upper() or uai.upper() in {"NO UAI", "TBC", "TBD", "PENDING", "UNALLOCATED"}:
            placeholders.append({"row": index, "uai": uai, "title": title})
        if not UAI_RE.fullmatch(uai):
            invalid.append({"row": index, "uai": uai, "title": title, "path": path})
        if not path:
            invalid.append({"row": index, "code": "MISSING_REPOSITORY_PATH", "uai": uai, "title": title})
        if UAI_RE.fullmatch(uai) and path:
            valid_rows.append(row)
        if uai:
            if uai in seen_uai:
                duplicate_uai.append({"uai": uai, "rows": [seen_uai[uai], index]})
            seen_uai[uai] = index
        if path:
            if path in seen_path:
                duplicate_paths.append({"path": path, "rows": [seen_path[path], index]})
            seen_path[path] = index
        for supporting in _deserialise_paths(row.get("Supporting Files", "")):
            supporting_path = norm_path(supporting)
            if not supporting_path:
                continue
            if supporting_path in seen_path:
                duplicate_paths.append({"path": supporting_path, "rows": [seen_path[supporting_path], index], "kind": "SUPPORTING_FILE_COLLISION"})
            seen_path[supporting_path] = index
            target = repo.joinpath(*Path(supporting).parts)
            if not target.is_file():
                missing_supporting_files.append({"row": index, "path": supporting})
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "canonical_register_path": CANONICAL_REGISTER_RELATIVE_PATH.as_posix(),
        "resolved_register_path": register.relative_to(repo).as_posix(),
        "row_count": len(rows),
        "valid_asset_rows": len(valid_rows),
        "legacy_placeholder_rows": placeholders,
        "invalid_rows": invalid,
        "duplicate_uai": duplicate_uai,
        "duplicate_paths": duplicate_paths,
        "missing_supporting_files": missing_supporting_files,
        "button_open_target_verified": register == (repo / CANONICAL_REGISTER_RELATIVE_PATH).resolve(),
    }
    report["valid"] = (
        report["button_open_target_verified"] and
        len(valid_rows) >= 10 and
        not placeholders and not invalid and not duplicate_uai and not duplicate_paths and not missing_supporting_files
    )
    return report


def run(repo: Path, apply: bool, open_after: bool = False) -> dict:
    repo = repo.resolve()
    register = resolve_register(repo, CANONICAL_REGISTER_RELATIVE_PATH)
    backup = repo / ".certiaura_backups" / f"master_asset_register_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"
    if apply:
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(register, backup)
    try:
        result = reconcile_full_historical_repository(
            repo,
            repo / MANIFEST,
            repo / POLICY,
            CANONICAL_REGISTER_RELATIVE_PATH,
            additional_files=None,
            apply=apply,
            report_path=repo / REPAIR_REPORT,
            census_report_path=repo / CENSUS_REPORT,
        )
        verification = verify(repo) if apply and result.get("applied") else {"valid": False, "not_applied": True}
        if apply:
            (repo / VERIFY_REPORT).write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
        if apply and not verification.get("valid"):
            shutil.copy2(backup, register)
            result["applied"] = False
            result["rolled_back"] = True
            result["verification"] = verification
        else:
            result["verification"] = verification
            if apply:
                result["backup_path"] = str(backup)
        if open_after and apply and result.get("applied") and os.name == "nt":
            os.startfile(register)  # type: ignore[attr-defined]
        return result
    except Exception as exc:
        if apply and backup.is_file():
            shutil.copy2(backup, register)
        return {"valid": False, "applied": False, "rolled_back": bool(apply), "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair and fully populate the canonical Certiaura Master Asset Register")
    parser.add_argument("repository", nargs="?", type=Path, default=HERE.parents[2])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = run(args.repository, args.apply, args.open)
    payload = json.dumps(result, indent=2)
    print(payload)
    if args.report:
        target = args.report if args.report.is_absolute() else args.repository / args.report
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload + "\n", encoding="utf-8")
    return 0 if result.get("valid") and (not args.apply or result.get("applied")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
