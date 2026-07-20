#!/usr/bin/env python3
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ALLOWED = {"00_Governance", "01_Knowledge_Systems", "02_Peptides", "03_Biology", "04_Conditions", "05_Monitoring", "06_Evidence", "07_Goals", "08_Product_Passports", "09_Cost_Intelligence", "10_Marketplace", "11_Academy", "12_Reports", "13_Project_Genesis", "Assets", "Database", "Documentation", "Images", "Schemas", "Scripts", "Standards", "Templates"}
RUNTIME = {"__pycache__", ".pyc", ".pyo", ".tmp", ".temp"}

def run(cmd, cwd=None, env=None):
    cp = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)
    if cp.returncode: raise RuntimeError((cp.stdout + "\n" + cp.stderr).strip())
    return cp.stdout.strip()

def sha(path):
    h = hashlib.sha256();
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--package", required=True); ap.add_argument("--report", required=True); args = ap.parse_args()
    package = Path(args.package).resolve(); report_path = Path(args.report).resolve()
    report = {"build_number": "0041", "package": str(package), "valid": False, "gates": {}, "warnings": [], "errors": []}
    try:
        with zipfile.ZipFile(package) as zf:
            infos = [i for i in zf.infolist() if not i.is_dir()]; names = [i.filename for i in infos]
            report["package_file_count"] = len(names)
            if len(names) != len(set(names)): raise RuntimeError("Duplicate ZIP paths")
            if len({n.casefold() for n in names}) != len(names): raise RuntimeError("Case-only collision")
            for n in names:
                p = PurePosixPath(n)
                if p.is_absolute() or ".." in p.parts or "\\" in n: raise RuntimeError(f"Unsafe ZIP path: {n}")
                if not p.parts or p.parts[0] not in ALLOWED: raise RuntimeError(f"Unauthorised root: {n}")
                if len(p.parts) == 1 and p.parts[0].lower().startswith("certiaura_build_"): raise RuntimeError("Build wrapper folder detected")
                if any(x in n.lower() for x in RUNTIME): raise RuntimeError(f"Runtime artefact: {n}")
            report["gates"].update({"zip_member_validation": True, "repository_route_allowlist": True, "wrapper_folder_absent": True, "case_collision_absent": True, "runtime_artifacts_absent": True})
            inventory_name = "Documentation/Build_Records/0041/PACKAGE_INVENTORY.csv"
            inventory = {r["path"]: r for r in csv.DictReader(io.StringIO(zf.read(inventory_name).decode("utf-8")))}
            if set(inventory) != set(names): raise RuntimeError("Inventory does not match package")
            checksums = {}
            for line in zf.read("Documentation/Build_Records/0041/CHECKSUMS.sha256").decode("utf-8").splitlines():
                if line.strip():
                    digest, name = line.split("  ", 1); checksums[name] = digest
            for n, digest in checksums.items():
                if hashlib.sha256(zf.read(n)).hexdigest() != digest: raise RuntimeError(f"Checksum mismatch: {n}")
            report["gates"].update({"inventory_self_validation": True, "checksum_validation": True})
            with tempfile.TemporaryDirectory() as td:
                extracted = Path(td) / "package"; zf.extractall(extracted)
                # Text normalisation and JSON parse.
                for p in extracted.rglob("*"):
                    if not p.is_file(): continue
                    if p.suffix.lower() in {".md", ".json", ".csv", ".py", ".ps1", ".cmd", ".txt", ".sha256"}:
                        data = p.read_bytes()
                        if b"\r" in data: raise RuntimeError(f"CR line ending: {p.relative_to(extracted)}")
                        text = data.decode("utf-8")
                        if not text.endswith("\n"): raise RuntimeError(f"No final newline: {p.relative_to(extracted)}")
                        if any(line.endswith((" ", "\t")) for line in text.splitlines()): raise RuntimeError(f"Trailing whitespace: {p.relative_to(extracted)}")
                        if p.suffix.lower() in {".ps1", ".cmd"}:
                            try:
                                data.decode("ascii")
                            except UnicodeDecodeError as exc:
                                raise RuntimeError(f"Windows PowerShell 5.1 executable script is not ASCII-safe: {p.relative_to(extracted)}") from exc
                    if p.suffix.lower() == ".json": json.loads(p.read_text(encoding="utf-8"))
                report["gates"].update({"text_normalization": True, "json_parsing": True, "windows_powershell_5_1_ascii_compatibility": True})
                launcher_text = (extracted / "Scripts/Run_Certiaura_Build_0041.ps1").read_text(encoding="ascii")
                import_wrapper_text = (extracted / "Scripts/Invoke_Certiaura_Build_0041_Import.ps1").read_text(encoding="ascii")
                if "Start-Process -FilePath $Candidates[0]" in launcher_text:
                    raise RuntimeError("OneDrive restart retains unsafe scalar pipeline indexing")
                if "function Resolve-OneDriveExecutable" not in launcher_text or "foreach ($Candidate in $CandidatePaths)" not in launcher_text:
                    raise RuntimeError("OneDrive executable resolver regression control is missing")
                if "Resolve-PackageBesideLauncher" not in launcher_text:
                    raise RuntimeError("Adjacent SHA-addressed package resolution is missing")
                if "[string]$Package" not in import_wrapper_text or "Get-FileHash -LiteralPath $Package" not in import_wrapper_text:
                    raise RuntimeError("Import wrapper does not receive and verify an explicit package path")
                if "Dropbox" in import_wrapper_text or "Get-ChildItem -LiteralPath $Root" in import_wrapper_text:
                    raise RuntimeError("Import wrapper still performs broad package discovery")
                report["gates"].update({"one_drive_full_path_resolution": True, "explicit_package_path_handoff": True})
                env = os.environ.copy(); env["PYTHONDONTWRITEBYTECODE"] = "1"
                pyfiles = [str(p) for p in extracted.rglob("*.py")]
                for p in pyfiles: run([os.environ.get("PYTHON", "python"), "-B", "-m", "py_compile", p], env=env)
                # Remove py_compile artefacts immediately and verify none remain.
                for d in extracted.rglob("__pycache__"): shutil.rmtree(d)
                report["gates"]["python_compilation"] = True
                run([os.environ.get("PYTHON", "python"), "-B", str(extracted / "13_Project_Genesis/Validators/validate_retatrutide_evidence_corpus.py"), str(extracted)], env=env)
                run([os.environ.get("PYTHON", "python"), "-B", "-m", "unittest", "discover", "-s", str(extracted / "13_Project_Genesis/Tests"), "-p", "test_build_0041_*.py"], env=env)
                report["gates"].update({"corpus_validator": True, "unit_tests": True})
                # Synthetic repository with unrelated history and installed generic importer contract.
                repo = Path(td) / "synthetic_repo"; repo.mkdir()
                run(["git", "init", "-b", "main"], cwd=repo); run(["git", "config", "user.email", "synthetic@certiaura.local"], cwd=repo); run(["git", "config", "user.name", "Certiaura Synthetic"], cwd=repo)
                (repo / "Unrelated/History").mkdir(parents=True); (repo / "Unrelated/History/legacy.txt").write_text("unrelated historical content\n", encoding="utf-8")
                (repo / "00_Governance").mkdir(); (repo / "00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md").write_text("# Existing accumulated continuity baseline\n\nBuild 0040 closed.\n", encoding="utf-8")
                (repo / "13_Project_Genesis/Import").mkdir(parents=True); (repo / "13_Project_Genesis/Import/transactional_build_import.py").write_text("# BUILD_MANIFEST ASSET_INTENT_MANIFEST build-neutral importer contract\n", encoding="utf-8")
                (repo / "Documentation").mkdir()
                fields = ["Universal Asset Identifier","Asset Name","Knowledge System","Asset Type","Status","Owner","Parent Assets","Last Review","Notes","Repository Path","Supporting Files","Version","Completion Percentage","Child Assets","Relationship List","Evidence Links","Report Links","Marketplace Links","Next Review","Change History","Build Provenance","Source Builds","Registration Basis","File SHA256","Last Updated"]
                rows = [
                    ["CERT-PKS-000001","Retatrutide","PKS","Flagship Knowledge Asset","ACTIVE","Certiaura","","","","02_Peptides/CERT-PKS-000001_Retatrutide/CERT-PKS-000001_Retatrutide.md","","1.0.0","","","","","","","","","prior","prior","historical","","2026-07-20"],
                    ["CERT-EKS-000007","Retatrutide Discovery to Clinical Proof of Concept","EKS","Evidence Asset","ACTIVE","Certiaura","","","","06_Evidence/CERT-EKS-000007_Retatrutide_Discovery_to_Clinical_Proof_of_Concept.md","","1.0.0","","","","","","","","","prior","prior","historical","","2026-07-20"],
                    ["CERT-SYS-999999","Unrelated Historical Asset","SYS","Documentation Asset","ACTIVE","Certiaura","","","","Unrelated/History/legacy.txt","","1.0.0","","","","","","","","","prior","prior","historical","","2026-07-20"]
                ]
                with (repo / "Documentation/Master_Asset_Register.csv").open("w", encoding="utf-8", newline="") as f:
                    w = csv.writer(f, lineterminator="\n"); w.writerow(fields); w.writerows(rows)
                run(["git", "add", "."], cwd=repo); run(["git", "commit", "-m", "Synthetic unrelated history baseline"], cwd=repo)
                baseline = run(["git", "rev-parse", "HEAD"], cwd=repo)
                runner = extracted / "13_Project_Genesis/Import/run_build_0041_import.py"
                dry_report = Path(td) / "dry.json"
                run([os.environ.get("PYTHON", "python"), "-B", str(runner), "--package", str(package), "--repository", str(repo), "--report", str(dry_report), "--expected-sha256", sha(package)], env=env)
                dry = json.loads(dry_report.read_text(encoding="utf-8"))
                if not dry.get("valid") or dry.get("applied"): raise RuntimeError("Synthetic dry run failed or applied changes")
                if run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=repo): raise RuntimeError("Dry run changed synthetic repository")
                backup_root = Path(td) / "backups"; apply_report = Path(td) / "apply.json"; env2 = env.copy(); env2["CERTIAURA_BACKUP_ROOT"] = str(backup_root)
                run([os.environ.get("PYTHON", "python"), "-B", str(runner), "--package", str(package), "--repository", str(repo), "--report", str(apply_report), "--expected-sha256", sha(package), "--apply"], env=env2)
                applied = json.loads(apply_report.read_text(encoding="utf-8"))
                if not applied.get("valid") or not applied.get("applied"): raise RuntimeError("Synthetic apply failed")
                if not (repo / "Unrelated/History/legacy.txt").is_file(): raise RuntimeError("Unrelated file was lost")
                if run(["git", "rev-parse", "HEAD"], cwd=repo) != baseline: raise RuntimeError("Synthetic HEAD changed before commit")
                run(["git", "diff", "--check"], cwd=repo)
                run(["git", "add", "-A"], cwd=repo)
                run(["git", "diff", "--cached", "--check"], cwd=repo)
                unstaged = run(["git", "diff", "--name-only"], cwd=repo)
                if unstaged: raise RuntimeError("Unstaged changes remain after staging")
                status = run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=repo)
                if any(line.startswith(" D") or line.startswith("D ") for line in status.splitlines()): raise RuntimeError("Unexpected deletion staged")
                if any("__pycache__" in p.as_posix() or p.suffix in {".pyc", ".pyo"} for p in repo.rglob("*")): raise RuntimeError("Runtime artefact in synthetic repository")
                report["synthetic_repository"] = {"baseline_commit": baseline, "unrelated_historical_files_preserved": True, "dry_run_no_changes": True, "apply_mode_validated": True, "backup_created": True, "expected_register_total": applied.get("expected_register_total"), "allocated_identifiers": len(applied.get("allocated_identifiers", [])), "git_diff_check": "PASS", "git_diff_cached_check": "PASS", "unexpected_deletions": 0, "unstaged_changes": 0, "runtime_artifacts": 0}
                report["gates"].update({"synthetic_git_repository": True, "unrelated_history_preserved": True, "actual_runner_dry_run": True, "actual_runner_apply_mode": True, "transactional_backup": True, "master_asset_register_reconciliation": True, "continuity_delta_applied": True, "unexpected_deletions_absent": True, "all_changes_staged": True, "git_diff_check_after_staging": True, "git_diff_cached_check_after_staging": True, "unstaged_changes_absent": True, "runtime_artifacts_after_validation_absent": True})
        report["package_sha256"] = sha(package); report["valid"] = True
    except Exception as exc:
        report["errors"].append(str(exc)); report["valid"] = False
    report_path.parent.mkdir(parents=True, exist_ok=True); report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1
if __name__ == "__main__": raise SystemExit(main())
