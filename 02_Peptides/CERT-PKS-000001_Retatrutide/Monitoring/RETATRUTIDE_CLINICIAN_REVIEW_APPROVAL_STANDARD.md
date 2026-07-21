# Retatrutide Clinician Review Approval Standard

**Build provenance:** `CERT-BUILD-0048`
**Version:** 1.0.0
**Status:** Controlled baseline
**Dependency:** Build 0047 clinician export and alert-review baseline.

## Purpose

This standard defines the controlled human approval layer applied after a structurally valid Retatrutide clinician export has been generated. It records review, requested corrections, approval, supersession and withdrawal without granting autonomous diagnostic or treatment authority to software.

## Mandatory review inputs

1. Exact clinician-export identifier and SHA-256.
2. Export version and source journey identifier.
3. Build 0047 structural-validation status.
4. Active alerts, unresolved uncertainty and missing-data summary.
5. Reviewer identity as a controlled role reference, not a direct personal identifier in public output.
6. Review timestamp, decision and rationale.
7. Evidence and rule provenance used by the reviewed export.
8. Any requested corrections linked to exact fields or observations.

## Permitted decisions

- `CHANGES_REQUIRED`
- `APPROVED_FOR_CONTROLLED_HANDOFF`
- `WITHDRAWN_BY_REVIEWER`
- `SUPERSEDED_BY_NEW_EXPORT`

Approval confirms only that the export is suitable for controlled handoff within its stated scope. It does not confirm diagnosis, treatment suitability, medicine access, dose selection, contraindication clearance or emergency exclusion.

## Separation of duties

The generator may create a draft review record. It may not populate an approval decision, reviewer attestation or approval timestamp. A review record must not approve itself, and the generator identity must not equal the reviewer role reference.

## Version integrity

Every approval record must bind to one immutable export hash. Any material correction requires a new export version, a new hash and a new review. Earlier approved versions remain in the audit chain as superseded rather than being overwritten.
