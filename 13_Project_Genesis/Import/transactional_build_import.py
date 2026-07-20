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
from pathlib import Path, PurePosixPath
from typing import Any

ALLOWED_ROOTS={"00_Governance","01_Knowledge_Systems","02_Peptides","03_Biology","04_Conditions","05_Monitoring","06_Evidence","07_Goals","08_Product_Passports","09_Cost_Intelligence","10_Marketplace","11_Academy","12_Reports","13_Project_Genesis","Assets","Database","Documentation","Images","Schemas","Scripts","Standards","Templates"}
BUILD_RECORD="Documentation/Build_Records/0039"
APPROVED_REPLACEMENTS={"00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md","13_Project_Genesis/Import/transactional_build_import.py"}
REGISTER_UAI="Universal Asset Identifier"
REGISTER_PATH="Repository Path"


def utc_now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def sha256_bytes(data: bytes): return hashlib.sha256(data).hexdigest()
def sha256_file(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def norm_rel(path: str):
    p=PurePosixPath(path.replace("\\","/"))
    if p.is_absolute() or ".." in p.parts or not p.parts: raise ValueError(f"Unsafe package path: {path}")
    return p.as_posix()
def safe_repo_path(repo: Path, rel: str):
    rel=norm_rel(rel); target=(repo/Path(*PurePosixPath(rel).parts)).resolve(); base=repo.resolve()
    try: target.relative_to(base)
    except ValueError as exc: raise ValueError(f"Path escapes repository: {rel}") from exc
    return target

def load_manifest(zf: zipfile.ZipFile):
    name=f"{BUILD_RECORD}/ASSET_INTENT_MANIFEST.json"
    try: return json.loads(zf.read(name).decode("utf-8"))
    except KeyError as exc: raise ValueError(f"Missing {name}") from exc

def inspect_package(zf: zipfile.ZipFile):
    names=[]; lower={}; collisions=[]
    for info in zf.infolist():
        if info.is_dir(): continue
        name=norm_rel(info.filename); names.append(name)
        key=name.casefold()
        if key in lower and lower[key]!=name: collisions.append([lower[key],name])
        lower[key]=name
    roots=sorted({PurePosixPath(n).parts[0] for n in names})
    unauthorized=sorted(set(roots)-ALLOWED_ROOTS)
    wrapper=bool(len(roots)==1 and (roots[0].lower().startswith("certiaura_build_") or roots[0].lower().startswith("build_")))
    return names,roots,unauthorized,wrapper,collisions

def read_register(path: Path):
    if not path.exists(): raise ValueError(f"Master Asset Register missing: {path}")
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f); rows=list(reader); fields=reader.fieldnames or []
    if REGISTER_UAI not in fields or REGISTER_PATH not in fields: raise ValueError("Master Asset Register missing required columns")
    uais=[r.get(REGISTER_UAI,"").strip() for r in rows if r.get(REGISTER_UAI,"").strip()]
    paths=[r.get(REGISTER_PATH,"").strip().replace("\\","/") for r in rows if r.get(REGISTER_PATH,"").strip()]
    if len(uais)!=len(set(uais)): raise ValueError("Master Asset Register contains duplicate Universal Asset Identifiers")
    if len([p.casefold() for p in paths])!=len(set(p.casefold() for p in paths)): raise ValueError("Master Asset Register contains duplicate repository paths")
    return fields,rows

def write_register(path: Path, fields: list[str], rows: list[dict[str,str]]):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n"); w.writeheader(); w.writerows(rows)

def reconcile_register(fields, rows, formal_assets):
    by_uai={r.get(REGISTER_UAI,"").strip():r for r in rows if r.get(REGISTER_UAI,"").strip()}
    by_path={r.get(REGISTER_PATH,"").strip().replace("\\","/").casefold():r for r in rows if r.get(REGISTER_PATH,"").strip()}
    changes=[]
    for asset in formal_assets:
        rel=asset["repository_path"]; action=asset["intended_action"]
        uai=(asset.get("existing_uai") or asset.get("proposed_uai") or "").strip()
        target=by_uai.get(uai) or by_path.get(rel.casefold())
        if action=="UPDATE":
            if target is None: raise ValueError(f"UPDATE formal asset not found in Master Asset Register: {rel} / {uai}")
        elif action=="CREATE":
            if target is not None: raise ValueError(f"CREATE formal asset conflicts with existing register identity: {rel} / {uai}")
            target={field:"" for field in fields}; rows.append(target)
        else: raise ValueError(f"Unsupported intended_action for Build 0039: {action}")
        mapping={
            "Universal Asset Identifier":uai,
            "Asset Name":asset.get("asset_title",""),
            "Knowledge System":asset.get("knowledge_system",""),
            "Asset Type":asset.get("asset_type",""),
            "Status":asset.get("proposed_status","ACTIVE"),
            "Owner":asset.get("owner","Certiaura"),
            "Repository Path":rel,
            "Version":asset.get("proposed_version",""),
            "Completion Percentage":str(asset.get("completion_percentage",100)),
            "Last Review":asset.get("last_review",""),
            "Next Review":asset.get("next_review",""),
            "Build Provenance":";".join(asset.get("build_provenance",[])),
            "Source Builds":";".join(asset.get("source_builds",[])),
            "Registration Basis":asset.get("registration_basis","BUILD_IMPORT")
        }
        for key,val in mapping.items():
            if key in fields: target[key]=val
        by_uai[uai]=target; by_path[rel.casefold()]=target
        changes.append({"path":rel,"uai":uai,"action":action})
    return rows,changes

def ensure_parent(target: Path, repo: Path, created_dirs: list[str]):
    missing=[]; cur=target.parent
    while cur!=repo and not cur.exists(): missing.append(cur); cur=cur.parent
    for directory in reversed(missing):
        directory.mkdir()
        created_dirs.append(directory.relative_to(repo).as_posix())

def safe_remove_empty_directories(repo: Path, created_directories: list[str], actions: list[dict[str,Any]]):
    """Remove only transaction-created directories that are proven empty. Never recursive."""
    unique=sorted(set(created_directories),key=lambda p:len(PurePosixPath(p).parts),reverse=True)
    for rel in unique:
        try: directory=safe_repo_path(repo,rel)
        except Exception as exc:
            actions.append({"path":rel,"action":"SKIP_DIRECTORY","reason":str(exc)}); continue
        if not directory.exists(): actions.append({"path":rel,"action":"DIRECTORY_ALREADY_ABSENT"}); continue
        if not directory.is_dir(): actions.append({"path":rel,"action":"SKIP_DIRECTORY","reason":"not_a_directory"}); continue
        try: empty=next(directory.iterdir(),None) is None
        except OSError as exc:
            actions.append({"path":rel,"action":"SKIP_DIRECTORY","reason":f"cannot_prove_empty:{exc}"}); continue
        if not empty:
            actions.append({"path":rel,"action":"PRESERVE_NONEMPTY_DIRECTORY"}); continue
        try:
            directory.rmdir()
            actions.append({"path":rel,"action":"REMOVE_EMPTY_TRANSACTION_DIRECTORY"})
        except OSError as exc:
            actions.append({"path":rel,"action":"SKIP_DIRECTORY","reason":f"rmdir_failed:{exc}"})

def recover_transaction(repo: Path, journal: dict[str,Any], apply: bool=True):
    actions=[]; backup=Path(journal["backup_root"])
    for item in reversed(journal.get("created_files",[])):
        rel=item["path"]; target=safe_repo_path(repo,rel)
        if not target.exists(): actions.append({"path":rel,"action":"FILE_ALREADY_ABSENT"}); continue
        current=sha256_file(target); expected=item.get("applied_sha256")
        if expected and current!=expected:
            actions.append({"path":rel,"action":"PRESERVE_CHANGED_CREATED_FILE","current_sha256":current}); continue
        if apply: target.unlink()
        actions.append({"path":rel,"action":"REMOVE_TRANSACTION_CREATED_FILE" if apply else "WOULD_REMOVE_TRANSACTION_CREATED_FILE"})
    for item in journal.get("replaced_files",[]):
        rel=item["path"]; source=backup/item["backup_rel"]; target=safe_repo_path(repo,rel)
        if not source.exists(): actions.append({"path":rel,"action":"RESTORE_FAILED","reason":"backup_missing"}); continue
        if apply:
            target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
        actions.append({"path":rel,"action":"RESTORE_REPLACED_FILE" if apply else "WOULD_RESTORE_REPLACED_FILE"})
    if apply: safe_remove_empty_directories(repo,journal.get("created_directories",[]),actions)
    else:
        for rel in journal.get("created_directories",[]): actions.append({"path":rel,"action":"WOULD_REMOVE_ONLY_IF_EMPTY_AND_TRANSACTION_CREATED"})
    return {"valid":True,"applied":apply,"actions":actions,"recursive_directory_deletion_used":False}

def write_json_report(repo: Path, report_arg: str, data: dict[str,Any]):
    report=Path(report_arg)
    if not report.is_absolute(): report=safe_repo_path(repo,report_arg)
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

def external_backup_root(repo: Path, build_number: str):
    parents=list(repo.resolve().parents)
    certiaura_root=parents[1] if len(parents)>1 else repo.parent
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    root=certiaura_root/"Backups"/f"Build_{build_number}_Pre_Import_{stamp}"
    root.mkdir(parents=True,exist_ok=False)
    return root

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("zip_path"); p.add_argument("repository_path"); p.add_argument("--apply",action="store_true"); p.add_argument("--asset-register",default="Documentation/Master_Asset_Register.csv"); p.add_argument("--report",default=f"{BUILD_RECORD}/GUIDED_DRY_RUN_REPORT.json")
    args=p.parse_args(argv); repo=Path(args.repository_path).resolve(); zpath=Path(args.zip_path).resolve(); errors=[]; warnings=[]
    report={"schema_version":"2.1.0","generated_at":utc_now(),"build_number":"0039","build_title":"evidence ingestion citation management living evidence surveillance and scientific review controls","package_version":"1.3.2","zip_path":str(zpath),"repository_path":str(repo),"apply_requested":args.apply}
    try:
        if not repo.is_dir(): raise ValueError("Repository path is not a directory")
        reg=safe_repo_path(repo,args.asset_register); fields,rows=read_register(reg)
        with zipfile.ZipFile(zpath) as zf:
            names,roots,unauthorized,wrapper,case_collisions=inspect_package(zf); manifest=load_manifest(zf)
            declared={f["repository_path"]:f for f in manifest.get("files",[])}
            unclassified=sorted(set(names)-set(declared)); missing=sorted(set(declared)-set(names))
            if unauthorized: errors.append({"code":"UNAUTHORISED_ROOTS","roots":unauthorized})
            if wrapper: errors.append({"code":"WRAPPER_FOLDER_DETECTED"})
            if case_collisions: errors.append({"code":"CASE_COLLISIONS","paths":case_collisions})
            if unclassified: errors.append({"code":"UNCLASSIFIED_PACKAGE_FILES","paths":unclassified})
            if missing: errors.append({"code":"DECLARED_FILES_MISSING","paths":missing})
            if manifest.get("package_version")!="1.3.2": errors.append({"code":"PACKAGE_VERSION_MISMATCH"})
            file_actions=[]; conflicts=[]
            for name in names:
                incoming=zf.read(name); target=safe_repo_path(repo,name); inc_hash=sha256_bytes(incoming)
                if not target.exists(): action="CREATE_FILE"
                elif target.is_dir(): action="REJECT_PATH_IS_DIRECTORY"; conflicts.append(name)
                else:
                    current=sha256_file(target)
                    if current==inc_hash: action="SKIP_IDENTICAL"
                    elif name in APPROVED_REPLACEMENTS: action="APPROVED_REPLACEMENT"
                    else: action="BLOCK_NONIDENTICAL_EXISTING"; conflicts.append(name)
                file_actions.append({"path":name,"classification":declared.get(name,{}).get("classification"),"action":action,"incoming_sha256":inc_hash})
            formal=[dict(f) for f in manifest.get("files",[]) if f.get("classification")=="FORMAL_ASSET"]
            proposed_rows,reg_changes=reconcile_register(fields,[dict(r) for r in rows],formal)
            report.update({"asset_manifest_path":f"{BUILD_RECORD}/ASSET_INTENT_MANIFEST.json","package_file_count":len(names),"formal_asset_count":len(formal),"roots":roots,"wrapper_folder_detected":wrapper,"unauthorised_roots":unauthorized,"case_collisions":case_collisions,"file_actions":file_actions,"assets_to_create":[c for c in reg_changes if c["action"]=="CREATE"],"assets_to_update":[c for c in reg_changes if c["action"]=="UPDATE"],"expected_register_total":len(proposed_rows),"conflicts":conflicts})
            if conflicts: errors.append({"code":"UNRESOLVED_FILE_CONFLICTS","paths":conflicts})
            report["errors"]=errors; report["warnings"]=warnings; report["valid"]=not errors; report["apply_allowed"]=not errors
            if args.apply and not errors:
                backup=external_backup_root(repo,"0039"); journal={"schema_version":"1.1.0","build_number":"0039","package_version":"1.3.2","repository_path":str(repo),"backup_root":str(backup),"created_files":[],"replaced_files":[],"created_directories":[],"created_at":utc_now()}
                reg_backup=backup/args.asset_register; reg_backup.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(reg,reg_backup)
                journal["replaced_files"].append({"path":args.asset_register,"backup_rel":args.asset_register})
                try:
                    for action in file_actions:
                        if action["action"]=="SKIP_IDENTICAL": continue
                        rel=action["path"]; target=safe_repo_path(repo,rel); ensure_parent(target,repo,journal["created_directories"])
                        if target.exists():
                            b=backup/"files"/Path(*PurePosixPath(rel).parts); b.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(target,b); journal["replaced_files"].append({"path":rel,"backup_rel":b.relative_to(backup).as_posix()})
                        else: journal["created_files"].append({"path":rel,"applied_sha256":action["incoming_sha256"]})
                        target.write_bytes(zf.read(rel))
                    write_register(reg,fields,proposed_rows)
                    # post-apply validation
                    for action in file_actions:
                        target=safe_repo_path(repo,action["path"])
                        if not target.is_file() or sha256_file(target)!=action["incoming_sha256"]: raise RuntimeError(f"Post-apply hash validation failed: {action['path']}")
                    read_register(reg)
                    journal_path=backup/"TRANSACTION_JOURNAL.json"; journal_path.write_text(json.dumps(journal,indent=2)+"\n",encoding="utf-8")
                    report.update({"applied":True,"transaction_status":"APPLIED_VALIDATED","backup_root":str(backup),"transaction_journal":str(journal_path),"recovery_safety":{"recursive_directory_deletion_used":False,"empty_only_directory_cleanup":True,"transaction_created_directories_only":True}})
                except Exception as exc:
                    journal_path=backup/"TRANSACTION_JOURNAL.json"; journal_path.write_text(json.dumps(journal,indent=2)+"\n",encoding="utf-8")
                    recovery=recover_transaction(repo,journal,apply=True)
                    report.update({"applied":False,"transaction_status":"FAILED_ROLLED_BACK","apply_error":str(exc),"backup_root":str(backup),"transaction_journal":str(journal_path),"recovery":recovery})
                    report["valid"]=False; report["errors"].append({"code":"APPLY_FAILED_ROLLED_BACK","message":str(exc)})
            else: report["applied"]=False
    except Exception as exc:
        report.update({"valid":False,"apply_allowed":False,"applied":False}); report.setdefault("errors",[]).append({"code":"IMPORTER_EXCEPTION","message":str(exc)})
    write_json_report(repo,args.report,report)
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report.get("valid") else 1

if __name__=="__main__": raise SystemExit(main())
