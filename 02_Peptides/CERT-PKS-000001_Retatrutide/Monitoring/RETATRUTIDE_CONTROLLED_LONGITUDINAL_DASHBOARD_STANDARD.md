# Retatrutide Controlled Longitudinal Dashboard Standard

**Build provenance:** `CERT-BUILD-0047`
**Version:** 1.0.0
**Status:** Controlled baseline
**Scope:** Research, clinical-trial, clinician-supervised and evidence-review contexts only.

## Purpose

This standard defines a reproducible longitudinal dashboard for the Retatrutide knowledge asset. It converts dated observations, provenance, data-quality indicators and controlled alerts into an auditable view without making an autonomous diagnosis or treatment decision.

## Mandatory dashboard domains

1. Subject and journey pseudonymous identifiers.
2. Investigational and regulatory status with dated source provenance.
3. Observation timeline and source type.
4. Weight and anthropometric trend summaries.
5. Vital-sign and laboratory fields where supplied by an authorised source.
6. Symptom and tolerability observations recorded as observations, not diagnoses.
7. Data completeness and uncertainty.
8. Active, reviewed and closed alerts.
9. Evidence links and rule provenance.
10. Clinician-export readiness and approval state.

## Controlled alert boundary

The dashboard may classify a record as requiring review only where the rule:

- has an explicit `rule_id`;
- has a source reference or local clinical protocol reference;
- records the approving clinician or governance authority;
- has a version and effective date;
- uses data available in the journey record;
- produces only a review or escalation state.

The baseline must not produce dose changes, medicine initiation, medicine cessation, diagnosis, contraindication clearance, emergency exclusion or a statement that care is unnecessary.

## Data quality

Every observation must include date, source type and source reference. Estimated, self-reported, device-derived, laboratory-derived and clinician-entered data must remain distinguishable. Missingness must be shown and must not be silently imputed.

## Longitudinal integrity

- Observation dates must be ordered and unique by observation identifier.
- Units must be explicit.
- Trend calculations must identify the first and last usable observations.
- Derived values must name their inputs and formula.
- Corrected data must retain correction history.
- Cross-subject merging is prohibited.

## Clinician export gate

An export may be generated when the journey passes structural validation. It must be marked `DRAFT_FOR_CLINICIAN_REVIEW` until an authorised clinician or trial investigator approves it. The export must show active alerts, unresolved uncertainty, missing fields and the investigational-status statement.
