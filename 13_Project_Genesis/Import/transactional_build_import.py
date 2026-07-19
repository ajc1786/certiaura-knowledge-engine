from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from asset_register_reconciler import (
    CANONICAL_REGISTER_RELATIVE_PATH,
    UAI_RE,
    _write_register,
    load_register,
    norm_path,
    resolve_register,
)
from historical_asset_backfill import reconcile_full_historical_repository
from repair_master_asset_register import verify as verify_master_asset_register

ALLOWED_ROOTS = {
    '00_Governance','01_Knowledge_Systems','02_Peptides','03_Biology','04_Conditions',
    '05_Monitoring','06_Evidence','07_Goals','08_Product_Passports','09_Cost_Intelligence',
    '10_Marketplace','11_Academy','12_Reports','13_Project_Genesis','Assets','Database',
    'Documentation','Images','Schemas','Scripts','Standards','Templates'
}
MANIFEST_PATH = 'Documentation/Build_Records/0038/ASSET_INTENT_MANIFEST.json'
CONFLICT_PATH = 'Documentation/Build_Records/0038/CONFLICT_POLICY.json'
POLICY_PATH = 'Documentation/Build_Records/0038/HISTORICAL_ASSET_BACKFILL_POLICY.json'
FULL_REPORT_PATH = 'Documentation/Build_Records/0038/FULL_HISTORICAL_ASSET_REGISTER_REPORT.json'
CENSUS_REPORT_PATH = 'Documentation/Build_Records/0038/HISTORICAL_ASSET_CENSUS_REPORT.json'
BUTTON_VERIFY_PATH = 'Documentation/Build_Records/0038/MASTER_ASSET_REGISTER_BUTTON_VERIFICATION.json'


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
    asset_register = asset_register or CANONICAL_REGISTER_RELATIVE_PATH
    errors: list[dict] = []
    plan: list[dict] = []
    seen_ci: dict[str, str] = {}
    historical_report = None

    with zipfile.ZipFile(zip_path) as zf:
        files = [i for i in zf.infolist() if not i.is_dir()]
        incoming_files = {i.filename: zf.read(i.filename) for i in files}
        if not files:
            errors.append({'code': 'EMPTY_PACKAGE'})
        roots = {PurePosixPath(i.filename).parts[0] for i in files if PurePosixPath(i.filename).parts}
        if len(roots) == 1 and next(iter(roots), '') not in ALLOWED_ROOTS:
            errors.append({'code': 'BUILD_WRAPPER_FOLDER'})

        if MANIFEST_PATH not in incoming_files:
            errors.append({'code': 'ASSET_INTENT_MANIFEST_MISSING', 'path': MANIFEST_PATH})
            manifest = {'file_classifications': [], 'formal_assets': [], 'build_number': '0038'}
        else:
            manifest = json.loads(incoming_files[MANIFEST_PATH])
        if POLICY_PATH not in incoming_files:
            errors.append({'code': 'HISTORICAL_ASSET_BACKFILL_POLICY_MISSING', 'path': POLICY_PATH})

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
            data = incoming_files[info.filename]
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

        try:
            with tempfile.TemporaryDirectory() as td:
                td_path = Path(td)
                manifest_path = td_path / 'asset_intent_manifest.json'
                policy_path = td_path / 'historical_policy.json'
                manifest_path.write_bytes(incoming_files.get(MANIFEST_PATH, b'{}'))
                policy_path.write_bytes(incoming_files.get(POLICY_PATH, b'{}'))
                historical_report = reconcile_full_historical_repository(
                    repo,
                    manifest_path,
                    policy_path,
                    asset_register,
                    additional_files=incoming_files,
                    apply=False,
                )
        except Exception as exc:
            errors.append({'code': 'FULL_HISTORICAL_ASSET_REGISTER_PREFLIGHT_FAILED', 'message': str(exc)})

    blocked = [x for x in plan if x['action'].startswith('BLOCK_')]
    return {
        'valid': not errors and not blocked and bool(historical_report and historical_report.get('valid')),
        'errors': errors,
        'routing_plan': plan,
        'full_historical_asset_register_report': historical_report,
        'summary': {
            'files': len(plan),
            'create': sum(1 for x in plan if x['action'] == 'CREATE'),
            'skip_identical': sum(1 for x in plan if x['action'] == 'SKIP_IDENTICAL'),
            'approved_replace': sum(1 for x in plan if x['action'] == 'APPROVED_REPLACE'),
            'blocked': len(blocked),
            'historical_registerable_assets': (
                historical_report.get('summary', {}).get('registerable_assets', 0)
                if historical_report else 0
            ),
            'historical_register_creates': (
                historical_report.get('summary', {}).get('register_creates', 0)
                if historical_report else 0
            ),
            'historical_register_updates': (
                historical_report.get('summary', {}).get('register_updates', 0)
                if historical_report else 0
            ),
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


def _validate_repo(repo: Path, manifest: dict, historical_report: dict) -> list[dict]:
    errors: list[dict] = []
    for item in historical_report.get('census', {}).get('registerable_assets', []):
        target = repo.joinpath(*PurePosixPath(item['repository_path']).parts)
        if not target.is_file():
            errors.append({'code': 'ORPHAN_REGISTERABLE_HISTORICAL_ASSET', 'path': item['repository_path']})
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
    if not historical_report.get('valid') or not historical_report.get('applied'):
        errors.append({'code': 'FULL_HISTORICAL_ASSET_REGISTER_RECONCILIATION_INVALID'})
    errors.extend(historical_report.get('coverage_errors', []))
    return errors


def _advance_checkpoint(repo: Path) -> None:
    path = repo / '00_Governance' / 'CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md'
    if not path.is_file():
        raise RuntimeError('CONTINUITY_CHECKPOINT_MISSING_AFTER_IMPORT')
    text = path.read_text(encoding='utf-8')
    text = text.replace('**Version:** 1.3.0', '**Version:** 1.3.1', 1)
    text = text.replace('"version": "1.3.0"', '"version": "1.3.1"', 1)
    text = text.replace(
        '**Checkpoint status:** BUILD 0038 FULL HISTORICAL RECONCILIATION DELIVERED — IMPORT PENDING',
        '**Checkpoint status:** BUILD 0038 FULL HISTORICAL RECONCILIATION IMPORTED AND VALIDATED — COMMIT/PUSH PENDING',
        1,
    )
    text = text.replace(
        'Import the corrected Build 0038 package and review the full historical repository census and Master Asset Register Change Report before apply.',
        'Commit and push corrected Build 0038 using the locked commit message, then confirm GitHub Actions green.',
        1,
    )
    text = text.replace('"required_action": "IMPORT_FULL_HISTORICAL_RECONCILIATION"', '"required_action": "COMMIT_PUSH_CONFIRM_ACTIONS"', 1)
    text = text.replace(
        '"immediate_next_action": "Import corrected Build 0038 and complete full historical Master Asset Register reconciliation"',
        '"immediate_next_action": "Commit and push corrected Build 0038 and confirm GitHub Actions green"',
        1,
    )
    path.write_text(text, encoding='utf-8')


def _sync_checkpoint_register(register: Path) -> None:
    rows, meta = load_register(register)
    wanted = norm_path('00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md')
    matches = [row for row in rows if norm_path(row.get('Repository Path')) == wanted]
    if len(matches) != 1:
        raise RuntimeError(f'CHECKPOINT_ASSET_REGISTER_MATCH_INVALID: {len(matches)}')
    checkpoint_path = register.parents[1] / '00_Governance' / 'CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md'
    matches[0]['Version'] = '1.3.1'
    matches[0]['Status'] = 'LOCKED_ACTIVE'
    if checkpoint_path.is_file():
        matches[0]['File SHA256'] = sha256_bytes(checkpoint_path.read_bytes())
    _write_register(register, rows, meta)


def apply_pack(zip_path: Path, repo: Path, backup_root: Path, asset_register: Path | None = None) -> dict:
    preflight = inspect_pack(zip_path, repo, asset_register)
    if not preflight['valid']:
        preflight['applied'] = False
        return preflight
    asset_register = asset_register or CANONICAL_REGISTER_RELATIVE_PATH
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
        policy_path = repo / POLICY_PATH
        historical_report_path = repo / FULL_REPORT_PATH
        census_report_path = repo / CENSUS_REPORT_PATH
        historical_report = reconcile_full_historical_repository(
            repo,
            manifest_path,
            policy_path,
            asset_register,
            additional_files=None,
            apply=True,
            report_path=historical_report_path,
            census_report_path=census_report_path,
        )
        validation_errors = _validate_repo(
            repo,
            json.loads(manifest_path.read_text(encoding='utf-8')),
            historical_report,
        )
        verification = verify_master_asset_register(repo)
        (repo / BUTTON_VERIFY_PATH).write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
        if not verification.get("valid"):
            validation_errors.append({"code": "CANONICAL_MASTER_ASSET_REGISTER_BUTTON_VERIFICATION_FAILED", "details": verification})
        if validation_errors:
            raise RuntimeError(json.dumps(validation_errors))

        _advance_checkpoint(repo)
        _sync_checkpoint_register(register)
        report = {
            **preflight,
            'applied': True,
            'backup_path': str(backup),
            'full_historical_asset_register_report': historical_report,
            'post_import_validation': {'valid': True, 'errors': []},
            'master_asset_register_button_verification': verification,
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
    parser = argparse.ArgumentParser(description='Transactional Certiaura Build 0038 importer with full historical asset-register reconciliation')
    parser.add_argument('zip_path', type=Path)
    parser.add_argument('repository', type=Path)
    parser.add_argument('--asset-register', type=Path, default=CANONICAL_REGISTER_RELATIVE_PATH)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--backup-root', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = apply_pack(
        args.zip_path,
        args.repository,
        args.backup_root or args.repository / '.certiaura_backups',
        args.asset_register,
    ) if args.apply else inspect_pack(args.zip_path, args.repository, args.asset_register)
    output = json.dumps(result, indent=2)
    print(output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + '\n', encoding='utf-8')
    return 0 if result.get('valid') and (not args.apply or result.get('applied')) else 1


if __name__ == '__main__':
    raise SystemExit(main())
