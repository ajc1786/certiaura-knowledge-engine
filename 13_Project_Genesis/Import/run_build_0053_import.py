from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BUILD_NUMBER = "0053"
EXPECTED_PREDECESSOR_COMMIT = "890df218b4f4dea92f4ccfa36b8106de59eca1b1"
ALLOWED_ROOTS = {
    "00_Governance",
    "01_Knowledge_Systems",
    "02_Peptides",
    "03_Biology",
    "04_Conditions",
    "05_Monitoring",
    "06_Evidence",
    "07_Goals",
    "08_Product_Passports",
    "09_Cost_Intelligence",
    "10_Marketplace",
    "11_Academy",
    "12_Reports",
    "13_Project_Genesis",
    "Assets",
    "Database",
    "Documentation",
    "Images",
    "Schemas",
    "Scripts",
    "Standards",
    "Templates",
}
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CURRENT_MANIFEST = (
    PACKAGE_ROOT / "Documentation/Build_Records/0053/ASSET_INTENT_MANIFEST.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(
    repo: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def normalise(name: str) -> str:
    return name.replace("\\", "/").lstrip("./")


def safe_member(name: str) -> bool:
    value = normalise(name)
    return (
        bool(value)
        and not value.startswith("/")
        and ":" not in value.split("/", 1)[0]
        and ".." not in Path(value).parts
    )


def load_manifest_from_zip(zf: zipfile.ZipFile) -> dict[str, Any]:
    path = "Documentation/Build_Records/0053/ASSET_INTENT_MANIFEST.json"
    return json.loads(zf.read(path).decode("utf-8"))


def validate_package(package: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if not package.is_file():
        return {}, ["package does not exist"]
    with zipfile.ZipFile(package, "r") as zf:
        names = [normalise(x.filename) for x in zf.infolist() if not x.is_dir()]
        if len(names) != len(set(names)):
            errors.append("duplicate ZIP paths")
        if len({name.lower() for name in names}) != len(names):
            errors.append("case-colliding ZIP paths")
        for name in names:
            if not safe_member(name):
                errors.append(f"unsafe ZIP path: {name}")
            root = name.split("/", 1)[0]
            if root not in ALLOWED_ROOTS:
                errors.append(f"unauthorised root: {root}")
        try:
            manifest = load_manifest_from_zip(zf)
        except Exception as exc:
            return {}, errors + [f"manifest load failed: {exc}"]
        declared = sorted(
            normalise(str(item["repository_path"]))
            for item in manifest.get("files", [])
        )
        if sorted(names) != declared:
            missing = sorted(set(declared) - set(names))
            extra = sorted(set(names) - set(declared))
            errors.append(
                f"package/manifest mismatch missing={missing} extra={extra}"
            )
        if manifest.get("build_number") != BUILD_NUMBER:
            errors.append("manifest build number mismatch")
        checksum_name = "Documentation/Build_Records/0053/CHECKSUMS.sha256"
        if checksum_name not in names:
            errors.append("CHECKSUMS.sha256 missing")
        else:
            expected: dict[str, str] = {}
            for line in zf.read(checksum_name).decode("utf-8").splitlines():
                if not line.strip():
                    continue
                digest, path = line.split("  ", 1)
                expected[normalise(path)] = digest.lower()
            for name, digest in expected.items():
                if name == checksum_name:
                    continue
                observed = hashlib.sha256(zf.read(name)).hexdigest()
                if observed != digest:
                    errors.append(f"checksum mismatch: {name}")
    return manifest, errors


def load_predecessor_module():
    path = (
        PACKAGE_ROOT
        / "13_Project_Genesis/Release/derive_build_0052_predecessor_evidence.py"
    )
    spec = importlib.util.spec_from_file_location("build0052_predecessor", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("predecessor evidence module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_column(headers: list[str], candidates: list[str]) -> str | None:
    lookup = {header.strip().lower(): header for header in headers}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    return None


def reconcile_register(
    repo: Path, manifest: dict[str, Any], build_provenance: str
) -> list[dict[str, str]]:
    path = repo / "Documentation/Master_Asset_Register.csv"
    if not path.exists():
        raise RuntimeError("canonical Master Asset Register is missing")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows = list(reader)
    if not headers:
        raise RuntimeError("Master Asset Register has no headers")

    required_new = [
        "Universal Asset Identifier",
        "Repository Path",
        "Asset Title",
        "Asset Type",
        "Knowledge System",
        "Version",
        "Status",
        "Owner",
        "Build Provenance",
    ]
    for header in required_new:
        if not find_column(headers, [header]):
            headers.append(header)

    uai_col = find_column(
        headers, ["Universal Asset Identifier", "UAI", "universal_asset_identifier"]
    )
    path_col = find_column(
        headers, ["Repository Path", "Canonical Path", "Path", "repository_path"]
    )
    if not uai_col or not path_col:
        raise RuntimeError("Master Asset Register UAI/path columns cannot be resolved")

    used = {
        str(row.get(uai_col, "")).strip()
        for row in rows
        if str(row.get(uai_col, "")).strip()
    }
    by_path = {
        normalise(str(row.get(path_col, ""))).lower(): row
        for row in rows
        if str(row.get(path_col, "")).strip()
    }
    changes: list[dict[str, str]] = []
    formal = [
        item
        for item in manifest.get("files", []) + manifest.get("generated_files", [])
        if item.get("classification") == "FORMAL_ASSET"
    ]

    for item in formal:
        rel = normalise(str(item["repository_path"]))
        action = str(item.get("intended_action", "CREATE"))
        existing = by_path.get(rel.lower())
        if action == "UPDATE":
            if existing is None:
                raise RuntimeError(
                    f"formal UPDATE asset absent from Master Asset Register: {rel}"
                )
            uai = str(existing.get(uai_col, "")).strip()
            if not uai:
                raise RuntimeError(f"formal UPDATE asset has blank UAI: {rel}")
            existing[find_column(headers, ["Version"]) or "Version"] = str(
                item.get("version", "1.0.0")
            )
            existing[find_column(headers, ["Status"]) or "Status"] = str(
                item.get("status", "ACTIVE")
            )
            existing[
                find_column(headers, ["Build Provenance"]) or "Build Provenance"
            ] = build_provenance
            changes.append(
                {"repository_path": rel, "action": "UPDATE", "uai": uai}
            )
        elif action == "CREATE":
            if existing is not None:
                raise RuntimeError(f"formal CREATE path already registered: {rel}")
            system = str(item.get("knowledge_system", "SYS"))
            prefix = f"CERT-{system}-"
            numbers: list[int] = []
            for uai in used:
                if uai.startswith(prefix):
                    try:
                        numbers.append(int(uai.split("-")[-1]))
                    except ValueError:
                        pass
            number = max(numbers, default=0) + 1
            uai = f"{prefix}{number:06d}"
            while uai in used:
                number += 1
                uai = f"{prefix}{number:06d}"
            used.add(uai)
            row = {header: "" for header in headers}
            row[uai_col] = uai
            row[path_col] = rel
            row[find_column(headers, ["Asset Title"]) or "Asset Title"] = str(
                item.get("asset_title", Path(rel).stem)
            )
            row[find_column(headers, ["Asset Type"]) or "Asset Type"] = str(
                item.get("asset_type", "Controlled Standard")
            )
            row[
                find_column(headers, ["Knowledge System"]) or "Knowledge System"
            ] = system
            row[find_column(headers, ["Version"]) or "Version"] = str(
                item.get("version", "1.0.0")
            )
            row[find_column(headers, ["Status"]) or "Status"] = str(
                item.get("status", "ACTIVE")
            )
            row[find_column(headers, ["Owner"]) or "Owner"] = str(
                item.get("owner", "Certiaura Governance")
            )
            row[
                find_column(headers, ["Build Provenance"]) or "Build Provenance"
            ] = build_provenance
            rows.append(row)
            by_path[rel.lower()] = row
            changes.append(
                {"repository_path": rel, "action": "CREATE", "uai": uai}
            )

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=headers, lineterminator="\n", extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)
    return changes


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def run_import(
    package_path: str | Path,
    repository: str | Path,
    backup_root: str | Path,
    report_path: str | Path,
    apply: bool,
    force_failure_after_apply: bool = False,
    expected_predecessor_commit: str = EXPECTED_PREDECESSOR_COMMIT,
    require_exact_head: bool = True,
) -> dict[str, Any]:
    package = Path(package_path).resolve()
    repo = Path(repository).resolve()
    backup_root_path = Path(backup_root).resolve()
    report = Path(report_path).resolve()

    manifest, package_errors = validate_package(package)
    if package_errors:
        raise RuntimeError(
            "package validation failed: " + "; ".join(package_errors)
        )
    if not (repo / ".git").exists():
        raise RuntimeError("repository is not a Git working tree")
    if git(repo, "status", "--porcelain").stdout.strip():
        raise RuntimeError("repository must be clean before Build 0053 import")

    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if require_exact_head and head != expected_predecessor_commit:
        raise RuntimeError(
            f"repository HEAD {head} does not equal required predecessor "
            f"{expected_predecessor_commit}"
        )

    predecessor_module = load_predecessor_module()
    predecessor_evidence = predecessor_module.derive(
        repo,
        CURRENT_MANIFEST,
        expected_commit=expected_predecessor_commit,
        expected_count=59,
    )

    package_paths = [
        normalise(str(item["repository_path"]))
        for item in manifest.get("files", [])
    ]
    generated_paths = [
        normalise(str(item["repository_path"]))
        for item in manifest.get("generated_files", [])
    ]
    owned = sorted(set(package_paths) | set(generated_paths))

    preflight = {
        "build_number": BUILD_NUMBER,
        "package_sha256": sha256_file(package),
        "repository_head": head,
        "predecessor_result": predecessor_evidence.get("result"),
        "predecessor_path_count": predecessor_evidence.get(
            "predecessor_path_count"
        ),
        "approved_predecessor_intersection": predecessor_evidence.get(
            "approved_intersection", []
        ),
        "owned_path_count": len(owned),
        "apply_requested": apply,
        "errors": [],
        "result": "DRY_RUN_VALIDATED",
    }
    if not apply:
        write_json(report, preflight)
        return preflight

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    backup = backup_root_path / f"Build_0053_Pre_Import_{timestamp}"
    backup.mkdir(parents=True, exist_ok=False)

    existed: dict[str, bool] = {}
    applied_hash: dict[str, str] = {}
    for rel in owned:
        target = repo / rel
        existed[rel] = target.exists()
        if target.exists():
            destination = backup / "files" / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, destination)
    write_json(
        backup / "TRANSACTION_METADATA.json",
        {
            "build_number": BUILD_NUMBER,
            "predecessor_head": head,
            "owned_paths": owned,
            "existed": existed,
        },
    )

    created: list[str] = []
    predecessor_rel = (
        "Documentation/Build_Records/0053/PREDECESSOR_CANONICAL_EVIDENCE.json"
    )
    register_report_rel = (
        "Documentation/Build_Records/0053/ASSET_REGISTER_CHANGE_REPORT.json"
    )
    import_report_rel = (
        "Documentation/Build_Records/0053/CANONICAL_IMPORT_REPORT.json"
    )
    validation_report_rel = (
        "Documentation/Build_Records/0053/POST_IMPORT_REPOSITORY_VALIDATION.json"
    )

    try:
        with zipfile.ZipFile(package, "r") as zf:
            for rel in package_paths:
                target = repo / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                data = zf.read(rel)
                target.write_bytes(data)
                applied_hash[rel] = hashlib.sha256(data).hexdigest()
                if not existed[rel]:
                    created.append(rel)

        write_json(repo / predecessor_rel, predecessor_evidence)
        applied_hash[predecessor_rel] = sha256_file(repo / predecessor_rel)
        if not existed.get(predecessor_rel, False):
            created.append(predecessor_rel)

        updater = repo / "Scripts/update_certiaura_build_0053_controls.py"
        update_result = subprocess.run(
            [sys.executable, "-B", str(updater), str(repo)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if update_result.returncode != 0:
            raise RuntimeError(
                "governance update failed: " + update_result.stderr.strip()
            )

        register_changes = reconcile_register(
            repo, manifest, f"Build {BUILD_NUMBER}"
        )
        write_json(
            repo / register_report_rel,
            {
                "build_number": BUILD_NUMBER,
                "canonical_register": "Documentation/Master_Asset_Register.csv",
                "changes": register_changes,
                "result": "ASSET_REGISTER_RECONCILED",
            },
        )
        applied_hash[register_report_rel] = sha256_file(repo / register_report_rel)
        if not existed.get(register_report_rel, False):
            created.append(register_report_rel)

        preliminary = {
            **preflight,
            "apply_requested": True,
            "applied": True,
            "backup_path": str(backup),
            "register_changes": register_changes,
            "created_paths": sorted(set(created)),
            "result": "APPLIED_PENDING_REPOSITORY_VALIDATION",
        }
        write_json(repo / import_report_rel, preliminary)
        applied_hash[import_report_rel] = sha256_file(repo / import_report_rel)
        if not existed.get(import_report_rel, False):
            created.append(import_report_rel)

        repository_validator = (
            repo
            / "13_Project_Genesis/Validators/validate_build_0053_repository.py"
        )
        validation_result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(repository_validator),
                str(repo),
                "--report",
                str(repo / validation_report_rel),
                "--expected-predecessor-commit",
                expected_predecessor_commit,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if validation_result.returncode != 0:
            if (repo / validation_report_rel).exists():
                applied_hash[validation_report_rel] = sha256_file(
                    repo / validation_report_rel
                )
                if not existed.get(validation_report_rel, False):
                    created.append(validation_report_rel)
            raise RuntimeError(
                "post-import repository validation failed: "
                + validation_result.stdout
                + validation_result.stderr
            )
        applied_hash[validation_report_rel] = sha256_file(
            repo / validation_report_rel
        )
        if not existed.get(validation_report_rel, False):
            created.append(validation_report_rel)

        for rel in generated_paths:
            target = repo / rel
            if not target.exists():
                raise RuntimeError(
                    f"generated owned path missing after update: {rel}"
                )
            applied_hash[rel] = sha256_file(target)
            if not existed.get(rel, False):
                created.append(rel)

        if force_failure_after_apply:
            raise RuntimeError("FORCED_POST_APPLY_FAILURE")

        result = {
            **preflight,
            "apply_requested": True,
            "applied": True,
            "backup_path": str(backup),
            "register_changes": register_changes,
            "created_paths": sorted(set(created)),
            "repository_validation": "PASS",
            "result": "CLEAN_REAPPLY_VALIDATED",
        }
        write_json(repo / import_report_rel, result)
        applied_hash[import_report_rel] = sha256_file(repo / import_report_rel)
        write_json(report, result)
        return result

    except Exception as exc:
        rollback_errors: list[str] = []
        for rel in reversed(owned):
            target = repo / rel
            source = backup / "files" / rel
            try:
                if existed.get(rel):
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
                elif target.exists():
                    current_hash = sha256_file(target)
                    expected_hash = applied_hash.get(rel)
                    if expected_hash is None or current_hash == expected_hash:
                        target.unlink()
                    else:
                        rollback_errors.append(
                            "created path changed after apply and was preserved: " + rel
                        )
            except Exception as rollback_exc:
                rollback_errors.append(f"{rel}: {rollback_exc}")

        dirty = git(repo, "status", "--porcelain").stdout.strip()
        if dirty:
            rollback_errors.append(
                "repository not clean after rollback: " + dirty.replace("\n", " | ")
            )

        failure = {
            **preflight,
            "apply_requested": True,
            "applied": False,
            "backup_path": str(backup),
            "error": str(exc),
            "rollback_errors": rollback_errors,
            "result": "ROLLBACK_STATE_EXACT"
            if not rollback_errors
            else "ROLLBACK_FAILED",
        }
        write_json(report, failure)
        if (
            force_failure_after_apply
            and str(exc) == "FORCED_POST_APPLY_FAILURE"
            and not rollback_errors
        ):
            return failure
        raise RuntimeError(json.dumps(failure, indent=2))



def rollback_from_backup(
    repository: str | Path,
    backup_path: str | Path,
    report_path: str | Path,
) -> dict[str, Any]:
    repo = Path(repository).resolve()
    backup = Path(backup_path).resolve()
    report = Path(report_path).resolve()
    metadata_path = backup / "TRANSACTION_METADATA.json"
    if not (repo / ".git").exists():
        raise RuntimeError("repository is not a Git working tree")
    if not metadata_path.is_file():
        raise RuntimeError(f"transaction metadata missing: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if str(metadata.get("build_number")) != BUILD_NUMBER:
        raise RuntimeError("transaction metadata does not belong to Build 0053")
    expected_head = str(metadata.get("predecessor_head", "")).strip()
    observed_head = git(repo, "rev-parse", "HEAD").stdout.strip()
    if observed_head != expected_head:
        raise RuntimeError(
            f"rollback HEAD mismatch expected={expected_head} observed={observed_head}"
        )
    owned = sorted(
        {normalise(str(value)) for value in metadata.get("owned_paths", [])}
    )
    existed = {
        normalise(str(key)): bool(value)
        for key, value in dict(metadata.get("existed", {})).items()
    }
    if not owned or set(owned) != set(existed):
        raise RuntimeError("transaction ownership metadata is incomplete")

    changed: set[str] = set()
    for args in (
        ("diff", "--name-only"),
        ("diff", "--cached", "--name-only"),
        ("ls-files", "--others", "--exclude-standard"),
    ):
        output = git(repo, *args).stdout
        changed.update(
            normalise(line.strip())
            for line in output.splitlines()
            if line.strip()
        )
    unexpected = sorted(changed - set(owned))
    if unexpected:
        raise RuntimeError(
            "rollback blocked by changes outside Build 0053 ownership: "
            + "; ".join(unexpected)
        )

    for rel in owned:
        target = repo / rel
        if existed[rel]:
            source = backup / "files" / rel
            if not source.is_file():
                raise RuntimeError(f"backup file missing: {source}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        elif target.exists():
            if not target.is_file():
                raise RuntimeError(f"rollback target is not a file: {target}")
            target.unlink()

    git(repo, "reset", "--mixed", "HEAD")
    dirty = git(repo, "status", "--porcelain", "--untracked-files=all").stdout.strip()
    final_head = git(repo, "rev-parse", "HEAD").stdout.strip()
    errors: list[str] = []
    if final_head != expected_head:
        errors.append("repository HEAD changed during rollback")
    if dirty:
        errors.append("repository not clean after rollback: " + dirty.replace("\n", " | "))
    result = {
        "build_number": BUILD_NUMBER,
        "backup_path": str(backup),
        "repository_head": final_head,
        "owned_path_count": len(owned),
        "errors": errors,
        "result": "ROLLBACK_STATE_EXACT" if not errors else "ROLLBACK_FAILED",
    }
    write_json(report, result)
    if errors:
        raise RuntimeError(json.dumps(result, indent=2))
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--backup-root", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force-failure-after-apply", action="store_true")
    parser.add_argument("--rollback-backup")
    args = parser.parse_args()
    try:
        if args.rollback_backup:
            result = rollback_from_backup(
                args.repository,
                args.rollback_backup,
                args.report,
            )
        else:
            result = run_import(
                args.package,
                args.repository,
                args.backup_root,
                args.report,
                args.apply,
                args.force_failure_after_apply,
            )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
