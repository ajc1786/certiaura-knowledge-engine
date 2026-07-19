\
from __future__ import annotations
import argparse, hashlib, json, shutil, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ALLOWED_ROOTS = {
    '00_Governance','01_Knowledge_Systems','02_Peptides','03_Biology','04_Conditions',
    '05_Monitoring','06_Evidence','07_Goals','08_Product_Passports','09_Cost_Intelligence',
    '10_Marketplace','11_Academy','12_Reports','13_Project_Genesis','Assets','Database',
    'Documentation','Images','Schemas','Scripts','Standards','Templates'
}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def validate_member(name: str) -> list[str]:
    errors=[]
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts: errors.append('UNSAFE_PATH')
    if not p.parts: errors.append('EMPTY_PATH')
    elif p.parts[0] not in ALLOWED_ROOTS: errors.append('UNAUTHORISED_ROOT')
    if any(x == '__pycache__' for x in p.parts) or name.endswith('.pyc'): errors.append('GENERATED_CACHE_FILE')
    return errors

def inspect_pack(zip_path: Path, repo: Path):
    plan=[]; errors=[]; seen_ci={}
    with zipfile.ZipFile(zip_path) as zf:
        files=[i for i in zf.infolist() if not i.is_dir()]
        roots={PurePosixPath(i.filename).parts[0] for i in files if PurePosixPath(i.filename).parts}
        if len(roots)==1 and next(iter(roots), '') not in ALLOWED_ROOTS:
            errors.append({'code':'BUILD_WRAPPER_FOLDER','message':'Top-level build wrapper detected'})
        for info in files:
            member_errors=validate_member(info.filename)
            if member_errors:
                errors.append({'code':','.join(member_errors),'path':info.filename})
                continue
            key=info.filename.lower()
            if key in seen_ci and seen_ci[key] != info.filename:
                errors.append({'code':'CASE_COLLISION','path':info.filename,'other':seen_ci[key]})
                continue
            seen_ci[key]=info.filename
            data=zf.read(info.filename); incoming=digest(data)
            target=repo.joinpath(*PurePosixPath(info.filename).parts)
            if not target.exists(): action='CREATE'
            elif target.is_dir(): action='BLOCK_DIRECTORY_COLLISION'
            else:
                current=digest(target.read_bytes())
                action='SKIP_IDENTICAL' if current==incoming else 'BLOCK_NONIDENTICAL_COLLISION'
            plan.append({'path':info.filename,'action':action,'sha256':incoming,'size_bytes':len(data)})
    return {'valid':not errors and not any(x['action'].startswith('BLOCK_') for x in plan), 'errors':errors, 'plan':plan}

def apply_pack(zip_path: Path, repo: Path, backup_root: Path):
    report=inspect_pack(zip_path,repo)
    if not report['valid']:
        return report
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup=backup_root/stamp; backup.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for item in report['plan']:
            if item['action']=='SKIP_IDENTICAL': continue
            target=repo.joinpath(*PurePosixPath(item['path']).parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(zf.read(item['path']))
    report['applied']=True; report['backup_path']=str(backup)
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('zip_path',type=Path); ap.add_argument('repo',type=Path)
    ap.add_argument('--apply',action='store_true'); ap.add_argument('--backup-root',type=Path)
    ap.add_argument('--report',type=Path)
    args=ap.parse_args()
    result=apply_pack(args.zip_path,args.repo,args.backup_root or args.repo/'.certiaura_backups') if args.apply else inspect_pack(args.zip_path,args.repo)
    text=json.dumps(result,indent=2); print(text)
    if args.report: args.report.write_text(text+'\n',encoding='utf-8')
    return 0 if result.get('valid') else 1
if __name__=='__main__': raise SystemExit(main())
