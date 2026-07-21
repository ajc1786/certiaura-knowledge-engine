from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

BUILD_ID = "CERT-BUILD-0048"
BUILD_NUMBER = "0048"
MANIFEST_PATH = "Documentation/Build_Records/0048/ASSET_INTENT_MANIFEST.json"
REGISTER_PATH = "Documentation/Master_Asset_Register.csv"
ALLOWED_ROOTS = {
    "00_Governance", "01_Knowledge_Systems", "02_Peptides", "03_Biology", "04_Conditions",
    "05_Monitoring", "06_Evidence", "07_Goals", "08_Product_Passports", "09_Cost_Intelligence",
    "10_Marketplace", "11_Academy", "12_Reports", "13_Project_Genesis", "Assets", "Database",
    "Documentation", "Images", "Schemas", "Scripts", "Standards", "Templates",
}
RUNTIME_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache"}
RUNTIME_EXTENSIONS = {".pyc", ".pyo"}
REQUIRED_REGISTER_COLUMNS = [
    "Universal Asset Identifier", "Asset Name", "Knowledge System", "Asset Type", "Status", "Owner",
    "Parent Assets", "Last Review", "Notes", "Repository Path", "Supporting Files", "Version",
    "Completion Percentage", "Child Assets", "Relationship List", "Evidence Links", "Report Links",
    "Marketplace Links", "Next Review", "Change History", "Build Provenance", "Source Builds",
    "Registration Basis", "File SHA256", "Last Updated",
]



def git_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError("repository HEAD could not be resolved")
    return result.stdout.strip()


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def safe_members(zf: zipfile.ZipFile) -> list[str]:
    members: list[str] = []
    lowered: set[str] = set()
    for info in zf.infolist():
        if info.is_dir():
            continue
        name = info.filename.replace("\\", "/")
        p = PurePosixPath(name)
        if p.is_absolute() or ".." in p.parts or not p.parts:
            raise ValueError(f"unsafe archive path: {name}")
        if p.parts[0] not in ALLOWED_ROOTS:
            raise ValueError(f"unauthorised root: {p.parts[0]}")
        if any(part in RUNTIME_NAMES for part in p.parts) or p.suffix.lower() in RUNTIME_EXTENSIONS:
            raise ValueError(f"runtime artefact prohibited: {name}")
        lower = name.lower()
        if lower in lowered:
            raise ValueError(f"case-only or duplicate collision: {name}")
        lowered.add(lower)
        members.append(name)
    return sorted(members)


def read_manifest(stage: Path) -> dict:
    manifest = json.loads((stage / MANIFEST_PATH).read_text(encoding="utf-8"))
    if manifest.get("build_id") != BUILD_ID:
        raise ValueError("Asset Intent Manifest build_id mismatch")
    seen: set[str] = set()
    for item in manifest.get("files", []):
        path = item.get("path")
        if not path or path in seen:
            raise ValueError("Asset Intent Manifest paths must be exact, unique and non-empty")
        seen.add(path)
        if item.get("build_provenance") != BUILD_ID:
            raise ValueError(f"build provenance mismatch for {path}")
    return manifest


def read_register(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise FileNotFoundError(f"canonical Master Asset Register missing: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    missing = [c for c in REQUIRED_REGISTER_COLUMNS if c not in fields]
    if missing:
        raise ValueError(f"Master Asset Register missing required columns: {missing}")
    return fields, rows


def allocate_uai(rows: list[dict[str, str]], system: str) -> str:
    prefix = f"CERT-{system}-"
    maximum = 0
    for row in rows:
        value = row.get("Universal Asset Identifier", "")
        if value.startswith(prefix):
            try:
                maximum = max(maximum, int(value.rsplit("-", 1)[1]))
            except ValueError:
                pass
    return f"{prefix}{maximum + 1:06d}"


def reconcile_register(fields: list[str], rows: list[dict[str, str]], manifest: dict, stage: Path) -> tuple[list[dict[str, str]], list[dict]]:
    by_path = {r.get("Repository Path", ""): r for r in rows if r.get("Repository Path")}
    by_uai = {r.get("Universal Asset Identifier", ""): r for r in rows if r.get("Universal Asset Identifier")}
    changes: list[dict] = []
    for item in manifest.get("files", []):
        if item.get("classification") != "FORMAL_ASSET":
            continue
        rel = item["path"]
        existing = by_path.get(rel)
        action = item.get("intended_action")
        if existing:
            uai = existing["Universal Asset Identifier"]
            if item.get("uai") not in (None, "", "UAI_ALLOCATION_REQUIRED", uai):
                raise ValueError(f"UAI conflict for existing path {rel}")
            if action == "CREATE":
                raise ValueError(f"CREATE formal asset already registered: {rel}")
            row = existing
            change = "UPDATE"
        else:
            if action not in {"CREATE", "UPDATE"}:
                raise ValueError(f"No existing asset for action {action}: {rel}")
            uai = item.get("uai")
            if not uai or uai == "UAI_ALLOCATION_REQUIRED":
                uai = allocate_uai(rows, item["knowledge_system"])
            if uai in by_uai:
                raise ValueError(f"duplicate UAI allocation: {uai}")
            row = {field: "" for field in fields}
            rows.append(row)
            by_path[rel] = row
            by_uai[uai] = row
            change = "CREATE"
        source = stage / rel
        row.update({
            "Universal Asset Identifier": uai,
            "Asset Name": item["asset_title"],
            "Knowledge System": item["knowledge_system"],
            "Asset Type": item["asset_type"],
            "Status": item.get("status", "CONTROLLED_BASELINE"),
            "Owner": item.get("owner", "Certiaura"),
            "Repository Path": rel,
            "Version": item.get("version", "1.0.0"),
            "Completion Percentage": item.get("completion_percentage", "100"),
            "Build Provenance": BUILD_ID,
            "Source Builds": BUILD_NUMBER,
            "Registration Basis": item.get("registration_basis", "BUILD_0048_ASSET_INTENT_MANIFEST_EXACT_PATH"),
            "File SHA256": sha256_file(source),
            "Last Updated": now_z(),
            "Change History": f"{now_z()} {BUILD_ID} {change}",
        })
        changes.append({"path": rel, "uai": uai, "action": change})
    return rows, changes



def classify_file_actions(repo: Path, stage: Path, manifest: dict) -> tuple[list[dict], list[dict]]:
    actions: list[dict] = []
    conflicts: list[dict] = []
    for item in manifest.get("files", []):
        rel = item["path"]
        src = stage / rel
        dest = repo / rel
        incoming_hash = sha256_file(src)
        record = {
            "path": rel,
            "classification": item.get("classification"),
            "intended_action": item.get("intended_action"),
            "incoming_sha256": incoming_hash,
        }
        if not dest.exists():
            record["action"] = "CREATE_FILE"
            actions.append(record)
            continue
        if not dest.is_file():
            record.update({"action": "BLOCKED_PATH_TYPE_COLLISION", "existing_type": "NON_FILE"})
            actions.append(record)
            conflicts.append(record.copy())
            continue
        existing_hash = sha256_file(dest)
        record["existing_sha256"] = existing_hash
        if existing_hash == incoming_hash:
            record["action"] = "UNCHANGED_IDENTICAL"
            actions.append(record)
            continue
        approved = (
            item.get("intended_action") in {"UPDATE", "SUPERSEDE"}
            and item.get("allow_replace", False) is True
        )
        expected_existing = str(item.get("expected_existing_sha256", "")).strip().upper()
        if approved and expected_existing and expected_existing != existing_hash:
            record.update({
                "action": "BLOCKED_PREDECESSOR_HASH_MISMATCH",
                "expected_existing_sha256": expected_existing,
            })
            actions.append(record)
            conflicts.append(record.copy())
            continue
        if approved:
            record["action"] = "APPROVED_REPLACEMENT"
            actions.append(record)
            continue
        record["action"] = "BLOCKED_UNAPPROVED_NON_IDENTICAL_COLLISION"
        actions.append(record)
        conflicts.append(record.copy())
    return actions, conflicts

def write_register(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--backup-root", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    repo = args.repository.resolve()
    package = args.package.resolve()
    report = {
        "build_id": BUILD_ID, "build_number": BUILD_NUMBER, "generated_at": now_z(),
        "package_sha256": sha256_file(package), "applied": False, "valid": False,
        "errors": [], "conflicts": [], "allocated_identifiers": [],
    }
    backup_path: Path | None = None
    try:
        if not (repo / ".git").is_dir():
            raise ValueError("repository must be a Git working tree")
        report["repository_head_before_apply"] = git_head(repo)
        with tempfile.TemporaryDirectory(prefix="certiaura_0048_") as tmp:
            stage = Path(tmp)
            with zipfile.ZipFile(package) as zf:
                members = safe_members(zf)
                zf.extractall(stage)
            manifest = read_manifest(stage)
            declared = sorted(item["path"] for item in manifest["files"])
            if sorted(members) != declared:
                missing = sorted(set(declared) - set(members))
                extra = sorted(set(members) - set(declared))
                raise ValueError(f"archive/manifest mismatch missing={missing} extra={extra}")
            file_actions, file_conflicts = classify_file_actions(repo, stage, manifest)
            report.update({
                "package_file_count": len(members),
                "formal_asset_count": sum(1 for x in manifest["files"] if x["classification"] == "FORMAL_ASSET"),
                "file_actions": file_actions,
                "conflicts": file_conflicts,
            })
            if file_conflicts:
                paths = ", ".join(item["path"] for item in file_conflicts)
                raise ValueError(f"dry-run detected unapproved repository collisions: {paths}")
            fields, rows = read_register(repo / REGISTER_PATH)
            rows_after, register_changes = reconcile_register(fields, rows, manifest, stage)
            report.update({
                "register_changes": register_changes,
                "expected_register_total": len(rows_after),
                "allocated_identifiers": [x["uai"] for x in register_changes if x["action"] == "CREATE"],
                "transaction_status": "DRY_RUN_VALIDATED",
                "valid": True,
            })
            if args.apply:
                if args.backup_root is None:
                    raise ValueError("--backup-root is mandatory for apply")
                backup_root = args.backup_root.resolve()
                try:
                    backup_root.relative_to(repo)
                    raise ValueError("transactional backup root must remain outside the repository")
                except ValueError as exc:
                    if str(exc).startswith("transactional backup root"):
                        raise
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                backup_path = backup_root / f"Build_0048_Pre_Import_{stamp}"
                backup_path.mkdir(parents=True, exist_ok=False)
                changed: list[str] = []
                try:
                    action_by_path = {item["path"]: item for item in file_actions}
                    for item in manifest["files"]:
                        rel = item["path"]
                        src = stage / rel
                        dest = repo / rel
                        file_action = action_by_path[rel]["action"]
                        if file_action == "UNCHANGED_IDENTICAL":
                            continue
                        if file_action == "APPROVED_REPLACEMENT":
                            if not dest.is_file():
                                raise ValueError(f"repository changed after dry-run for approved replacement: {rel}")
                            if sha256_file(dest) != action_by_path[rel]["existing_sha256"]:
                                raise ValueError(f"repository file hash changed after dry-run: {rel}")
                            b = backup_path / "repository_files" / rel
                            b.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(dest, b)
                        elif file_action == "CREATE_FILE":
                            if dest.exists():
                                raise ValueError(f"repository path appeared after dry-run: {rel}")
                        else:
                            raise ValueError(f"unapproved file action reached apply stage: {rel} {file_action}")
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dest)
                        changed.append(rel)
                    register = repo / REGISTER_PATH
                    reg_backup = backup_path / REGISTER_PATH
                    reg_backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(register, reg_backup)
                    write_register(register, fields, rows_after)
                    report.update({"applied": True, "transaction_status": "APPLIED_PENDING_REPOSITORY_VALIDATION", "backup_path": str(backup_path), "changed_paths": changed})
                except Exception:
                    # Restore overwritten files and register. New files are removed.
                    for rel in changed:
                        dest = repo / rel
                        b = backup_path / "repository_files" / rel
                        if b.exists():
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(b, dest)
                        elif dest.exists():
                            dest.unlink()
                    reg_backup = backup_path / REGISTER_PATH
                    if reg_backup.exists():
                        shutil.copy2(reg_backup, repo / REGISTER_PATH)
                    raise
    except Exception as exc:
        report["errors"].append(str(exc))
        report["valid"] = False
        report["transaction_status"] = "FAILED_CLOSED"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
