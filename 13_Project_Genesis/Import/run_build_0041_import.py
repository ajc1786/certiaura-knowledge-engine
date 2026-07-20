#!/usr/bin/env python3
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

BUILD_RECORD = "Documentation/Build_Records/0041"
REGISTER = "Documentation/Master_Asset_Register.csv"
CONTINUITY = "00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md"
REQUIRED_IMPORTER = "13_Project_Genesis/Import/transactional_build_import.py"
CHECKPOINT_BEGIN = "<!-- CERTIAURA_ACTIVE_CHECKPOINT_BEGIN -->"
CHECKPOINT_END = "<!-- CERTIAURA_ACTIVE_CHECKPOINT_END -->"

def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def git(repo: Path, *args: str) -> str:
    cp = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    if cp.returncode: raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
    return cp.stdout.strip()

def load_zip_json(zf: zipfile.ZipFile, name: str):
    return json.loads(zf.read(name).decode("utf-8"))

def safe_members(zf: zipfile.ZipFile) -> list[str]:
    names = []
    seen_case = set()
    for info in zf.infolist():
        if info.is_dir(): continue
        p = PurePosixPath(info.filename)
        if p.is_absolute() or ".." in p.parts or "\\" in info.filename: raise RuntimeError(f"Unsafe ZIP member: {info.filename}")
        key = info.filename.casefold()
        if key in seen_case: raise RuntimeError(f"Case collision or duplicate: {info.filename}")
        seen_case.add(key); names.append(info.filename)
    return sorted(names)

def read_register(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f); rows = list(reader); fields = reader.fieldnames or []
    if "Universal Asset Identifier" not in fields or "Repository Path" not in fields: raise RuntimeError("Master Asset Register structure is invalid")
    uais = [r.get("Universal Asset Identifier", "").strip() for r in rows]
    paths = [r.get("Repository Path", "").strip().replace("\\", "/") for r in rows]
    if any(not x for x in uais): raise RuntimeError("Blank UAI found in Master Asset Register")
    if len(uais) != len(set(uais)): raise RuntimeError("Duplicate UAI found in Master Asset Register")
    nonblank_paths = [x.casefold() for x in paths if x]
    if len(nonblank_paths) != len(set(nonblank_paths)): raise RuntimeError("Duplicate canonical path found in Master Asset Register")
    return fields, rows

def allocate(rows, system: str, reserved: set[str]) -> str:
    pat = re.compile(rf"^CERT-{re.escape(system)}-(\d+)$")
    nums = [int(m.group(1)) for r in rows if (m := pat.match(r.get("Universal Asset Identifier", "").strip()))]
    n = max(nums or [0]) + 1
    while f"CERT-{system}-{n:06d}" in reserved: n += 1
    value = f"CERT-{system}-{n:06d}"; reserved.add(value); return value

def checkpoint_block(title: str) -> str:
    return f"""{CHECKPOINT_BEGIN}\n## Active continuation checkpoint — Build 0041\n\n- Last closed build: **0040** at `6f4dfb11dfdc4b28fe736972864ec1acf1a1e056` (`ACTIONS_GREEN_CLOSED`).\n- Current build: **0041 — {title}**.\n- Current state after import: `IMPORTED` pending repository validation, commit, push and GitHub Actions green.\n- Immediate next action: run post-import validators, both Git diff checks, stage all package changes, confirm no deletions, residue or runtime artefacts, then commit and push using the locked message.\n- Closure gate: do not set `ACTIONS_GREEN_CLOSED` until Actions are green and the Build 0041 lessons-learned record is verified.\n- Following planned integrated package: Build 0042 — Retatrutide safety, monitoring, contraindication and clinical-outcome integration baseline.\n{CHECKPOINT_END}\n"""

def update_checkpoint(text: str, title: str) -> str:
    block = checkpoint_block(title)
    pattern = re.compile(re.escape(CHECKPOINT_BEGIN) + r".*?" + re.escape(CHECKPOINT_END) + r"\n?", re.S)
    if pattern.search(text): text = pattern.sub(block, text)
    else: text = text.rstrip() + "\n\n" + block
    return text.replace("\r\n", "\n").replace("\r", "\n")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True)
    ap.add_argument("--repository", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--expected-sha256")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    package = Path(args.package).resolve(); repo = Path(args.repository).resolve(); report_path = Path(args.report).resolve()
    report = {"build_number": "0041", "apply_requested": args.apply, "applied": False, "valid": False, "errors": [], "warnings": [], "allocated_identifiers": [], "files": []}
    try:
        if not package.is_file(): raise RuntimeError("Package not found")
        actual_sha = hash_file(package); report["package_sha256"] = actual_sha
        if args.expected_sha256 and actual_sha.lower() != args.expected_sha256.lower(): raise RuntimeError("Package SHA-256 mismatch")
        if not (repo / ".git").is_dir(): raise RuntimeError("Repository is not a Git repository")
        if git(repo, "status", "--porcelain", "--untracked-files=all"): raise RuntimeError("Repository is not clean")
        report["repository_head_before"] = git(repo, "rev-parse", "HEAD")
        importer = repo / REQUIRED_IMPORTER
        if not importer.is_file(): raise RuntimeError("Installed Project Genesis transactional importer is missing")
        importer_text = importer.read_text(encoding="utf-8", errors="replace")
        neutral_markers = ["BUILD_MANIFEST", "ASSET_INTENT_MANIFEST"]
        missing_markers = [x for x in neutral_markers if x not in importer_text]
        if missing_markers: raise RuntimeError(f"Installed importer does not expose build-neutral metadata markers: {missing_markers}")
        report["installed_importer_compatibility"] = {"path": REQUIRED_IMPORTER, "build_neutral_markers": True, "invocation_mode": "package-specific transactional runner using installed importer contract"}
        register_path = repo / REGISTER
        continuity_path = repo / CONTINUITY
        if not register_path.is_file(): raise RuntimeError("Canonical Master Asset Register is missing")
        if not continuity_path.is_file(): raise RuntimeError("Canonical continuity checkpoint is missing")
        fields, rows = read_register(register_path)
        with zipfile.ZipFile(package) as zf:
            members = safe_members(zf)
            manifest = load_zip_json(zf, f"{BUILD_RECORD}/BUILD_MANIFEST.json")
            intents = load_zip_json(zf, f"{BUILD_RECORD}/ASSET_INTENT_MANIFEST.json")
            inventory_text = zf.read(f"{BUILD_RECORD}/PACKAGE_INVENTORY.csv").decode("utf-8")
            inventory_paths = {r["path"] for r in csv.DictReader(io.StringIO(inventory_text))}
            if set(members) != inventory_paths: raise RuntimeError("Package inventory does not match ZIP members")
            if manifest.get("build_number") != "0041": raise RuntimeError("Incorrect build number")
            title = manifest.get("build_title", "")
            if not title: raise RuntimeError("Build title missing")
            declared = {x["path"] for x in intents.get("files", [])}
            if declared != set(members): raise RuntimeError("Asset Intent Manifest does not classify every package file")
            reserved = {r["Universal Asset Identifier"].strip() for r in rows}
            new_rows = []
            for asset in intents.get("formal_assets", []):
                if asset.get("intended_action") != "CREATE": continue
                uai = allocate(rows + new_rows, asset["knowledge_system"], reserved)
                report["allocated_identifiers"].append({"path": asset["repository_relative_path"], "allocated_uai": uai})
                row = {f: "" for f in fields}
                values = {
                    "Universal Asset Identifier": uai, "Asset Name": asset["asset_title"], "Knowledge System": asset["knowledge_system"],
                    "Asset Type": asset["asset_type"], "Status": asset.get("proposed_status", "ACTIVE"), "Owner": asset.get("owner", "Certiaura"),
                    "Repository Path": asset["repository_relative_path"], "Version": asset.get("proposed_version", "1.0.0"),
                    "Completion Percentage": str(asset.get("completion_percentage", 100)), "Build Provenance": "CERT-BUILD-0041",
                    "Source Builds": "0041", "Registration Basis": "ASSET_INTENT_MANIFEST", "Last Updated": "2026-07-20"
                }
                for k, v in values.items():
                    if k in row: row[k] = v
                new_rows.append(row)
            report["formal_asset_count"] = len(intents.get("formal_assets", []))
            report["expected_register_total"] = len(rows) + len(new_rows)
            report["package_file_count"] = len(members)
            report["apply_allowed"] = True
            if not args.apply:
                report["valid"] = True; report["transaction_status"] = "DRY_RUN_VALIDATED"
            else:
                backup_root = Path(os.environ.get("CERTIAURA_BACKUP_ROOT", "")).resolve() if os.environ.get("CERTIAURA_BACKUP_ROOT") else None
                if not backup_root: raise RuntimeError("CERTIAURA_BACKUP_ROOT is required for apply mode")
                backup = backup_root / f"Build_0041_Pre_Import_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
                backup.mkdir(parents=True, exist_ok=False)
                created = []; backed = []
                try:
                    # Backup register and continuity, then target files that already exist.
                    for rel in [REGISTER, CONTINUITY]:
                        src = repo / rel; dst = backup / "files" / rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst); backed.append(rel)
                    for rel in members:
                        target = repo / PurePosixPath(rel)
                        if target.exists():
                            dst = backup / "files" / PurePosixPath(rel); dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(target, dst); backed.append(rel)
                    for rel in members:
                        target = repo / PurePosixPath(rel); target.parent.mkdir(parents=True, exist_ok=True)
                        if not target.exists(): created.append(rel)
                        target.write_bytes(zf.read(rel)); report["files"].append({"path": rel, "action": "WRITE"})
                    # Register reconciliation.
                    with register_path.open("w", encoding="utf-8", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows + new_rows)
                    # Continuity delta is applied without replacing the accumulated baseline.
                    current = continuity_path.read_text(encoding="utf-8")
                    continuity_path.write_text(update_checkpoint(current, title), encoding="utf-8", newline="\n")
                    report["backup_path"] = str(backup)
                    report["backup_files"] = sorted(set(backed))
                    report["created_files"] = created
                    report["applied"] = True; report["valid"] = True; report["transaction_status"] = "APPLIED_PENDING_POST_IMPORT_VALIDATION"
                except Exception:
                    for rel in created:
                        p = repo / PurePosixPath(rel)
                        if p.exists(): p.unlink()
                    for rel in backed:
                        src = backup / "files" / PurePosixPath(rel); dst = repo / PurePosixPath(rel); dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
                    raise
        report["repository_head_after"] = git(repo, "rev-parse", "HEAD")
        if report["repository_head_after"] != report["repository_head_before"]: raise RuntimeError("Repository HEAD changed during import")
    except Exception as exc:
        report["errors"].append(str(exc)); report["valid"] = False
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1
if __name__ == "__main__": raise SystemExit(main())
