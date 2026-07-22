from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

BUILD = "0052"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def materialise(package: str):
    path = Path(package)
    if path.is_dir():
        return path.resolve(), None
    temporary = Path(tempfile.mkdtemp(prefix="certiaura_0052_rc6_"))
    with zipfile.ZipFile(path) as archive:
        archive.extractall(temporary)
    return temporary, temporary


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="ascii", newline="\n")


def validate_register(repo: Path):
    path = repo / "Documentation/Master_Asset_Register.csv"
    if not path.is_file():
        raise RuntimeError("Canonical Master Asset Register missing")
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
    if not rows:
        raise RuntimeError("Canonical Master Asset Register empty")
    fields = list(rows[0].keys())
    if "Universal Asset Identifier" not in fields or "Repository Path" not in fields:
        raise RuntimeError("Canonical Master Asset Register columns invalid")
    uais = [row.get("Universal Asset Identifier", "").strip() for row in rows if row.get("Universal Asset Identifier", "").strip()]
    if len(uais) != len(set(uais)):
        raise RuntimeError("Duplicate UAI in canonical Master Asset Register")
    return path, len(rows), sha(path)


def run_command(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    result = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError("COMMAND_FAILED: " + " ".join(args) + "\n" + result.stdout + "\n" + result.stderr)
    return result


def snapshot_index(repo: Path, backup: Path) -> None:
    git_dir = run_command(["git", "-C", str(repo), "rev-parse", "--git-dir"]).stdout.strip()
    git_path = Path(git_dir)
    if not git_path.is_absolute():
        git_path = repo / git_path
    index = git_path / "index"
    if index.is_file():
        shutil.copy2(index, backup / "GIT_INDEX_BEFORE")


def restore_index(repo: Path, backup: Path) -> None:
    saved = backup / "GIT_INDEX_BEFORE"
    if not saved.is_file():
        return
    git_dir = run_command(["git", "-C", str(repo), "rev-parse", "--git-dir"]).stdout.strip()
    git_path = Path(git_dir)
    if not git_path.is_absolute():
        git_path = repo / git_path
    shutil.copy2(saved, git_path / "index")


def validate_evidence(evidence: dict, repo: Path, package_sha: str, manifest: dict) -> None:
    if evidence.get("result") != "PREDECESSOR_CANONICAL_EVIDENCE_VALIDATED":
        raise RuntimeError("Predecessor evidence result invalid")
    if evidence.get("package_sha256") != package_sha:
        raise RuntimeError("Predecessor evidence package SHA mismatch")
    if evidence.get("negative_tests_result") != "PASS" or evidence.get("negative_test_count") != 15:
        raise RuntimeError("Predecessor negative tests incomplete")
    schema = evidence.get("predecessor_manifest_path_schema")
    if not isinstance(schema, dict) or schema.get("container") not in ("ARRAY", "OBJECT_MAP"):
        raise RuntimeError("Predecessor manifest schema evidence invalid")
    paths = evidence.get("repository_paths", [])
    hashes = evidence.get("path_sha256", {})
    if not paths or sorted(paths) != sorted(hashes):
        raise RuntimeError("Predecessor evidence path/hash set invalid")
    current_paths = {x.get("repository_path") for x in manifest.get("files", [])}
    approved = {x.get("repository_path") for x in manifest.get("files", []) if x.get("approved_replacement") is True and x.get("predecessor_build") == "0051"}
    if (set(paths) & current_paths) - approved:
        raise RuntimeError("Unauthorised predecessor/current manifest intersection")
    closed = evidence.get("closed_snapshot_sha")
    for relative in paths:
        actual = subprocess.run(["git", "-C", str(repo), "show", f"{closed}:{relative}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if actual.returncode != 0 or hashlib.sha256(actual.stdout).hexdigest().upper() != hashes[relative]:
            raise RuntimeError("Canonical predecessor object mismatch: " + relative)


def run(repository: str, package: str, report: str, predecessor_evidence: str, package_sha: str, apply: bool, backup_root: str | None, simulate_failure: bool) -> int:
    repo = Path(repository).resolve()
    root, temporary = materialise(package)
    try:
        manifest = load(root / "Documentation/Build_Records/0052/ASSET_INTENT_MANIFEST.json")
        entries = manifest["files"]
        paths = [x["repository_path"] for x in entries]
        by_path = {x["repository_path"]: x for x in entries}
        evidence = load(Path(predecessor_evidence).resolve())
        validate_evidence(evidence, repo, package_sha.upper(), manifest)
        register_path, register_rows, register_hash = validate_register(repo)
        routing = []
        conflicts = []
        for relative in paths:
            source = root / relative
            destination = repo / relative
            if not source.is_file():
                raise RuntimeError("Manifest source missing: " + relative)
            state = "ABSENT"
            if destination.exists():
                state = "IDENTICAL" if sha(source) == sha(destination) else "CONFLICT"
                if state == "CONFLICT" and by_path[relative].get("approved_replacement") is True and by_path[relative].get("intended_action") == "UPDATE":
                    state = "APPROVED_REPLACEMENT"
                elif state == "CONFLICT":
                    conflicts.append(relative)
            routing.append({"source": relative, "target": relative, "destination_state": state})
        result = {
            "valid": not conflicts,
            "build_number": BUILD,
            "candidate": "RC6",
            "mode": "APPLY" if apply else "DRY_RUN",
            "transaction_status": "FAILED_CLOSED" if conflicts else ("APPLIED_VALIDATED" if apply else "DRY_RUN_VALIDATED"),
            "applied": False,
            "canonical_register": "Documentation/Master_Asset_Register.csv",
            "register_rows_before": register_rows,
            "expected_register_rows_after": register_rows,
            "formal_asset_count": 0,
            "routing": routing,
            "conflicts": conflicts,
            "predecessor_import_commit_sha": evidence["import_commit_sha"],
            "predecessor_closed_snapshot_sha": evidence["closed_snapshot_sha"],
            "predecessor_path_count": evidence["path_count"],
            "predecessor_unauthorised_intersection": evidence["unauthorised_manifest_intersection"],
            "backup_path": None,
        }
        if conflicts:
            write_json(Path(report), result)
            return 2
        if not apply:
            write_json(Path(report), result)
            print(json.dumps(result, indent=2))
            return 0
        if not backup_root:
            raise RuntimeError("External backup root required")
        backup_parent = Path(backup_root).resolve()
        try:
            backup_parent.relative_to(repo)
            raise RuntimeError("Backup root must be outside repository")
        except ValueError:
            pass
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        backup = backup_parent / ("Build_0052_RC6_Pre_Import_" + stamp)
        backup.mkdir(parents=True, exist_ok=False)
        snapshot_index(repo, backup)
        existing = []
        changed = []
        for relative in paths:
            destination = repo / relative
            if destination.is_file():
                existing.append(relative)
                target = backup / "WORKTREE_BEFORE" / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination, target)
        write_json(backup / "BACKUP_RECORD.json", {"build_number":"0052","candidate":"RC6","repository":str(repo),"paths":paths,"existing_paths":existing,"register_sha256":register_hash})
        try:
            for relative in paths:
                source = root / relative
                destination = repo / relative
                if destination.exists() and sha(source) == sha(destination):
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                changed.append(relative)
            evidence_target = repo / "Documentation/Build_Records/0052/PREDECESSOR_CANONICAL_EVIDENCE.json"
            write_json(evidence_target, evidence)
            updater_report = repo / "Documentation/Build_Records/0052/ACCUMULATED_LESSONS_UPDATE_REPORT.json"
            run_command([sys.executable, "-B", str(repo / "Scripts/update_certiaura_accumulated_lessons.py"), "--repository", str(repo), "--current-build", "0052", "--report", str(updater_report), "--apply"])
            updater_result = load(updater_report)
            write_json(repo / "Documentation/Build_Records/0052/LESSONS_COVERAGE_REPORT.json", {"build_number":"0052","candidate":"RC6","result":"LESSONS_COVERAGE_COMPLETE","historical_coverage":updater_result.get("historical_coverage"),"historical_coverage_mode":updater_result.get("historical_coverage_mode"),"discovered_matrix_builds":updater_result.get("discovered_matrix_builds"),"ledger_only_builds":updater_result.get("ledger_only_builds"),"covered_builds":updater_result.get("covered_builds"),"ledger_only_historical_evidence":updater_result.get("ledger_only_historical_evidence"),"current_build_lesson_ids":updater_result.get("current_build_lesson_ids")})
            if simulate_failure:
                raise RuntimeError("SIMULATED_POST_APPLY_FAILURE")
            _, rows_after, register_hash_after = validate_register(repo)
            if rows_after != register_rows or register_hash_after != register_hash:
                raise RuntimeError("Master Asset Register changed despite zero formal asset delta")
            result["applied"] = True
            result["backup_path"] = str(backup)
            result["changed_paths"] = changed
            result["register_rows_after"] = rows_after
            result["master_asset_register_reconciliation"] = "PASS_ZERO_DELTA"
            write_json(Path(report), result)
            print(json.dumps(result, indent=2))
            return 0
        except Exception as exc:
            for relative in paths:
                destination = repo / relative
                before = backup / "WORKTREE_BEFORE" / relative
                if relative in existing and before.is_file():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(before, destination)
                elif relative not in existing and destination.exists():
                    destination.unlink()
            restore_index(repo, backup)
            result["transaction_status"] = "ROLLED_BACK"
            result["rollback_completed"] = True
            result["backup_path"] = str(backup)
            result["rollback_reason"] = str(exc)
            result["failure_code"] = "BUILD_0052_TRANSACTION_ROLLED_BACK"
            write_json(Path(report), result)
            failure_message = (
                "BUILD_0052_TRANSACTION_ROLLED_BACK: "
                + str(exc)
                + " | report="
                + str(Path(report).resolve())
                + " | backup="
                + str(backup)
            )
            print(failure_message, file=sys.stderr)
            return 3
    finally:
        if temporary:
            shutil.rmtree(temporary, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--predecessor-evidence", required=True)
    parser.add_argument("--package-sha256", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup-root")
    parser.add_argument("--simulate-post-apply-failure", action="store_true")
    args = parser.parse_args()
    return run(args.repository, args.package, args.report, args.predecessor_evidence, args.package_sha256, args.apply, args.backup_root, args.simulate_post_apply_failure)


if __name__ == "__main__":
    sys.exit(main())
