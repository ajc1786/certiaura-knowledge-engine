# Retatrutide Clinician Export Baseline

**Build provenance:** `CERT-BUILD-0047`
**Version:** 1.0.0
**Status:** Controlled baseline

## Objective

Provide a concise, auditable clinician-facing export of a pseudonymous longitudinal journey. The export supports review; it is not a prescription, diagnosis, clinical decision support authorisation or substitute for the source record.

## Required sections

1. Export metadata, version and generation time.
2. Pseudonymous subject and journey identifiers.
3. Compound identity and current investigational-status statement.
4. Data sources, date range and completeness summary.
5. Baseline and latest observation summary.
6. Derived trends with formulas and input dates.
7. Symptom and tolerability timeline.
8. Active alerts and alert-review status.
9. Resolved alerts with rationale.
10. Missing data, conflicts and uncertainty.
11. Evidence and rule provenance.
12. Approval state and disclaimer.

## Privacy minimum

The default export must not contain name, full address, personal email, telephone number, national identifier, exact date of birth or free-text identifiers. A separate controlled clinical system may map the pseudonym to a person.

## Export states

- `DRAFT_FOR_CLINICIAN_REVIEW`
- `CLINICIAN_APPROVED`
- `SUPERSEDED`
- `WITHDRAWN`

Only an authorised reviewer may set `CLINICIAN_APPROVED`.
