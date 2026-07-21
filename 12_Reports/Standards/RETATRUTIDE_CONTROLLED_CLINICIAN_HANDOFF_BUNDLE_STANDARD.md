# Retatrutide Controlled Clinician Handoff Bundle Standard

**Build provenance:** `CERT-BUILD-0048`
**Version:** 1.0.0
**Status:** Controlled baseline

## Purpose

Define a portable, auditable bundle for transferring an approved pseudonymous Retatrutide clinician export to an authorised review destination.

## Required bundle components

- approved clinician export;
- clinician review decision;
- export version-chain record;
- evidence and alert provenance summary;
- bundle manifest containing file paths, SHA-256 values and byte sizes;
- handoff metadata and expiry date;
- acknowledgement template;
- safety and investigational-status statement.

## Privacy and minimisation

The default bundle must not include a name, full address, personal email, telephone number, national identifier, exact date of birth, free-text identifiers or an unencrypted re-identification key.

## Handoff states

- `BUNDLE_DRAFT`
- `READY_FOR_AUTHORISED_HANDOFF`
- `HANDED_OFF`
- `ACKNOWLEDGED`
- `EXPIRED`
- `WITHDRAWN`

## Fail-closed controls

Bundle generation fails when approval is absent, hashes do not match, the version is superseded or withdrawn, direct identifiers are detected, active urgent-routing information is omitted, or any component lacks exact build provenance.

The bundle is an information transfer mechanism. It is not a prescription, medicine order, treatment plan, diagnosis or emergency-care determination.
