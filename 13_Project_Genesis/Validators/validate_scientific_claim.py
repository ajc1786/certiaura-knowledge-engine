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


REQUIRED = ['claim_id','exact_claim_text','claim_classes','risk_level','audience','jurisdiction','channels','commercial_purpose','product_regulatory_classification','evidence','ai_involvement','reviews','disposition','status','build_provenance']
ABSOLUTE_PATTERNS = ['100% safe','risk free','no side effects','guaranteed','guarantees','cure-all']
HIGH_CLASSES = {'HEALTH','MEDICINAL','SAFETY','COMPARATIVE','COMMERCIAL','TESTIMONIAL','AI_RECOMMENDATION'}


def validate(data):
    errors = []
    for key in REQUIRED:
        if key not in data:
            errors.append(f'missing required field: {key}')
    if errors:
        return errors
    text = str(data.get('exact_claim_text','')).lower()
    classes = set(data.get('claim_classes') or [])
    reviews = data.get('reviews') or {}
    audience = data.get('audience')
    reg = data.get('product_regulatory_classification')
    commercial = bool(data.get('commercial_purpose'))
    evidence = data.get('evidence') or []
    disposition = data.get('disposition')

    if not data.get('exact_claim_text','').strip():
        errors.append('exact_claim_text must not be blank')
    if any(p in text for p in ABSOLUTE_PATTERNS):
        errors.append('blocked absolute guarantee or safety wording detected')
    if classes & HIGH_CLASSES and not evidence and disposition in {'APPROVED','APPROVED_WITH_CONDITIONS'}:
        errors.append('high-risk approved claim requires evidence')
    if classes & {'HEALTH','MEDICINAL','SAFETY','COMPARATIVE'} and reviews.get('scientific') not in {'APPROVED','APPROVED_WITH_CONDITIONS'} and disposition in {'APPROVED','APPROVED_WITH_CONDITIONS'}:
        errors.append('scientific review required for approved high-risk claim')
    if 'MEDICINAL' in classes:
        if reg == 'UNLICENSED_PRODUCT':
            errors.append('medicinal claim for unlicensed product is blocked')
        if reviews.get('medical') not in {'APPROVED','APPROVED_WITH_CONDITIONS'} and disposition in {'APPROVED','APPROVED_WITH_CONDITIONS'}:
            errors.append('medical review required for approved medicinal claim')
        if reviews.get('legal_regulatory') not in {'APPROVED','APPROVED_WITH_CONDITIONS'} and disposition in {'APPROVED','APPROVED_WITH_CONDITIONS'}:
            errors.append('legal/regulatory review required for approved medicinal claim')
    if reg == 'PRESCRIPTION_ONLY_MEDICINE' and audience in {'PUBLIC','MIXED'} and commercial:
        errors.append('public promotional prescription-only medicine claim is blocked')
    if commercial and not str(data.get('commercial_interest_disclosure','')).strip():
        errors.append('commercial-purpose claim requires commercial interest disclosure')
    if data.get('ai_involvement') in {'RECOMMENDATION','PERSONALISATION'} and reviews.get('communications') not in {'APPROVED','APPROVED_WITH_CONDITIONS'} and disposition in {'APPROVED','APPROVED_WITH_CONDITIONS'}:
        errors.append('AI recommendation/personalisation requires communications review')
    if disposition in {'APPROVED','APPROVED_WITH_CONDITIONS'} and not data.get('approval_expiry'):
        errors.append('approved claim requires approval_expiry')
    return errors


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print('Usage: validate_scientific_claim.py <record.json>', file=sys.stderr)
        return 2
    try:
        data = load(argv[0])
        return result(validate(data))
    except Exception as exc:
        return result([f'validation exception: {exc}'])

if __name__ == '__main__':
    raise SystemExit(main())
