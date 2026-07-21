# Retatrutide Clinician Review Decision Workflow

**Build provenance:** `CERT-BUILD-0048`
**Version:** 1.0.0
**Status:** Controlled baseline

## State model

`DRAFT_REVIEW` -> `IN_REVIEW` -> `CHANGES_REQUIRED` -> `REVISED_EXPORT_PENDING`

or

`DRAFT_REVIEW` -> `IN_REVIEW` -> `APPROVED_FOR_CONTROLLED_HANDOFF`

An approved review may later move to `SUPERSEDED` or `WITHDRAWN`. State transitions require timestamped audit events and an authorised human role.

## Review gates

Approval is blocked when:

- the export is not `DRAFT_FOR_CLINICIAN_REVIEW`;
- the export hash is missing or differs from the reviewed file;
- active urgent-routing states are omitted;
- unresolved uncertainty is concealed;
- direct identifiers are present;
- evidence or rule provenance is incomplete;
- the reviewer role is absent;
- the same actor is recorded as both generator and reviewer;
- autonomous treatment, dosing, diagnosis or reassurance language is present.

## Permitted follow-up actions

- `REQUEST_EXPORT_CORRECTION`
- `REQUEST_SOURCE_VERIFICATION`
- `REQUEST_ALERT_REVIEW_COMPLETION`
- `APPROVE_CONTROLLED_HANDOFF`
- `WITHDRAW_EXPORT`
- `SUPERSEDE_EXPORT`
- `CLINICIAN_DECISION_REQUIRED`

## Audit rule

Each transition appends an event. Existing events are immutable. Corrections append a new event and, where applicable, generate a new export version.
