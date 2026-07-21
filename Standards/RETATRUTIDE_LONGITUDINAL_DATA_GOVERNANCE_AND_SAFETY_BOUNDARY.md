# Retatrutide Longitudinal Data Governance and Safety Boundary

**Build provenance:** `CERT-BUILD-0047`
**Version:** 1.0.0
**Status:** Locked implementation boundary for Build 0047

## Boundary

Retatrutide remains an investigational medicine unless and until the applicable regulator grants an approval for a specific indication and jurisdiction. The Build 0047 dashboard is an information-management and review workflow. It does not authorise access, supply, compounding, administration or treatment.

## Fail-closed controls

The system must fail closed when:

- subject or journey identity is ambiguous;
- source provenance is absent;
- an alert rule lacks approval provenance;
- an action contains an autonomous treatment instruction;
- a clinician export contains direct personal identifiers;
- dates, units or identifiers are structurally invalid;
- the Asset Intent Manifest does not own the exact validated path;
- build provenance is not exactly `CERT-BUILD-0047`.

## Human authority

Clinical interpretation, diagnosis, treatment, medicine changes and emergency assessment remain with authorised healthcare professionals and applicable local services. Automated output may only request review or route the record to a designated human workflow.

## Auditability

Generated outputs must retain input hashes, generator version, rule versions, build provenance and generation timestamp. Corrections create a new export version and preserve supersession history.
