# Retatrutide Alert Review Workflow

**Build provenance:** `CERT-BUILD-0047`
**Version:** 1.0.0
**Status:** Controlled baseline

## Workflow states

`NEW` -> `TRIAGED` -> `CLINICAL_REVIEW_PENDING` -> `CLINICIAN_REVIEWED` -> `CLOSED`

An alert may move to `DATA_CORRECTION_PENDING` where the trigger is caused by missing, inconsistent or incorrectly sourced data. Closure requires a recorded rationale and reviewer identity.

## Severity model

- `INFORMATIONAL`: data-quality or context signal with no immediate clinical interpretation.
- `ROUTINE_REVIEW`: review in the normal clinician or trial workflow.
- `PRIORITY_REVIEW`: prompt clinician or investigator review under the governing protocol.
- `URGENT_REVIEW`: immediate escalation to the designated clinical route or local emergency route.

Severity does not equal a diagnosis. The workflow records that review is required and preserves the source rule.

## Mandatory review record

Each review must record:

- exact alert identifier and journey identifier;
- trigger data and measurement provenance;
- rule version and approval provenance;
- reviewer role and timestamp;
- decision state;
- rationale;
- permitted follow-up action;
- unresolved uncertainty;
- closure or next-review date.

## Permitted baseline actions

- `REQUEST_REPEAT_MEASUREMENT`
- `REQUEST_SOURCE_VERIFICATION`
- `CONTACT_DESIGNATED_CLINICIAN`
- `FOLLOW_LOCAL_URGENT_CARE_ROUTE`
- `CORRECT_DATA_WITH_AUDIT_TRAIL`
- `CONTINUE_OBSERVATION_UNDER_PROTOCOL`
- `CLINICIAN_DECISION_REQUIRED`

The baseline validator rejects autonomous treatment, dosing, diagnosis and reassurance actions.

## Ownership rule

Build-owned assets are resolved only from exact repository-relative paths declared in `Documentation/Build_Records/0047/ASSET_INTENT_MANIFEST.json` where `build_provenance` exactly equals `CERT-BUILD-0047`. Build-number substring matching is prohibited.
