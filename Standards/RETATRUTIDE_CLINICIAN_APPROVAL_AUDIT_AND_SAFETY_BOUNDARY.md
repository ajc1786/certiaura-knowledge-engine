# Retatrutide Clinician Approval Audit and Safety Boundary

**Build provenance:** `CERT-BUILD-0048`
**Version:** 1.0.0
**Status:** Locked implementation boundary for Build 0048

## Human authority

Only an authorised human clinician or trial investigator may approve an export for controlled handoff. Software may validate structure, calculate hashes, assemble a draft bundle and identify missing controls. It may not approve, diagnose, prescribe, select a dose, recommend medicine access, clear contraindications or state that urgent care is unnecessary.

## Fail-closed conditions

- review approval is absent or machine-generated;
- reviewer and generator are the same actor;
- export or component hashes do not match;
- the export version is withdrawn, expired or superseded;
- the version chain is broken or cyclic;
- direct identifiers are present;
- urgent-routing status is suppressed;
- approval rationale, timestamp or reviewer role is missing;
- evidence provenance is absent;
- the exact Asset Intent Manifest path is not owned by `CERT-BUILD-0048`.

## Audit retention

Audit events, approvals, withdrawals, supersession links, acknowledgements and hashes are append-only. Deletion requires a separately authorised retention decision and must preserve the fact and authority of deletion.
