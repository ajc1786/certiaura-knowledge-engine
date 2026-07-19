from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from asset_register_reconciler import reconcile, resolve_register, RegisterError, norm_path, load_register, _write_register

ALLOWED_ROOTS = {
    '00_Governance','01_Knowledge_Systems','02_Peptides','03_Biology','04_Conditions',
    '05_Monitoring','06_Evidence','07_Goals','08_Product_Passports','09_Cost_Intelligence',
    '10_Marketplace','11_Academy','12_Reports','13_Project_Genesis','Assets','Database',
    'Documentation','Images','Schemas','Scripts','Standards','Templates'
}
MANIFEST_PATH = 'Documentation/Build_Records/0038/ASSET_INTENT_MANIFEST.json'
CONFLICT_PATH = 'Documentation/Build_Records/0038/CONFLICT_POLICY.json'


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_member(name: str) -> list[str]:
    p = PurePosixPath(name)
    errors: list[str] = []
    if p.is_absolute() or '..' in p.parts:
        errors.append('UNSAFE_PATH')
    if not p.parts:
        errors.append('EMPTY_PATH')
    elif p.parts[0] not in ALLOWED_ROOTS:
        errors.append('UNAUTHORISED_ROOT')
    if any(x == '__pycache__' for x in p.parts) or name.endswith('.pyc'):
        errors.append('GENERATED_CACHE_FILE')
    return errors


def load_policy(zf: zipfile.ZipFile) -> dict:
    if CONFLICT_PATH not in zf.namelist():
        return {'approved_replacements': []}
    return json.loads(zf.read(CONFLICT_PATH))


def inspect_pack(zip_path: Path, repo: Path, asset_register: Path | None = None) -> dict:
    errors: list[dict] = []
    plan: list[dict] = []
    seen_ci: dict[str, str] = {}
    with zipfile.ZipFile(zip_path) as zf:
        files = [i for i in zf.infolist() if not i.is_dir()]
        if not files:
            errors.append({'code': 'EMPTY_PACKAGE'})
        roots = {PurePosixPath(i.filename).parts[0] for i in files if PurePosixPath(i.filename).parts}
        if len(roots) == 1 and next(iter(roots), '') not in ALLOWED_ROOTS:
            errors.append({'code': 'BUILD_WRAPPER_FOLDER'})
        if MANIFEST_PATH not in zf.namelist():
            errors.append({'code': 'ASSET_INTENT_MANIFEST_MISSING', 'path': MANIFEST_PATH})
            manifest = {'file_classifications': [], 'formal_assets': [], 'build_number': '0038'}
        else:
            manifest = json.loads(zf.read(MANIFEST_PATH))
        classified = {x['path'] for x in manifest.get('file_classifications', [])}
        policy = load_policy(zf)
        approved = {x['path']: x for x in policy.get('approved_replacements', [])}
        for info in files:
            member_errors = validate_member(info.filename)
            if member_errors:
                errors.append({'code': ','.join(member_errors), 'path': info.filename})
                continue
            key = info.filename.lower()
            if key in seen_ci and seen_ci[key] != info.filename:
                errors.append({'code': 'CASE_COLLISION', 'path': info.filename, 'other': seen_ci[key]})
                continue
            seen_ci[key] = info.filename
            if info.filename not in classified:
                errors.append({'code': 'UNCLASSIFIED_PACKAGE_FILE', 'path': info.filename})
            data = zf.read(info.filename)
            incoming = sha256_bytes(data)
            target = repo.joinpath(*PurePosixPath(info.filename).parts)
            if not target.exists():
                action = 'CREATE'
            elif target.is_dir():
                action = 'BLOCK_DIRECTORY_COLLISION'
            else:
                current = sha256_bytes(target.read_bytes())
                if current == incoming:
                    action = 'SKIP_IDENTICAL'
                elif info.filename in approved:
                    action = 'APPROVED_REPLACE'
                else:
                    action = 'BLOCK_NONIDENTICAL_COLLISION'
            plan.append({'path': info.filename, 'action': action, 'sha256': incoming, 'size_bytes': len(data)})

        # Extract manifest to a temporary path for reconciliation planning.
        register_report = None
        try:
            with tempfile.TemporaryDirectory() as td:
                mp = Path(td) / 'manifest.json'
                mp.write_text(json.dumps(manifest), encoding='utf-8')
                register_report = reconcile(repo, mp, asset_register, apply=False)
        except Exception as exc:
            errors.append({'code': 'MASTER_ASSET_REGISTER_PREFLIGHT_FAILED', 'message': str(exc)})

    blocked = [x for x in plan if x['action'].startswith('BLOCK_')]
    return {
        'valid': not errors and not blocked and bool(register_report and register_report.get('valid')),
        'errors': errors,
        'routing_plan': plan,
        'asset_register_change_report': register_report,
        'summary': {
            'files': len(plan),
            'create': sum(1 for x in plan if x['action'] == 'CREATE'),
            'skip_identical': sum(1 for x in plan if x['action'] == 'SKIP_IDENTICAL'),
            'approved_replace': sum(1 for x in plan if x['action'] == 'APPROVED_REPLACE'),
            'blocked': len(blocked),
        }
    }


def _backup(repo: Path, paths: list[str], register: Path, backup_root: Path) -> tuple[Path, dict]:
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = backup_root / f'build_0038_{stamp}'
    backup.mkdir(parents=True, exist_ok=False)
    manifest = {'created_at': stamp, 'files': []}
    all_paths = list(dict.fromkeys(paths + [str(register.relative_to(repo)).replace('\\', '/')]))
    for rel in all_paths:
        target = repo.joinpath(*PurePosixPath(rel).parts)
        entry = {'path': rel, 'existed': target.is_file()}
        if target.is_file():
            dest = backup.joinpath(*PurePosixPath(rel).parts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, dest)
            entry['sha256'] = sha256_bytes(target.read_bytes())
        manifest['files'].append(entry)
    (backup / 'ROLLBACK_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return backup, manifest


def _rollback(repo: Path, backup: Path, backup_manifest: dict) -> None:
    for entry in reversed(backup_manifest['files']):
        target = repo.joinpath(*PurePosixPath(entry['path']).parts)
        if entry['existed']:
            source = backup.joinpath(*PurePosixPath(entry['path']).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        elif target.exists() and target.is_file():
            target.unlink()


def _validate_repo(repo: Path, manifest: dict, register_report: dict) -> list[dict]:
    errors: list[dict] = []
    for item in manifest.get('formal_assets', []):
        target = repo.joinpath(*PurePosixPath(item['repository_path']).parts)
        if not target.is_file():
            errors.append({'code': 'ORPHAN_FORMAL_ASSET', 'path': item['repository_path']})
    # Validate touched JSON and Python files.
    for item in manifest.get('file_classifications', []):
        path = item['path']
        target = repo.joinpath(*PurePosixPath(path).parts)
        if not target.is_file():
            continue
        try:
            if target.suffix.lower() == '.json':
                json.loads(target.read_text(encoding='utf-8'))
            elif target.suffix.lower() == '.py':
                compile(target.read_text(encoding='utf-8'), str(target), 'exec')
        except Exception as exc:
            errors.append({'code': 'POST_IMPORT_FILE_VALIDATION_FAILED', 'path': path, 'message': str(exc)})
    if not register_report.get('valid'):
        errors.append({'code': 'ASSET_REGISTER_RECONCILIATION_INVALID'})
    return errors


def _advance_checkpoint(repo: Path) -> None:
    path = repo / '00_Governance' / 'CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md'
    if not path.is_file():
        raise RuntimeError('CONTINUITY_CHECKPOINT_MISSING_AFTER_IMPORT')
    text = path.read_text(encoding='utf-8')
    text = text.replace('**Version:** 1.2.0', '**Version:** 1.2.1', 1)
    text = text.replace('"version": "1.2.0"', '"version": "1.2.1"', 1)
    text = text.replace(
        '**Checkpoint status:** BUILD 0038 DELIVERED — TRANSACTIONAL IMPORT PENDING',
        '**Checkpoint status:** BUILD 0038 IMPORTED AND REPOSITORY VALIDATED — COMMIT/PUSH PENDING',
        1,
    )
    text = text.replace(
        'Import corrected Build 0038 through the transactional Project Genesis importer, review the dry-run routing and Asset Register Change Reports, then apply and validate.',
        'Commit and push corrected Build 0038 using the locked commit message, then confirm GitHub Actions green.',
        1,
    )
    text = text.replace('"required_action": "IMPORT_TRANSACTIONALLY"', '"required_action": "COMMIT_PUSH_CONFIRM_ACTIONS"', 1)
    text = text.replace(
        '"immediate_next_action": "Import corrected Build 0038 transactionally, review dry-run reports, reconcile the Master Asset Register and validate the repository"',
        '"immediate_next_action": "Commit and push corrected Build 0038 and confirm GitHub Actions green"',
        1,
    )
    path.write_text(text, encoding='utf-8')



def _sync_checkpoint_register_version(register: Path) -> None:
    rows, meta = load_register(register)
    wanted = norm_path('00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md')
    matches = [row for row in rows if norm_path(row.get('Repository Path')) == wanted]
    if len(matches) != 1:
        raise RuntimeError(f'CHECKPOINT_ASSET_REGISTER_MATCH_INVALID: {len(matches)}')
    matches[0]['Version'] = '1.2.1'
    matches[0]['Status'] = 'LOCKED_ACTIVE'
    _write_register(register, rows, meta)

def apply_pack(zip_path: Path, repo: Path, backup_root: Path, asset_register: Path | None = None) -> dict:
    preflight = inspect_pack(zip_path, repo, asset_register)
    if not preflight['valid']:
        preflight['applied'] = False
        return preflight
    register = resolve_register(repo, asset_register)
    touched = [x['path'] for x in preflight['routing_plan'] if x['action'] in {'CREATE', 'APPROVED_REPLACE'}]
    backup, backup_manifest = _backup(repo, touched, register, backup_root)
    try:
        with zipfile.ZipFile(zip_path) as zf:
            for item in preflight['routing_plan']:
                if item['action'] not in {'CREATE', 'APPROVED_REPLACE'}:
                    continue
                target = repo.joinpath(*PurePosixPath(item['path']).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(item['path']))
        manifest_path = repo / MANIFEST_PATH
        register_report_path = repo / 'Documentation/Build_Records/0038/ASSET_REGISTER_CHANGE_REPORT.json'
        register_report = reconcile(repo, manifest_path, asset_register, apply=True, report_path=register_report_path)
        validation_errors = _validate_repo(repo, json.loads(manifest_path.read_text(encoding='utf-8')), register_report)
        if validation_errors:
            raise RuntimeError(json.dumps(validation_errors))
        _advance_checkpoint(repo)
        _sync_checkpoint_register_version(register)
        report = {
            **preflight,
            'applied': True,
            'backup_path': str(backup),
            'asset_register_change_report': register_report,
            'post_import_validation': {'valid': True, 'errors': []},
        }
        report_path = repo / 'Documentation/Build_Records/0038/IMPORT_REPORT.json'
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        return report
    except Exception as exc:
        _rollback(repo, backup, backup_manifest)
        preflight['applied'] = False
        preflight['rolled_back'] = True
        preflight['runtime_error'] = str(exc)
        return preflight


def main() -> int:
    parser = argparse.ArgumentParser(description='Transactional Certiaura Build 0038 importer')
    parser.add_argument('zip_path', type=Path)
    parser.add_argument('repository', type=Path)
    parser.add_argument('--asset-register', type=Path)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--backup-root', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = apply_pack(args.zip_path, args.repository, args.backup_root or args.repository / '.certiaura_backups', args.asset_register) if args.apply else inspect_pack(args.zip_path, args.repository, args.asset_register)
    output = json.dumps(result, indent=2)
    print(output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + '\n', encoding='utf-8')
    return 0 if result.get('valid') and (not args.apply or result.get('applied')) else 1


if __name__ == '__main__':
    raise SystemExit(main())
