from __future__ import annotations
import json
import sys
from pathlib import Path


def load(path: str):
    with Path(path).open('r', encoding='utf-8') as f:
        return json.load(f)


def result(errors):
    payload = {'valid': not errors, 'errors': errors}
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 1


REQUIRED = ['communication_id','title','audience','jurisdiction','channels','claim_ids','commercial_interest','ai_involvement','required_disclosures','approval_level','reviews','decision','status','build_provenance']
PUBLIC_CHANNELS = {'WEBSITE','MARKETPLACE','AFFILIATE','SOCIAL','EMAIL_CAMPAIGN','PAID_ADVERTISEMENT','AI_CHAT'}


def validate(data):
    errors = []
    for key in REQUIRED:
        if key not in data:
            errors.append(f'missing required field: {key}')
    if errors:
        return errors
    reviews = data.get('reviews') or {}
    decision = data.get('decision')
    channels = set(data.get('channels') or [])
    audience = data.get('audience')
    reg = data.get('product_regulatory_classification')
    commercial = bool(data.get('commercial_interest'))
    approved = decision in {'APPROVED','APPROVED_WITH_CONDITIONS'}

    if not data.get('claim_ids'):
        errors.append('at least one claim_id is required')
    if commercial and not str(data.get('commercial_interest_disclosure','')).strip():
        errors.append('commercial interest disclosure is required')
    if commercial and not data.get('required_disclosures'):
        errors.append('commercial communication requires explicit disclosure controls')
    if approved and reviews.get('communications') not in {'APPROVED','APPROVED_WITH_CONDITIONS'}:
        errors.append('communications review required before approval')
    if channels & PUBLIC_CHANNELS and audience not in {'PUBLIC','MIXED'}:
        errors.append('public channel requires PUBLIC or MIXED audience classification')
    if reg == 'PRESCRIPTION_ONLY_MEDICINE' and audience in {'PUBLIC','MIXED'} and commercial:
        errors.append('public promotional prescription-only medicine communication is blocked')
    if data.get('ai_involvement') == 'PERSONALISATION' and approved:
        if reviews.get('data_protection') not in {'APPROVED','APPROVED_WITH_CONDITIONS'}:
            errors.append('personalised AI communication requires data-protection review')
        if reviews.get('medical') not in {'APPROVED','APPROVED_WITH_CONDITIONS'}:
            errors.append('personalised AI health communication requires medical review')
    if approved and not data.get('approval_expiry'):
        errors.append('approved communication requires approval_expiry')
    return errors


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print('Usage: validate_communication_approval.py <record.json>', file=sys.stderr)
        return 2
    try:
        return result(validate(load(argv[0])))
    except Exception as exc:
        return result([f'validation exception: {exc}'])

if __name__ == '__main__':
    raise SystemExit(main())
