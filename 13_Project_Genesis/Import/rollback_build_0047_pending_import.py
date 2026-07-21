from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

BUILD_ID = "CERT-BUILD-0047"
REGISTER_PATH = "Documentation/Master_Asset_Register.csv"
ALLOWED_ROOTS = {
    "00_Governance", "01_Knowledge_Systems", "02_Peptides", "03_Biology", "04_Conditions",
    "05_Monitoring", "06_Evidence", "07_Goals", "08_Product_Passports", "09_Cost_Intelligence",
    "10_Marketplace", "11_Academy", "12_Reports", "13_Project_Genesis", "Assets", "Database",
    "Documentation", "Images", "Schemas", "Scripts", "Standards", "Templates",
}


def now_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def safe_relative(value: str) -> Path:
    posix = PurePosixPath(value.replace("\\", "/"))
    if posix.is_absolute() or not posix.parts or ".." in posix.parts:
        raise ValueError(f"unsafe rollback path: {value}")
    if posix.parts[0] not in ALLOWED_ROOTS:
        raise ValueError(f"unauthorised rollback root: {posix.parts[0]}")
    return Path(*posix.parts)


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {message}")
    return result.stdout


def remove_empty_parents(path: Path, stop: Path) -> None:
    parent = path.parent
    while parent != stop and is_within(parent, stop):
        try:
            parent.rmdir()
        except OSError:
            break
        parent = parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--apply-report", required=True, type=Path)
    parser.add_argument("--rollback-report", required=True, type=Path)
    parser.add_argument("--expected-package-sha256")
    args = parser.parse_args()

    repo = args.repository.resolve()
    apply_report_path = args.apply_report.resolve()
    rollback_report_path = args.rollback_report.resolve()
    result: dict = {
        "build_id": BUILD_ID,
        "generated_at": now_z(),
        "status": "FAILED_CLOSED",
        "valid": False,
        "errors": [],
        "removed_created_paths": [],
        "restored_replacement_paths": [],
        "register_restored": False,
        "backup_retained": True,
    }

    try:
        if not (repo / ".git").is_dir():
            raise ValueError("repository must be a Git working tree")
        if not apply_report_path.is_file():
            raise FileNotFoundError(f"apply report not found: {apply_report_path}")

        apply_report = json.loads(apply_report_path.read_text(encoding="utf-8"))
        if apply_report.get("build_id") != BUILD_ID:
            raise ValueError("apply report build_id mismatch")
        if not bool(apply_report.get("applied")):
            raise ValueError("apply report does not record an applied transaction")
        if not bool(apply_report.get("valid")):
            raise ValueError("apply report is not valid")

        expected_package = (args.expected_package_sha256 or "").strip().upper()
        actual_package = str(apply_report.get("package_sha256", "")).strip().upper()
        if expected_package and actual_package != expected_package:
            raise ValueError("apply report package SHA-256 mismatch")
        result["package_sha256"] = actual_package

        backup_value = str(apply_report.get("backup_path", "")).strip()
        if not backup_value:
            raise ValueError("apply report does not contain backup_path")
        backup = Path(backup_value).resolve()
        if not backup.is_dir():
            raise FileNotFoundError(f"external transactional backup missing: {backup}")
        if is_within(backup, repo):
            raise ValueError("transactional backup is inside the repository")
        result["backup_path"] = str(backup)

        current_head = run_git(repo, "rev-parse", "HEAD").strip()
        expected_head = str(apply_report.get("repository_head_before_apply", "")).strip()
        if expected_head and current_head != expected_head:
            raise ValueError(
                "repository HEAD changed after apply; automatic pre-commit rollback is prohibited"
            )
        result["repository_head"] = current_head

        file_actions = {
            str(item.get("path")): item
            for item in apply_report.get("file_actions", [])
            if item.get("path")
        }
        changed_paths = [str(value) for value in apply_report.get("changed_paths", [])]
        if not changed_paths:
            raise ValueError("apply report does not contain changed_paths")
        if len(changed_paths) != len(set(changed_paths)):
            raise ValueError("apply report contains duplicate changed_paths")

        # The workflow starts from a clean index. Reset only the index so files can be
        # restored from the transaction report and external backup deterministically.
        run_git(repo, "reset", "--mixed", "HEAD")

        created_for_cleanup: list[Path] = []
        for value in reversed(changed_paths):
            rel = safe_relative(value)
            action_record = file_actions.get(value)
            if action_record is None:
                raise ValueError(f"changed path missing file action: {value}")
            action = str(action_record.get("action", ""))
            dest = repo / rel
            incoming_hash = str(action_record.get("incoming_sha256", "")).strip().upper()

            if action == "CREATE_FILE":
                if dest.exists() or dest.is_symlink():
                    if dest.is_dir() and not dest.is_symlink():
                        raise ValueError(f"created path became a directory: {value}")
                    if incoming_hash and sha256_file(dest) != incoming_hash:
                        raise ValueError(
                            f"created file changed after import; refusing deletion: {value}"
                        )
                    dest.unlink()
                result["removed_created_paths"].append(value)
                created_for_cleanup.append(dest)
            elif action == "APPROVED_REPLACEMENT":
                source = backup / "repository_files" / rel
                if not source.is_file():
                    raise FileNotFoundError(f"replacement backup missing: {source}")
                if dest.exists() and incoming_hash and sha256_file(dest) != incoming_hash:
                    raise ValueError(
                        f"replacement file changed after import; refusing restore: {value}"
                    )
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                result["restored_replacement_paths"].append(value)
            else:
                raise ValueError(
                    f"changed path has unsupported rollback action {action}: {value}"
                )

        register_backup = backup / REGISTER_PATH
        if not register_backup.is_file():
            raise FileNotFoundError(
                f"Master Asset Register backup missing: {register_backup}"
            )
        register_dest = repo / REGISTER_PATH
        register_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(register_backup, register_dest)
        result["register_restored"] = True
        result["register_sha256"] = sha256_file(register_dest)

        for created in created_for_cleanup:
            remove_empty_parents(created, repo)

        dirty = run_git(repo, "status", "--porcelain", "--untracked-files=all")
        if dirty.strip():
            result["remaining_git_status"] = dirty.splitlines()
            raise ValueError("repository is not clean after rollback")

        result.update({
            "status": "ROLLED_BACK_CLEAN",
            "valid": True,
            "repository_clean": True,
            "apply_report": str(apply_report_path),
        })
    except Exception as exc:
        result["errors"].append(str(exc))

    rollback_report_path.parent.mkdir(parents=True, exist_ok=True)
    rollback_report_path.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
