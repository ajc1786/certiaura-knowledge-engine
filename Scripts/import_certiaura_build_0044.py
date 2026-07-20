from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ALLOWED_ROOTS = {
    "00_Governance", "01_Knowledge_Systems", "02_Peptides", "03_Biology",
    "04_Conditions", "05_Monitoring", "06_Evidence", "07_Goals",
    "08_Product_Passports", "09_Cost_Intelligence", "10_Marketplace",
    "11_Academy", "12_Reports", "13_Project_Genesis", "Assets", "Database",
    "Documentation", "Images", "Schemas", "Scripts", "Standards", "Templates"
}
REQUIRED_COLUMNS = [
    "Universal Asset Identifier", "Asset Name", "Knowledge System", "Asset Type",
    "Status", "Owner", "Parent Assets", "Last Review", "Notes",
    "Repository Path", "Supporting Files", "Version", "Completion Percentage",
    "Child Assets", "Relationship List", "Evidence Links", "Report Links",
    "Marketplace Links", "Next Review", "Change History", "Build Provenance",
    "Source Builds", "Registration Basis", "File SHA256", "Last Updated"
]

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())

def read_register(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        missing = [column for column in REQUIRED_COLUMNS if column not in fields]
        if missing:
            raise RuntimeError("Master Asset Register missing columns: " + ", ".join(missing))
        return fields, list(reader)

def write_register(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    temporary = path.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)

def next_uai(rows: list[dict[str, str]], system: str, reserved: set[str]) -> str:
    pattern = re.compile(rf"^CERT-{re.escape(system)}-(\d{{6}})$")
    numbers = []
    for row in rows:
        match = pattern.fullmatch((row.get("Universal Asset Identifier") or "").strip())
        if match:
            numbers.append(int(match.group(1)))
    number = max(numbers, default=0) + 1
    candidate = f"CERT-{system}-{number:06d}"
    while candidate in reserved:
        number += 1
        candidate = f"CERT-{system}-{number:06d}"
    return candidate

def validate_register(rows: list[dict[str, str]], repository: Path) -> list[str]:
    errors: list[str] = []
    identifiers: dict[str, int] = {}
    paths: dict[str, int] = {}
    for index, row in enumerate(rows, 2):
        uai = (row.get("Universal Asset Identifier") or "").strip()
        path = (row.get("Repository Path") or "").strip().replace("\\", "/")
        if not uai:
            errors.append(f"Blank UAI at register row {index}")
        else:
            identifiers[uai] = identifiers.get(uai, 0) + 1
        if path:
            key = path.lower()
            paths[key] = paths.get(key, 0) + 1
            status = (row.get("Status") or "").upper()
            allowed_missing = any(word in status for word in ("RETIRED", "SUPERSEDED", "ARCHIVED"))
            if not allowed_missing and not (repository / Path(path)).is_file():
                errors.append(f"Register path does not resolve: {path}")
    for uai, count in identifiers.items():
        if count > 1:
            errors.append(f"Duplicate UAI: {uai}")
    for path, count in paths.items():
        if count > 1:
            errors.append(f"Duplicate canonical repository path: {path}")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--backup-root")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    package = Path(args.package).resolve()
    repository = Path(args.repository).resolve()
    report_path = Path(args.report).resolve()
    register_path = repository / "Documentation/Master_Asset_Register.csv"
    errors: list[str] = []
    conflicts: list[dict[str, str]] = []
    allocations: list[dict[str, str]] = []
    routing: list[dict[str, str]] = []
    backup_path: Path | None = None
    applied = False

    if not package.is_file():
        errors.append(f"Package not found: {package}")
    if not repository.is_dir():
        errors.append(f"Repository not found: {repository}")
    if not register_path.is_file():
        errors.append("Canonical Master Asset Register missing")
    if list(repository.rglob("Master_Asset_Register.csv")) != [register_path]:
        errors.append("Canonical Master Asset Register is missing or ambiguous")

    try:
        fields, rows = read_register(register_path) if register_path.is_file() else (REQUIRED_COLUMNS, [])
    except Exception as exc:
        errors.append(str(exc))
        fields, rows = REQUIRED_COLUMNS, []

    if errors:
        incoming_data = {}
        intent = {"assets": []}
        path_map = {}
        package_names = []
    else:
        with zipfile.ZipFile(package) as archive:
            package_names = [name for name in archive.namelist() if not name.endswith("/")]
            roots = {PurePosixPath(name).parts[0] for name in package_names}
            if roots - ALLOWED_ROOTS:
                errors.append("Unauthorised package root route")
            incoming_data = {name: archive.read(name) for name in package_names}
            intent = json.loads(incoming_data[
                "Documentation/Build_Records/0044/ASSET_INTENT_MANIFEST.json"
            ].decode("utf-8"))

        reserved = {
            (row.get("Universal Asset Identifier") or "").strip()
            for row in rows
            if (row.get("Universal Asset Identifier") or "").strip()
        }
        path_map: dict[str, dict] = {}
        for asset in intent.get("assets", []):
            source = asset["repository_path"]
            target = source
            uai = asset.get("existing_uai")
            if asset["classification"] == "FORMAL_ASSET" and not uai:
                uai = next_uai(rows, asset["knowledge_system"], reserved)
                reserved.add(uai)
                target = source.replace("__UAI__", uai)
                allocations.append({"source_path": source, "target_path": target, "uai": uai})
            path_map[source] = {"target": target, "uai": uai, "asset": asset}

        for name in package_names:
            target = path_map.get(name, {}).get("target", name)
            destination = repository / Path(target)
            incoming_hash = sha256_bytes(incoming_data[name])
            existing_hash = sha256_file(destination) if destination.is_file() else None
            action = path_map.get(name, {}).get("asset", {}).get("intended_action")
            allow_replace = path_map.get(name, {}).get("asset", {}).get("allow_replace", False)
            routing.append({
                "source": name,
                "target": target,
                "destination_state": "ABSENT" if existing_hash is None else (
                    "IDENTICAL" if existing_hash == incoming_hash else "NON_IDENTICAL"
                )
            })
            if existing_hash is not None and existing_hash != incoming_hash:
                if not (action == "UPDATE" and allow_replace):
                    conflicts.append({
                        "path": target,
                        "reason": "NON_IDENTICAL_EXISTING_FILE",
                        "resolution": "BLOCKED"
                    })

    expected_register_total = len(rows) + sum(
        1 for allocation in allocations
    )

    if args.apply and not errors and not conflicts:
        if not args.backup_root:
            errors.append("Backup root is required for apply")
        else:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path(args.backup_root).resolve() / f"Build_0044_Pre_Import_{stamp}"
            journal: list[tuple[str, Path, Path | None]] = []
            original_register = register_path.read_bytes()
            try:
                backup_path.mkdir(parents=True, exist_ok=False)
                shutil.copy2(register_path, backup_path / "Master_Asset_Register.csv")
                (backup_path / "TRANSACTION_METADATA.json").write_text(
                    json.dumps({
                        "build_number": "0044",
                        "created_utc": utc_now(),
                        "package": str(package),
                        "repository": str(repository),
                        "planned_file_count": len(routing),
                        "register_rows_before": len(rows)
                    }, indent=2) + "\n",
                    encoding="utf-8", newline="\n"
                )

                for item in routing:
                    source = item["source"]
                    target = item["target"]
                    destination = repository / Path(target)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    if destination.exists():
                        backup_file = backup_path / "files" / Path(target)
                        backup_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(destination, backup_file)
                        journal.append(("restore", destination, backup_file))
                    else:
                        journal.append(("delete", destination, None))

                    data = incoming_data[source]
                    allocation = path_map.get(source)
                    if allocation and allocation.get("uai"):
                        try:
                            text = data.decode("utf-8")
                            data = text.replace(
                                "UAI_ALLOCATION_REQUIRED", allocation["uai"]
                            ).encode("utf-8")
                        except UnicodeDecodeError:
                            pass
                    destination.write_bytes(data)

                for source, item in path_map.items():
                    asset = item["asset"]
                    if asset["classification"] != "FORMAL_ASSET":
                        continue
                    uai = item["uai"]
                    target = item["target"]
                    destination = repository / Path(target)
                    existing = next(
                        (
                            row for row in rows
                            if (row.get("Universal Asset Identifier") or "").strip() == uai
                        ),
                        None
                    )
                    row = existing or {column: "" for column in fields}
                    row.update({
                        "Universal Asset Identifier": uai,
                        "Asset Name": asset["asset_title"],
                        "Knowledge System": asset["knowledge_system"],
                        "Asset Type": asset["asset_type"],
                        "Status": asset["proposed_status"],
                        "Owner": asset["owner"],
                        "Parent Assets": "; ".join(asset.get("parent_assets", [])),
                        "Notes": asset.get("notes", "Build 0044 controlled baseline"),
                        "Repository Path": target,
                        "Supporting Files": "; ".join(asset.get("supporting_files", [])),
                        "Version": asset["proposed_version"],
                        "Completion Percentage": str(asset.get("completion_percentage", 0)),
                        "Child Assets": "; ".join(asset.get("child_assets", [])),
                        "Relationship List": json.dumps(
                            asset.get("relationships", []), separators=(",", ":")
                        ),
                        "Evidence Links": "; ".join(asset.get("evidence_links", [])),
                        "Report Links": "; ".join(asset.get("report_links", [])),
                        "Marketplace Links": "; ".join(asset.get("marketplace_links", [])),
                        "Change History": f"{utc_now()} Build 0044 import",
                        "Build Provenance": "CERT-BUILD-0044",
                        "Source Builds": "0041; 0042; 0043; 0044",
                        "Registration Basis": "BUILD_ASSET_INTENT_MANIFEST",
                        "File SHA256": sha256_file(destination),
                        "Last Updated": utc_now()
                    })
                    if not existing:
                        rows.append(row)

                register_errors = validate_register(rows, repository)
                if register_errors:
                    raise RuntimeError("; ".join(register_errors))
                write_register(register_path, fields, rows)
                applied = True
            except Exception as exc:
                errors.append("Transactional apply failed: " + str(exc))
                for action, destination, backup_file in reversed(journal):
                    try:
                        if action == "restore" and backup_file is not None:
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(backup_file, destination)
                        elif action == "delete" and destination.exists():
                            destination.unlink()
                    except Exception as rollback_exc:
                        errors.append("Rollback file failure: " + str(rollback_exc))
                try:
                    register_path.write_bytes(original_register)
                except Exception as rollback_exc:
                    errors.append("Rollback register failure: " + str(rollback_exc))
                applied = False

    transaction_status = (
        "APPLIED_VALIDATED" if args.apply and applied and not errors and not conflicts
        else "APPLY_BLOCKED" if args.apply
        else "DRY_RUN_VALIDATED" if not errors and not conflicts
        else "DRY_RUN_BLOCKED"
    )
    result = {
        "valid": not errors and not conflicts and (applied if args.apply else True),
        "build_number": "0044",
        "mode": "APPLY" if args.apply else "DRY_RUN",
        "transaction_status": transaction_status,
        "applied": applied,
        "canonical_register": "Documentation/Master_Asset_Register.csv",
        "register_rows_before": len(rows) - (len(allocations) if applied else 0),
        "expected_register_rows_after": expected_register_total,
        "allocations": allocations,
        "routing": routing,
        "conflicts": conflicts,
        "errors": errors,
        "backup_path": str(backup_path) if backup_path else None
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
