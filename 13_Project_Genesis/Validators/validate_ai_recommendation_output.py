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


REQUIRED = ['ai_output_id','output_type','personalisation_level','audience','jurisdiction','health_data_used','intended_purpose','medical_device_assessment','dpia_status','evidence_refs','uncertainty_statement','commercial_interest','human_review','risk_level','disposition','model_version','prompt_record','output_record','status','build_provenance']
BLOCK_TYPES = {'DOSE_OR_TITRATION','DIAGNOSIS','PRESCRIPTION_SELECTION','TREATMENT_PLAN'}
HIGH_TYPES = {'PRODUCT_RANKING','PERSONALISED_RISK','REGIMEN_SUGGESTION'} | BLOCK_TYPES


def validate(data):
    errors = []
    for key in REQUIRED:
        if key not in data:
            errors.append(f'missing required field: {key}')
    if errors:
        return errors
    output_type = data.get('output_type')
    personalisation = data.get('personalisation_level')
    health_data = bool(data.get('health_data_used'))
    review = data.get('human_review') or {}
    disposition = data.get('disposition')
    commercial = bool(data.get('commercial_interest'))

    if output_type in HIGH_TYPES and not data.get('evidence_refs'):
        errors.append('high-risk AI output requires evidence_refs')
    if not str(data.get('uncertainty_statement','')).strip():
        errors.append('uncertainty_statement is required')
    if output_type in BLOCK_TYPES and disposition not in {'REGULATED_PATHWAY_OR_BLOCK','BLOCK'}:
        errors.append('diagnosis, prescribing, dose or treatment output must be blocked or use a regulated pathway')
    if output_type in HIGH_TYPES and not bool(review.get('required')):
        errors.append('high-risk AI output must require human review')
    if output_type in HIGH_TYPES and disposition == 'ALLOW':
        errors.append('high-risk AI output cannot be automatically allowed')
    if personalisation in {'PERSONAL_HEALTH','CLINICAL'} or health_data:
        if data.get('dpia_status') not in {'APPROVED'}:
            errors.append('personal health data use requires approved DPIA status')
        if review.get('status') not in {'APPROVED','APPROVED_WITH_CONDITIONS'} and disposition not in {'BLOCK','REGULATED_PATHWAY_OR_BLOCK'}:
            errors.append('personal health output requires completed human review unless blocked')
    if data.get('medical_device_assessment') == 'PENDING' and disposition in {'ALLOW','ALLOW_WITH_CONTROLS'} and output_type in HIGH_TYPES:
        errors.append('potential medical-device intended purpose cannot be released while assessment is pending')
    if commercial and not str(data.get('commercial_interest_disclosure','')).strip():
        errors.append('commercial AI recommendation requires disclosure')
    if not str(data.get('model_version','')).strip() or not str(data.get('prompt_record','')).strip() or not str(data.get('output_record','')).strip():
        errors.append('model, prompt and output records are required for auditability')
    return errors


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) != 1:
        print('Usage: validate_ai_recommendation_output.py <record.json>', file=sys.stderr)
        return 2
    try:
        return result(validate(load(argv[0])))
    except Exception as exc:
        return result([f'validation exception: {exc}'])

if __name__ == '__main__':
    raise SystemExit(main())
