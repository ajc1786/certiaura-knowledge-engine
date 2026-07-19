from __future__ import annotations
import argparse
import csv
import json
import re
from pathlib import Path

UAI_RE = re.compile(r'^CERT-[A-Z0-9]+-\d{6}$')


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('repository_path')
    args = parser.parse_args(argv)
    repo = Path(args.repository_path).resolve()
    errors = []
    required = [
        '00_Governance/SCIENTIFIC_CLAIMS_ADVERTISING_AI_COMMUNICATIONS_STANDARD.md',
        '00_Governance/AI_RECOMMENDATION_SAFETY_BOUNDARY_STANDARD.md',
        '00_Governance/RESPONSIBLE_COMMUNICATIONS_APPROVAL_WORKFLOW.md',
        'Documentation/Master_Asset_Register.csv',
        'Documentation/Build_Records/0037/ASSET_INTENT_MANIFEST.json'
    ]
    for rel in required:
        if not (repo / rel).is_file():
            errors.append(f'missing required repository file: {rel}')

    register = repo / 'Documentation/Master_Asset_Register.csv'
    if register.is_file():
        with register.open('r', encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        uais = [str(r.get('Universal Asset Identifier','')).strip() for r in rows]
        blanks = [i for i,u in enumerate(uais, 2) if not u]
        duplicates = sorted({u for u in uais if u and uais.count(u) > 1})
        invalid = sorted({u for u in uais if u and not UAI_RE.match(u)})
        placeholders = [u for u in uais if u.upper() == 'NO NEW UAI']
        if blanks: errors.append(f'blank UAI rows: {len(blanks)}')
        if duplicates: errors.append(f'duplicate UAI groups: {len(duplicates)}')
        if invalid: errors.append(f'invalid UAI formats: {len(invalid)}')
        if placeholders: errors.append('legacy NO NEW UAI placeholder detected')

    print(json.dumps({'valid': not errors, 'errors': errors}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    raise SystemExit(main())
