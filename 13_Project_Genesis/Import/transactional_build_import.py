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
from typing import Any

ALLOWED_ROOTS = {
    "00_Governance", "01_Knowledge_Systems", "02_Peptides", "03_Biology",
    "04_Conditions", "05_Monitoring", "06_Evidence", "07_Goals",
    "08_Product_Passports", "09_Cost_Intelligence", "10_Marketplace",
    "11_Academy", "12_Reports", "13_Project_Genesis", "Assets", "Database",
    "Documentation", "Images", "Schemas", "Scripts", "Standards", "Templates",
}
REGISTER_UAI = "Universal Asset Identifier"
REGISTER_PATH = "Repository Path"
BUILD_MANIFEST_RE = re.compile(r"^Documentation/Build_Records/(\d{4}[A-Za-z]?)/BUILD_MANIFEST\.json$")
WRAPPER_RE = re.compile(r"^(?:Certiaura[_ -]?Build|Build)[_ -]?\d+[A-Za-z]?(?:[_ -].*)?$", re.I)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def norm_rel(path: str) -> str:
    candidate = PurePosixPath(path.replace("\\", "/"))
    if candidate.is_absolute() or not candidate.parts or ".." in candidate.parts:
        raise ValueError(f"Unsafe repository-relative path: {path}")
    return candidate.as_posix()


def safe_repo_path(repo: Path, rel: str) -> Path:
    normalised = norm_rel(rel)
    target = (repo / Path(*PurePosixPath(normalised).parts)).resolve()
    base = repo.resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"Path escapes repository: {rel}") from exc
    return target


def read_json_member(zf: zipfile.ZipFile, member: str) -> dict[str, Any]:
    try:
        value = json.loads(zf.read(member).decode("utf-8"))
    except KeyError as exc:
        raise ValueError(f"Required package member missing: {member}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON member {member}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {member}")
    return value


def inspect_package(zf: zipfile.ZipFile) -> tuple[list[str], list[str], list[str], bool, list[list[str]]]:
    names: list[str] = []
    lowered: dict[str, str] = {}
    collisions: list[list[str]] = []
    for info in zf.infolist():
        if info.is_dir():
            continue
        name = norm_rel(info.filename)
        names.append(name)
        key = name.casefold()
        if key in lowered and lowered[key] != name:
            collisions.append([lowered[key], name])
        lowered[key] = name
    if len(names) != len(set(names)):
        raise ValueError("Duplicate package paths detected")
    roots = sorted({PurePosixPath(name).parts[0] for name in names})
    unauthorised = sorted(set(roots) - ALLOWED_ROOTS)
    wrapper = bool(len(roots) == 1 and WRAPPER_RE.match(roots[0]))
    return names, roots, unauthorised, wrapper, collisions


def discover_build_metadata(zf: zipfile.ZipFile, names: list[str]) -> dict[str, Any]:
    manifest_paths = [name for name in names if BUILD_MANIFEST_RE.match(name)]
    if len(manifest_paths) != 1:
        raise ValueError(f"Expected exactly one BUILD_MANIFEST.json; found {len(manifest_paths)}")
    manifest_path = manifest_paths[0]
    match = BUILD_MANIFEST_RE.match(manifest_path)
    assert match is not None
    path_build = match.group(1)
    manifest = read_json_member(zf, manifest_path)
    build_number = str(manifest.get("build_number", "")).strip()
    if build_number != path_build:
        raise ValueError(f"Build number mismatch: path={path_build}, manifest={build_number}")
    build_title = str(manifest.get("build_title", "")).strip()
    package_version = str(manifest.get("package_version", "")).strip()
    if not build_title or not package_version:
        raise ValueError("Build manifest must declare build_title and package_version")
    record_root = f"Documentation/Build_Records/{build_number}"
    asset_manifest_path = f"{record_root}/ASSET_INTENT_MANIFEST.json"
    routing_manifest_path = f"{record_root}/ROUTING_MANIFEST.json"
    intent = read_json_member(zf, asset_manifest_path)
    routing = read_json_member(zf, routing_manifest_path)
    if str(intent.get("build_number", build_number)) != build_number:
        raise ValueError("Asset Intent Manifest build number mismatch")
    if str(routing.get("build_number", build_number)) != build_number:
        raise ValueError("Routing Manifest build number mismatch")
    return {
        "build_number": build_number,
        "build_title": build_title,
        "package_version": package_version,
        "record_root": record_root,
        "manifest_path": manifest_path,
        "asset_manifest_path": asset_manifest_path,
        "routing_manifest_path": routing_manifest_path,
        "manifest": manifest,
        "intent": intent,
        "routing": routing,
    }


def read_register(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise ValueError(f"Master Asset Register missing: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []
    if REGISTER_UAI not in fields or REGISTER_PATH not in fields:
        raise ValueError("Master Asset Register missing required columns")
    uais = [row.get(REGISTER_UAI, "").strip() for row in rows if row.get(REGISTER_UAI, "").strip()]
    paths = [row.get(REGISTER_PATH, "").strip().replace("\\", "/") for row in rows if row.get(REGISTER_PATH, "").strip()]
    if len(uais) != len(set(uais)):
        raise ValueError("Master Asset Register contains duplicate Universal Asset Identifiers")
    folded = [path.casefold() for path in paths]
    if len(folded) != len(set(folded)):
        raise ValueError("Master Asset Register contains duplicate repository paths")
    return fields, rows


def write_register(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def next_uai(rows: list[dict[str, str]], knowledge_system: str) -> str:
    system = knowledge_system.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{2,6}", system):
        raise ValueError(f"Invalid Knowledge System for UAI allocation: {knowledge_system}")
    pattern = re.compile(rf"^CERT-{re.escape(system)}-(\d{{6}})$")
    used = {row.get(REGISTER_UAI, "").strip() for row in rows}
    highest = 0
    for value in used:
        match = pattern.match(value)
        if match:
            highest = max(highest, int(match.group(1)))
    candidate = highest + 1
    while f"CERT-{system}-{candidate:06d}" in used:
        candidate += 1
    return f"CERT-{system}-{candidate:06d}"


def asset_path(asset: dict[str, Any]) -> str:
    value = asset.get("repository_path") or asset.get("path")
    if not value:
        raise ValueError("Formal asset is missing repository path")
    return norm_rel(str(value))


def requested_uai(asset: dict[str, Any]) -> str:
    for key in ("existing_uai", "proposed_uai", "universal_asset_identifier"):
        value = str(asset.get(key, "")).strip()
        if value:
            return value
    return ""


def reconcile_register(
    fields: list[str],
    rows: list[dict[str, str]],
    formal_assets: list[dict[str, Any]],
    build_number: str,
) -> tuple[list[dict[str, str]], list[dict[str, Any]], list[dict[str, str]]]:
    by_uai = {row.get(REGISTER_UAI, "").strip(): row for row in rows if row.get(REGISTER_UAI, "").strip()}
    by_path = {
        row.get(REGISTER_PATH, "").strip().replace("\\", "/").casefold(): row
        for row in rows
        if row.get(REGISTER_PATH, "").strip()
    }
    changes: list[dict[str, Any]] = []
    allocations: list[dict[str, str]] = []
    for asset in formal_assets:
        rel = asset_path(asset)
        action = str(asset.get("intended_action", "")).strip().upper()
        knowledge_system = str(asset.get("knowledge_system", "SYS")).strip().upper()
        uai = requested_uai(asset)
        if action == "CREATE" and uai in {"", "UAI_ALLOCATION_REQUIRED", "AUTO_ALLOCATE"}:
            uai = next_uai(rows, knowledge_system)
            allocations.append({"path": rel, "allocated_uai": uai})
        target = by_uai.get(uai) if uai else None
        target = target or by_path.get(rel.casefold())
        if action == "CREATE":
            if target is not None:
                raise ValueError(f"CREATE formal asset conflicts with existing identity: {rel} / {uai}")
            target = {field: "" for field in fields}
            rows.append(target)
        elif action == "UPDATE":
            if target is None:
                raise ValueError(f"UPDATE formal asset not found: {rel} / {uai}")
            existing_uai = target.get(REGISTER_UAI, "").strip()
            if existing_uai and uai and existing_uai != uai:
                raise ValueError(f"UPDATE attempted to change UAI: {existing_uai} -> {uai}")
            uai = existing_uai or uai
        elif action in {"NO_CHANGE", "SUPERSEDE", "RETIRE"}:
            if target is None:
                raise ValueError(f"{action} formal asset not found: {rel} / {uai}")
            uai = target.get(REGISTER_UAI, "").strip() or uai
        else:
            raise ValueError(f"Unsupported formal asset intended_action: {action}")
        if not uai:
            raise ValueError(f"Formal asset has no resolved UAI: {rel}")
        mapping = {
            "Universal Asset Identifier": uai,
            "Asset Name": str(asset.get("asset_title", asset.get("title", ""))),
            "Knowledge System": knowledge_system,
            "Asset Type": str(asset.get("asset_type", "")),
            "Status": str(asset.get("proposed_status", "ACTIVE")),
            "Owner": str(asset.get("owner", "Certiaura")),
            "Repository Path": rel,
            "Version": str(asset.get("proposed_version", "")),
            "Completion Percentage": str(asset.get("completion_percentage", 100)),
            "Last Review": str(asset.get("last_review", "")),
            "Next Review": str(asset.get("next_review", "")),
            "Build Provenance": f"CERT-BUILD-{build_number}",
            "Source Builds": str(asset.get("source_builds", build_number)),
            "Registration Basis": str(asset.get("registration_basis", "BUILD_IMPORT")),
        }
        for key, value in mapping.items():
            if key in fields:
                target[key] = value
        by_uai[uai] = target
        by_path[rel.casefold()] = target
        changes.append({"path": rel, "uai": uai, "action": action})
    return rows, changes, allocations


def ensure_parent(target: Path, repo: Path, created_dirs: list[str]) -> None:
    missing: list[Path] = []
    current = target.parent
    while current != repo and not current.exists():
        missing.append(current)
        current = current.parent
    for directory in reversed(missing):
        directory.mkdir()
        created_dirs.append(directory.relative_to(repo).as_posix())


def safe_remove_empty_directories(repo: Path, created_directories: list[str], actions: list[dict[str, Any]]) -> None:
    unique = sorted(set(created_directories), key=lambda value: len(PurePosixPath(value).parts), reverse=True)
    for rel in unique:
        directory = safe_repo_path(repo, rel)
        if not directory.exists():
            actions.append({"path": rel, "action": "DIRECTORY_ALREADY_ABSENT"})
            continue
        if not directory.is_dir():
            actions.append({"path": rel, "action": "SKIP_DIRECTORY_NOT_DIRECTORY"})
            continue
        if next(directory.iterdir(), None) is not None:
            actions.append({"path": rel, "action": "PRESERVE_NONEMPTY_DIRECTORY"})
            continue
        directory.rmdir()
        actions.append({"path": rel, "action": "REMOVE_EMPTY_TRANSACTION_DIRECTORY"})


def recover_transaction(repo: Path, journal: dict[str, Any], apply: bool = True) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    backup = Path(journal["backup_root"])
    for item in reversed(journal.get("created_files", [])):
        rel = item["path"]
        target = safe_repo_path(repo, rel)
        if not target.exists():
            actions.append({"path": rel, "action": "FILE_ALREADY_ABSENT"})
            continue
        current = sha256_file(target)
        expected = item.get("applied_sha256")
        if expected and current != expected:
            actions.append({"path": rel, "action": "PRESERVE_CHANGED_CREATED_FILE", "current_sha256": current})
            continue
        if apply:
            target.unlink()
        actions.append({"path": rel, "action": "REMOVE_TRANSACTION_CREATED_FILE" if apply else "WOULD_REMOVE_TRANSACTION_CREATED_FILE"})
    for item in journal.get("replaced_files", []):
        rel = item["path"]
        source = backup / item["backup_rel"]
        target = safe_repo_path(repo, rel)
        if not source.is_file():
            actions.append({"path": rel, "action": "RESTORE_FAILED", "reason": "backup_missing"})
            continue
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        actions.append({"path": rel, "action": "RESTORE_REPLACED_FILE" if apply else "WOULD_RESTORE_REPLACED_FILE"})
    if apply:
        safe_remove_empty_directories(repo, journal.get("created_directories", []), actions)
    return {
        "valid": True,
        "applied": apply,
        "actions": actions,
        "recursive_directory_deletion_used": False,
    }


def write_json_report(repo: Path, report_arg: str | None, default_rel: str, data: dict[str, Any]) -> Path:
    report = Path(report_arg) if report_arg else safe_repo_path(repo, default_rel)
    if not report.is_absolute():
        report = safe_repo_path(repo, report.as_posix())
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return report


def external_backup_root(repo: Path, build_number: str) -> Path:
    explicit = os.environ.get("CERTIAURA_BACKUP_ROOT", "").strip()
    if explicit:
        parent = Path(explicit).expanduser().resolve()
    else:
        parents = list(repo.resolve().parents)
        certiaura_root = parents[1] if len(parents) > 1 else repo.parent
        parent = certiaura_root / "Backups"
    parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    root = parent / f"Build_{build_number}_Pre_Import_{stamp}"
    root.mkdir(parents=True, exist_ok=False)
    return root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Certiaura build-neutral transactional build importer")
    parser.add_argument("zip_path")
    parser.add_argument("repository_path")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--asset-register", default="Documentation/Master_Asset_Register.csv")
    parser.add_argument("--report")
    args = parser.parse_args(argv)

    repo = Path(args.repository_path).resolve()
    zip_path = Path(args.zip_path).resolve()
    report: dict[str, Any] = {
        "schema_version": "3.0.0",
        "generated_at": utc_now(),
        "zip_path": str(zip_path),
        "repository_path": str(repo),
        "apply_requested": args.apply,
    }
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    default_report = "Documentation/Build_Records/UNKNOWN/GUIDED_DRY_RUN_REPORT.json"
    try:
        if not repo.is_dir():
            raise ValueError("Repository path is not a directory")
        if not zip_path.is_file():
            raise ValueError("Build ZIP does not exist")
        register_path = safe_repo_path(repo, args.asset_register)
        fields, rows = read_register(register_path)
        with zipfile.ZipFile(zip_path) as zf:
            names, roots, unauthorised, wrapper, case_collisions = inspect_package(zf)
            metadata = discover_build_metadata(zf, names)
            build_number = metadata["build_number"]
            record_root = metadata["record_root"]
            default_report = f"{record_root}/{'GUIDED_IMPORT_REPORT.json' if args.apply else 'GUIDED_DRY_RUN_REPORT.json'}"
            report.update({
                "build_number": build_number,
                "build_title": metadata["build_title"],
                "package_version": metadata["package_version"],
                "build_manifest_path": metadata["manifest_path"],
                "asset_manifest_path": metadata["asset_manifest_path"],
                "routing_manifest_path": metadata["routing_manifest_path"],
            })
            intent_files = metadata["intent"].get("files", [])
            routing_files = metadata["routing"].get("files", [])
            declared = {norm_rel(str(item.get("path") or item.get("repository_path"))): item for item in intent_files}
            routed = {norm_rel(str(item.get("path") or item.get("destination"))): item for item in routing_files}
            unclassified = sorted(set(names) - set(declared))
            missing_declared = sorted(set(declared) - set(names))
            missing_routed = sorted(set(names) - set(routed))
            if unauthorised:
                errors.append({"code": "UNAUTHORISED_ROOTS", "roots": unauthorised})
            if wrapper:
                errors.append({"code": "WRAPPER_FOLDER_DETECTED"})
            if case_collisions:
                errors.append({"code": "CASE_COLLISIONS", "paths": case_collisions})
            if unclassified:
                errors.append({"code": "UNCLASSIFIED_PACKAGE_FILES", "paths": unclassified})
            if missing_declared:
                errors.append({"code": "DECLARED_FILES_MISSING", "paths": missing_declared})
            if missing_routed:
                errors.append({"code": "UNROUTED_PACKAGE_FILES", "paths": missing_routed})

            approved_replacements = {
                path for path, item in routed.items()
                if str(item.get("action", "")).upper() in {"REPLACE_FILE", "APPROVED_REPLACEMENT"}
            }
            file_actions: list[dict[str, Any]] = []
            conflicts: list[str] = []
            for name in names:
                incoming = zf.read(name)
                target = safe_repo_path(repo, name)
                incoming_hash = sha256_bytes(incoming)
                if not target.exists():
                    action = "CREATE_FILE"
                elif target.is_dir():
                    action = "REJECT_PATH_IS_DIRECTORY"
                    conflicts.append(name)
                else:
                    current_hash = sha256_file(target)
                    if current_hash == incoming_hash:
                        action = "SKIP_IDENTICAL"
                    elif name in approved_replacements:
                        action = "APPROVED_REPLACEMENT"
                    else:
                        action = "BLOCK_NONIDENTICAL_EXISTING"
                        conflicts.append(name)
                file_actions.append({
                    "path": name,
                    "classification": declared.get(name, {}).get("classification"),
                    "action": action,
                    "incoming_sha256": incoming_hash,
                })

            formal_assets = [dict(item) for item in intent_files if item.get("classification") == "FORMAL_ASSET"]
            proposed_rows, register_changes, allocations = reconcile_register(
                fields, [dict(row) for row in rows], formal_assets, build_number
            )
            report.update({
                "package_file_count": len(names),
                "formal_asset_count": len(formal_assets),
                "roots": roots,
                "wrapper_folder_detected": wrapper,
                "unauthorised_roots": unauthorised,
                "case_collisions": case_collisions,
                "file_actions": file_actions,
                "assets_to_create": [item for item in register_changes if item["action"] == "CREATE"],
                "assets_to_update": [item for item in register_changes if item["action"] == "UPDATE"],
                "allocated_identifiers": allocations,
                "expected_register_total": len(proposed_rows),
                "conflicts": conflicts,
            })
            if conflicts:
                errors.append({"code": "UNRESOLVED_FILE_CONFLICTS", "paths": conflicts})
            report["errors"] = errors
            report["warnings"] = warnings
            report["valid"] = not errors
            report["apply_allowed"] = not errors
            report["applied"] = False

            if args.apply and not errors:
                backup = external_backup_root(repo, build_number)
                journal: dict[str, Any] = {
                    "schema_version": "2.0.0",
                    "build_number": build_number,
                    "build_title": metadata["build_title"],
                    "package_version": metadata["package_version"],
                    "repository_path": str(repo),
                    "backup_root": str(backup),
                    "created_files": [],
                    "replaced_files": [],
                    "created_directories": [],
                    "created_at": utc_now(),
                }
                register_backup = backup / args.asset_register
                register_backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(register_path, register_backup)
                journal["replaced_files"].append({"path": args.asset_register, "backup_rel": args.asset_register})
                try:
                    for item in file_actions:
                        if item["action"] == "SKIP_IDENTICAL":
                            continue
                        rel = item["path"]
                        target = safe_repo_path(repo, rel)
                        ensure_parent(target, repo, journal["created_directories"])
                        if target.exists():
                            backup_file = backup / "files" / Path(*PurePosixPath(rel).parts)
                            backup_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(target, backup_file)
                            journal["replaced_files"].append({
                                "path": rel,
                                "backup_rel": backup_file.relative_to(backup).as_posix(),
                            })
                        else:
                            journal["created_files"].append({"path": rel, "applied_sha256": item["incoming_sha256"]})
                        target.write_bytes(zf.read(rel))
                    write_register(register_path, fields, proposed_rows)
                    for item in file_actions:
                        target = safe_repo_path(repo, item["path"])
                        if not target.is_file() or sha256_file(target) != item["incoming_sha256"]:
                            raise RuntimeError(f"Post-apply hash validation failed: {item['path']}")
                    _, validated_rows = read_register(register_path)
                    if len(validated_rows) != len(proposed_rows):
                        raise RuntimeError("Post-apply Master Asset Register row count mismatch")
                    journal_path = backup / "TRANSACTION_JOURNAL.json"
                    journal_path.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8", newline="\n")
                    report.update({
                        "applied": True,
                        "transaction_status": "APPLIED_VALIDATED",
                        "backup_root": str(backup),
                        "transaction_journal": str(journal_path),
                        "recovery_safety": {
                            "recursive_directory_deletion_used": False,
                            "empty_only_directory_cleanup": True,
                            "transaction_created_directories_only": True,
                        },
                    })
                except Exception as exc:
                    journal_path = backup / "TRANSACTION_JOURNAL.json"
                    journal_path.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8", newline="\n")
                    recovery = recover_transaction(repo, journal, apply=True)
                    report.update({
                        "applied": False,
                        "transaction_status": "FAILED_ROLLED_BACK",
                        "apply_error": str(exc),
                        "backup_root": str(backup),
                        "transaction_journal": str(journal_path),
                        "recovery": recovery,
                        "valid": False,
                    })
                    report["errors"].append({"code": "APPLY_FAILED_ROLLED_BACK", "message": str(exc)})
    except Exception as exc:
        report.update({"valid": False, "apply_allowed": False, "applied": False})
        report.setdefault("errors", []).append({"code": "IMPORTER_EXCEPTION", "message": str(exc)})

    output_path = write_json_report(repo, args.report, default_report, report)
    report["report_path"] = str(output_path)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
