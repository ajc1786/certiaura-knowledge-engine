from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description='Run corrected Build 0037 through the installed transactional Build 0038 importer.')
    parser.add_argument('zip_path')
    parser.add_argument('repository_path')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--report', default='Documentation/Build_Records/0037/DRY_RUN_REPORT.json')
    args = parser.parse_args(argv)

    repo = Path(args.repository_path).resolve()
    zip_path = Path(args.zip_path).resolve()
    register = repo / 'Documentation/Master_Asset_Register.csv'
    importer = repo / '13_Project_Genesis/Import/transactional_build_import.py'
    if not zip_path.is_file():
        raise SystemExit(f'Build pack not found: {zip_path}')
    if not register.is_file():
        raise SystemExit(f'Canonical Master Asset Register not found: {register}')
    if not importer.is_file():
        raise SystemExit('Build 0038 transactional importer is not installed; stop without changing the repository.')

    command = [sys.executable, str(importer), str(zip_path), str(repo), '--asset-register', 'Documentation/Master_Asset_Register.csv', '--report', args.report]
    if args.apply:
        command.append('--apply')
    return subprocess.call(command, cwd=repo)

if __name__ == '__main__':
    raise SystemExit(main())
