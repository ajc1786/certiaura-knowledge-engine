from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

ALLOWED_ROOTS = {
    "00_Governance", "01_Knowledge_Systems", "02_Peptides", "03_Biology",
    "04_Conditions", "05_Monitoring", "06_Evidence", "07_Goals",
    "08_Product_Passports", "09_Cost_Intelligence", "10_Marketplace",
    "11_Academy", "12_Reports", "13_Project_Genesis", "Assets", "Database",
    "Documentation", "Images", "Schemas", "Scripts", "Standards", "Templates",
}
TEXT_SUFFIXES = {
    ".md", ".json", ".csv", ".py", ".ps1", ".cmd", ".txt", ".yml",
    ".yaml", ".toml", ".ini", ".cfg", ".xml", ".html", ".css", ".js",
}
RUNTIME_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
RUNTIME_NAMES = {".DS_Store", "Thumbs.db", ".coverage"}
RUNTIME_SUFFIXES = {".pyc", ".pyo"}
WRAPPER_RE = re.compile(r"^(?:Certiaura[_ -]?Build|Build)[_ -]?\d+[A-Za-z]?(?:[_ -].*)?$", re.I)


class PreflightError(RuntimeError):
    pass


@dataclass
class Report:
    package: str
    valid: bool = False
    build_number: str | None = None
    package_file_count: int = 0
    staged_file_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    gates: dict[str, bool] = field(default_factory=dict)
    synthetic_repository: dict[str, Any] = field(default_factory=dict)

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "package": self.package,
            "build_number": self.build_number,
            "package_file_count": self.package_file_count,
            "staged_file_count": self.staged_file_count,
            "valid": self.valid,
            "gates": self.gates,
            "synthetic_repository": self.synthetic_repository,
            "warnings": self.warnings,
            "errors": self.errors,
        }


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise PreflightError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def _normalise_member(name: str) -> str:
    if "\\" in name:
        raise PreflightError(f"Backslash path separator is prohibited in ZIP member: {name}")
    p = PurePosixPath(name)
    if p.is_absolute() or not p.parts or any(part in {"", ".", ".."} for part in p.parts):
        raise PreflightError(f"Unsafe ZIP member path: {name}")
    return p.as_posix()


def _is_runtime_artifact(path: str) -> bool:
    p = PurePosixPath(path)
    return (
        any(part in RUNTIME_PARTS for part in p.parts)
        or p.name in RUNTIME_NAMES
        or p.suffix.lower() in RUNTIME_SUFFIXES
    )


def _decode_text(path: str, data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PreflightError(f"Text file is not valid UTF-8: {path}: {exc}") from exc


def _validate_text(path: str, data: bytes) -> None:
    text = _decode_text(path, data)
    if "\r" in text:
        raise PreflightError(f"Non-LF line ending detected: {path}")
    if text and not text.endswith("\n"):
        raise PreflightError(f"Missing final newline: {path}")
    for line_no, line in enumerate(text.split("\n"), start=1):
        if line.endswith(" ") or line.endswith("\t"):
            raise PreflightError(f"Trailing whitespace: {path}:{line_no}")
    suffix = PurePosixPath(path).suffix.lower()
    if suffix == ".json":
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            raise PreflightError(f"Invalid JSON: {path}: {exc}") from exc
    if suffix == ".py":
        try:
            compile(text, path, "exec")
        except SyntaxError as exc:
            raise PreflightError(f"Python compilation failed: {path}: {exc}") from exc


def _find_single(paths: Iterable[str], suffix: str) -> str:
    matches = [p for p in paths if p.endswith(suffix)]
    if len(matches) != 1:
        raise PreflightError(f"Expected exactly one {suffix}; found {len(matches)}")
    return matches[0]


def _load_json(files: dict[str, bytes], path: str) -> dict[str, Any]:
    try:
        obj = json.loads(_decode_text(path, files[path]))
    except KeyError as exc:
        raise PreflightError(f"Required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PreflightError(f"Invalid JSON: {path}: {exc}") from exc
    if not isinstance(obj, dict):
        raise PreflightError(f"JSON object required: {path}")
    return obj


def _validate_inventory(files: dict[str, bytes], inventory_path: str) -> None:
    text = _decode_text(inventory_path, files[inventory_path])
    rows = list(csv.DictReader(text.splitlines()))
    required = {"path", "classification", "action", "sha256", "size_bytes"}
    if not rows or not required.issubset(set(rows[0].keys())):
        raise PreflightError("Package inventory columns are invalid")
    row_paths = [row["path"] for row in rows]
    if len(row_paths) != len(set(row_paths)):
        raise PreflightError("Duplicate path in package inventory")
    if set(row_paths) != set(files):
        missing = sorted(set(files) - set(row_paths))
        extra = sorted(set(row_paths) - set(files))
        raise PreflightError(f"Inventory/member mismatch; missing={missing}; extra={extra}")
    for row in rows:
        path = row["path"]
        expected_size = int(row["size_bytes"])
        if expected_size != len(files[path]):
            raise PreflightError(f"Inventory size mismatch: {path}")
        expected_hash = row["sha256"].strip().lower()
        if expected_hash and expected_hash != _sha256(files[path]):
            raise PreflightError(f"Inventory hash mismatch: {path}")


def _validate_checksums(files: dict[str, bytes], checksum_path: str) -> None:
    entries: dict[str, str] = {}
    for line in _decode_text(checksum_path, files[checksum_path]).splitlines():
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise PreflightError(f"Malformed checksum line: {line}")
        digest, path = parts[0].lower(), parts[1]
        if path in entries:
            raise PreflightError(f"Duplicate checksum path: {path}")
        entries[path] = digest
    expected_paths = set(files) - {checksum_path}
    if set(entries) != expected_paths:
        raise PreflightError("Checksum/member set mismatch")
    for path, digest in entries.items():
        if digest != _sha256(files[path]):
            raise PreflightError(f"Checksum mismatch: {path}")


def _validate_manifests(files: dict[str, bytes], report: Report) -> tuple[dict[str, Any], str]:
    manifest_path = _find_single(files, "/BUILD_MANIFEST.json")
    manifest = _load_json(files, manifest_path)
    build_number = str(manifest.get("build_number", "")).strip()
    if not re.fullmatch(r"\d{4}[A-Za-z]?", build_number):
        raise PreflightError("Invalid or missing build number")
    report.build_number = build_number
    record_root = f"Documentation/Build_Records/{build_number}/"
    required_paths = {
        record_root + "BUILD_MANIFEST.json",
        record_root + "PACKAGE_INVENTORY.csv",
        record_root + "CHECKSUMS.sha256",
        record_root + "ROUTING_MANIFEST.json",
        record_root + "ASSET_INTENT_MANIFEST.json",
        record_root + "PRE_RELEASE_SYNTHETIC_IMPORT_REPORT.json",
        record_root + "COMMIT_MESSAGE.txt",
    }
    missing = sorted(required_paths - set(files))
    if missing:
        raise PreflightError(f"Mandatory build records missing: {missing}")
    if int(manifest.get("package_file_count", -1)) != len(files):
        raise PreflightError("Build manifest package_file_count does not match ZIP")
    if manifest.get("destructive_deletions_permitted") is not False:
        raise PreflightError("Destructive deletions must be explicitly false for standard packages")
    commit = _decode_text(record_root + "COMMIT_MESSAGE.txt", files[record_root + "COMMIT_MESSAGE.txt"]).strip()
    if commit != manifest.get("exact_commit_message"):
        raise PreflightError("Commit message record does not match build manifest")
    expected_prefix = f"Add Certiaura Build {build_number} "
    if not commit.startswith(expected_prefix):
        raise PreflightError("Commit message does not follow the locked convention")

    routing = _load_json(files, record_root + "ROUTING_MANIFEST.json")
    routing_paths = [str(item.get("path", "")) for item in routing.get("files", [])]
    if set(routing_paths) != set(files) or len(routing_paths) != len(set(routing_paths)):
        raise PreflightError("Routing manifest does not classify the exact ZIP member set")

    intent = _load_json(files, record_root + "ASSET_INTENT_MANIFEST.json")
    intent_paths = [str(item.get("path", "")) for item in intent.get("files", [])]
    if set(intent_paths) != set(files) or len(intent_paths) != len(set(intent_paths)):
        raise PreflightError("Asset Intent Manifest does not classify the exact ZIP member set")
    for item in intent.get("files", []):
        if item.get("intended_action") == "DELETE":
            raise PreflightError(f"Delete action is prohibited: {item.get('path')}")

    _validate_inventory(files, record_root + "PACKAGE_INVENTORY.csv")
    _validate_checksums(files, record_root + "CHECKSUMS.sha256")
    return manifest, record_root


def _load_zip(package: Path, report: Report) -> tuple[dict[str, bytes], dict[str, Any]]:
    if not package.is_file():
        raise PreflightError(f"Package not found: {package}")
    if package.suffix.lower() != ".zip":
        raise PreflightError("Package must be a ZIP file")
    files: dict[str, bytes] = {}
    lowered: dict[str, str] = {}
    with zipfile.ZipFile(package, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            path = _normalise_member(info.filename)
            if path in files:
                raise PreflightError(f"Duplicate ZIP path: {path}")
            low = path.casefold()
            if low in lowered:
                raise PreflightError(f"Case-only path collision: {lowered[low]} vs {path}")
            lowered[low] = path
            files[path] = zf.read(info)
    if not files:
        raise PreflightError("Package is empty")
    report.package_file_count = len(files)
    first_parts = {PurePosixPath(path).parts[0] for path in files}
    wrappers = sorted(part for part in first_parts if WRAPPER_RE.match(part))
    if wrappers:
        raise PreflightError(f"Build wrapper folder detected: {wrappers}")
    unauthorised = sorted(part for part in first_parts if part not in ALLOWED_ROOTS)
    if unauthorised:
        raise PreflightError(f"Unauthorised repository roots: {unauthorised}")
    for path, data in files.items():
        if _is_runtime_artifact(path):
            raise PreflightError(f"Runtime artefact prohibited: {path}")
        if PurePosixPath(path).suffix.lower() in TEXT_SUFFIXES:
            _validate_text(path, data)
    manifest, _ = _validate_manifests(files, report)
    return files, manifest


def _write_unrelated_history(repo: Path) -> dict[str, str]:
    historical = {
        "00_Governance/UNRELATED_HISTORICAL_DECISION.md": "# Historical decision\n\nUnrelated baseline record.\n",
        "Documentation/Historical/UNRELATED_LEGACY_RECORD.md": "# Legacy record\n\nPreserve this file.\n",
        "Database/Legacy/unrelated_reference.csv": "key,value\nlegacy,1\n",
        "13_Project_Genesis/Legacy/unrelated_utility.py": "VALUE = 'unrelated'\n",
    }
    for rel, content in historical.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return {rel: _sha256((repo / rel).read_bytes()) for rel in historical}


def _write_synthetic_register(repo: Path) -> tuple[str, int]:
    rel = "Documentation/Master_Asset_Register.csv"
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "Universal Asset Identifier", "Asset Name", "Knowledge System", "Asset Type",
        "Status", "Owner", "Repository Path", "Version", "Completion Percentage",
        "Last Review", "Next Review", "Build Provenance", "Source Builds", "Registration Basis",
    ]
    rows = [
        {
            "Universal Asset Identifier": "CERT-SYS-000009",
            "Asset Name": "Locked Build Continuity and Checkpoint",
            "Knowledge System": "SYS",
            "Repository Path": "00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",
            "Status": "ACTIVE",
        },
        {
            "Universal Asset Identifier": "CERT-SYS-000082",
            "Asset Name": "Transactional Build Importer",
            "Knowledge System": "SYS",
            "Repository Path": "13_Project_Genesis/Import/transactional_build_import.py",
            "Status": "ACTIVE",
        },
        {
            "Universal Asset Identifier": "CERT-PKS-000001",
            "Asset Name": "Unrelated Peptide Record",
            "Knowledge System": "PKS",
            "Repository Path": "02_Peptides/Unrelated_Record.md",
            "Status": "ACTIVE",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return rel, len(rows)


def _safe_extract(files: dict[str, bytes], repo: Path) -> None:
    base = repo.resolve()
    for rel, data in files.items():
        target = (repo / Path(*PurePosixPath(rel).parts)).resolve()
        if os.path.commonpath([str(base), str(target)]) != str(base):
            raise PreflightError(f"Extraction escaped repository: {rel}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def _scan_runtime(repo: Path) -> list[str]:
    found: list[str] = []
    for path in repo.rglob("*"):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(repo).as_posix()
        if _is_runtime_artifact(rel):
            found.append(rel)
    return sorted(found)


def _read_json_file(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PreflightError(f"JSON object required: {path}")
    return value


def _run_real_importer(
    package: Path,
    files: dict[str, bytes],
    manifest: dict[str, Any],
    repo: Path,
    temp_root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    importer_rel = "13_Project_Genesis/Import/transactional_build_import.py"
    runner_rel = f"13_Project_Genesis/Import/run_build_{manifest['build_number']}_import.py"
    if importer_rel not in files:
        raise PreflightError("Candidate package does not contain the build-neutral transactional importer")
    if runner_rel not in files:
        raise PreflightError(f"Candidate package does not contain the current-build runner: {runner_rel}")

    execution_root = temp_root / "candidate_importer"
    execution_root.mkdir(parents=True, exist_ok=True)
    importer_path = execution_root / importer_rel
    runner_path = execution_root / runner_rel
    importer_path.parent.mkdir(parents=True, exist_ok=True)
    importer_path.write_bytes(files[importer_rel])
    runner_path.write_bytes(files[runner_rel])

    dry_report_path = temp_root / "actual_importer_dry_run.json"
    apply_report_path = temp_root / "actual_importer_apply.json"
    backup_root = temp_root / "Backups"
    env = dict(os.environ)
    env["CERTIAURA_BACKUP_ROOT"] = str(backup_root)

    dry = subprocess.run(
        [
            sys.executable, "-B", str(runner_path), str(package), str(repo),
            "--asset-register", "Documentation/Master_Asset_Register.csv",
            "--report", str(dry_report_path),
        ],
        cwd=execution_root,
        env=env,
        text=True,
        capture_output=True,
    )
    if dry.returncode != 0:
        raise PreflightError(
            f"Actual importer dry run failed ({dry.returncode})\nSTDOUT:\n{dry.stdout}\nSTDERR:\n{dry.stderr}"
        )
    dry_report = _read_json_file(dry_report_path)
    expected = {
        "build_number": str(manifest["build_number"]),
        "build_title": str(manifest["build_title"]),
        "package_version": str(manifest["package_version"]),
    }
    for key, value in expected.items():
        if dry_report.get(key) != value:
            raise PreflightError(f"Importer dry-run metadata mismatch for {key}: {dry_report.get(key)!r} != {value!r}")
    if not dry_report.get("valid") or not dry_report.get("apply_allowed") or dry_report.get("applied"):
        raise PreflightError("Importer dry-run status is not valid/apply_allowed/non-applied")
    if dry_report.get("asset_manifest_path") != f"Documentation/Build_Records/{manifest['build_number']}/ASSET_INTENT_MANIFEST.json":
        raise PreflightError("Importer resolved the wrong Asset Intent Manifest path")

    clean_after_dry = _run(["git", "status", "--porcelain", "--untracked-files=all"], repo).stdout.splitlines()
    if clean_after_dry:
        raise PreflightError(f"Actual importer dry run changed the repository: {clean_after_dry}")

    apply_result = subprocess.run(
        [
            sys.executable, "-B", str(runner_path), str(package), str(repo),
            "--asset-register", "Documentation/Master_Asset_Register.csv",
            "--report", str(apply_report_path), "--apply",
        ],
        cwd=execution_root,
        env=env,
        text=True,
        capture_output=True,
    )
    if apply_result.returncode != 0:
        raise PreflightError(
            f"Actual importer apply failed ({apply_result.returncode})\nSTDOUT:\n{apply_result.stdout}\nSTDERR:\n{apply_result.stderr}"
        )
    apply_report = _read_json_file(apply_report_path)
    for key, value in expected.items():
        if apply_report.get(key) != value:
            raise PreflightError(f"Importer apply metadata mismatch for {key}: {apply_report.get(key)!r} != {value!r}")
    if not apply_report.get("valid") or not apply_report.get("applied"):
        raise PreflightError("Importer apply did not finish valid and applied")
    if apply_report.get("transaction_status") != "APPLIED_VALIDATED":
        raise PreflightError("Importer transaction status is not APPLIED_VALIDATED")
    journal = Path(str(apply_report.get("transaction_journal", "")))
    if not journal.is_file():
        raise PreflightError("Importer did not create a transaction journal")
    journal_data = _read_json_file(journal)
    for key, value in expected.items():
        if journal_data.get(key) != value:
            raise PreflightError(f"Transaction journal metadata mismatch for {key}")
    return dry_report, apply_report


def _synthetic_import(package: Path, files: dict[str, bytes], manifest: dict[str, Any], report: Report, keep_temp: bool) -> None:
    temp_obj = tempfile.TemporaryDirectory(prefix="certiaura_preflight_")
    temp_root = Path(temp_obj.name)
    repo = temp_root / "synthetic_repo"
    repo.mkdir(parents=True)
    try:
        _run(["git", "init", "-b", "main"], repo)
        _run(["git", "config", "user.email", "preflight@certiaura.invalid"], repo)
        _run(["git", "config", "user.name", "Certiaura Preflight"], repo)
        baseline_hashes = _write_unrelated_history(repo)
        register_rel, register_baseline_rows = _write_synthetic_register(repo)

        routing_path = _find_single(files, "/ROUTING_MANIFEST.json")
        routing = json.loads(_decode_text(routing_path, files[routing_path]))
        replacement_paths = sorted(
            str(item.get("path"))
            for item in routing.get("files", [])
            if item.get("action") == "REPLACE_FILE"
        )
        for rel in replacement_paths:
            target = repo / Path(*PurePosixPath(rel).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"SYNTHETIC PRE-EXISTING REPOSITORY CONTENT\n")

        _run(["git", "add", "-A"], repo)
        _run(["git", "commit", "-m", "Synthetic unrelated historical baseline"], repo)
        baseline_commit = _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()

        dry_report, apply_report = _run_real_importer(package, files, manifest, repo, temp_root)

        for rel, digest in baseline_hashes.items():
            path = repo / rel
            if not path.is_file() or _sha256(path.read_bytes()) != digest:
                raise PreflightError(f"Unrelated historical file changed or missing: {rel}")

        expected_register_total = register_baseline_rows + int(manifest.get("formal_assets_created", 0))
        if int(apply_report.get("expected_register_total", -1)) != expected_register_total:
            raise PreflightError(
                f"Synthetic register total mismatch: {apply_report.get('expected_register_total')} != {expected_register_total}"
            )
        allocations = apply_report.get("allocated_identifiers", [])
        if int(manifest.get("formal_assets_created", 0)) != len(allocations):
            raise PreflightError("Synthetic UAI allocation count does not match formal_assets_created")

        deleted = _run(["git", "diff", "--name-only", "--diff-filter=D"], repo).stdout.splitlines()
        if deleted:
            raise PreflightError(f"Unexpected tracked deletions before staging: {deleted}")

        _run(["git", "add", "-A"], repo)
        _run(["git", "diff", "--check"], repo)
        _run(["git", "diff", "--cached", "--check"], repo)

        deleted_cached = _run(["git", "diff", "--cached", "--name-only", "--diff-filter=D"], repo).stdout.splitlines()
        if deleted_cached:
            raise PreflightError(f"Unexpected staged deletions: {deleted_cached}")
        unstaged = _run(["git", "diff", "--name-only"], repo).stdout.splitlines()
        if unstaged:
            raise PreflightError(f"Unstaged changes remain after staging: {unstaged}")
        untracked = _run(["git", "ls-files", "--others", "--exclude-standard"], repo).stdout.splitlines()
        if untracked:
            raise PreflightError(f"Untracked files remain after staging: {untracked}")

        staged = _run(["git", "diff", "--cached", "--name-only"], repo).stdout.splitlines()
        expected_staged = set(files) | {register_rel}
        if set(staged) != expected_staged:
            missing = sorted(expected_staged - set(staged))
            extra = sorted(set(staged) - expected_staged)
            raise PreflightError(f"Staged path set differs from imported transaction; missing={missing}; extra={extra}")

        runtime = _scan_runtime(repo)
        if runtime:
            raise PreflightError(f"Runtime artefacts present after synthetic import: {runtime}")

        report.staged_file_count = len(staged)
        report.synthetic_repository = {
            "baseline_commit_created": True,
            "baseline_commit": baseline_commit,
            "unrelated_historical_file_count": len(baseline_hashes),
            "unrelated_historical_files_preserved": True,
            "declared_replacement_paths_seeded": len(replacement_paths),
            "actual_importer_dry_run": "PASS",
            "actual_importer_apply": "PASS",
            "importer_metadata_matches_current_build": True,
            "transaction_journal_validated": True,
            "master_asset_register_reconciled": True,
            "identifier_allocation_validated": True,
            "expected_register_total": expected_register_total,
            "unexpected_deletions": 0,
            "unstaged_changes_after_staging": 0,
            "untracked_files_after_staging": 0,
            "runtime_artifacts_after_validation": 0,
            "git_diff_check": "PASS",
            "git_diff_cached_check": "PASS",
            "staged_paths_match_imported_transaction": True,
            "dry_run_report": dry_report,
            "apply_report_summary": {
                "build_number": apply_report.get("build_number"),
                "build_title": apply_report.get("build_title"),
                "package_version": apply_report.get("package_version"),
                "transaction_status": apply_report.get("transaction_status"),
                "allocated_identifiers": apply_report.get("allocated_identifiers"),
            },
        }
        if keep_temp:
            retained = Path(tempfile.mkdtemp(prefix="certiaura_preflight_retained_")) / "synthetic_repo"
            shutil.copytree(repo, retained)
            report.synthetic_repository["retained_path"] = str(retained)
    finally:
        temp_obj.cleanup()


def run_preflight(package: Path, keep_temp: bool = False) -> Report:
    report = Report(package=str(package))
    try:
        files, manifest = _load_zip(package, report)
        report.gates.update({
            "zip_member_validation": True,
            "repository_route_allowlist": True,
            "wrapper_folder_absent": True,
            "case_collision_absent": True,
            "runtime_artifacts_absent": True,
            "text_normalization": True,
            "json_parsing": True,
            "python_compilation": True,
            "manifest_self_validation": True,
            "inventory_self_validation": True,
            "checksum_validation": True,
        })
        _synthetic_import(package, files, manifest, report, keep_temp)
        report.gates.update({
            "synthetic_git_repository": True,
            "actual_transactional_importer_dry_run": True,
            "actual_transactional_importer_apply": True,
            "current_build_metadata_validation": True,
            "master_asset_register_reconciliation": True,
            "transaction_backup_and_journal": True,
            "unrelated_history_preserved": True,
            "unexpected_deletions_absent": True,
            "all_changes_staged": True,
            "git_diff_check_after_staging": True,
            "git_diff_cached_check_after_staging": True,
            "unstaged_changes_absent": True,
            "untracked_runtime_artifacts_absent": True,
        })
        report.valid = True
    except Exception as exc:
        report.fail(str(exc))
        report.valid = False
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Certiaura build-package automated preflight")
    parser.add_argument("package", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--keep-temp", action="store_true")
    args = parser.parse_args(argv)

    report = run_preflight(args.package.resolve(), keep_temp=args.keep_temp)
    payload = json.dumps(report.as_dict(), indent=2, sort_keys=False) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8", newline="\n")
    sys.stdout.write(payload)
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
