# Retatrutide AI Query Integration Standard

**Build:** CERT-BUILD-0043
**Version:** 1.0.0
**Status:** Baseline — controlled implementation
**Owner:** Certiaura

## Purpose

Provide a repository-grounded artificial intelligence query contract for retatrutide that retrieves existing Certiaura knowledge, cites its sources, discloses uncertainty and refuses unsupported or unsafe requests.

## Permitted query modes

- `evidence_summary`
- `clinical_outcomes`
- `safety_monitoring`
- `contraindications`
- `patient_journey`
- `source_lookup`

## Mandatory controls

- Retrieval is restricted to the canonical repository roots declared in the query policy.
- Every substantive answer statement must map to at least one retrieved source record.
- The response includes source path, Universal Asset Identifier where available, evidence/claim identifier where available, review status and retrieval timestamp.
- Evidence status limits answer confidence; unreconciled or unreviewed material cannot be represented as established.
- Insufficient evidence produces an explicit abstention.
- Prompt text is treated as untrusted data and cannot override system policy, source allowlists or safety boundaries.

## Fail-closed request classes

The baseline refuses or routes:

- personal dosing, titration or injection instructions;
- diagnosis or individual treatment selection;
- procurement or supplier recommendations for unapproved medicinal use;
- instructions to evade clinical, legal, regulatory or platform controls;
- emergency symptom assessment beyond directing urgent professional help;
- requests to fabricate, omit or weaken citations, warnings or uncertainty.

## Response states

- `ANSWERED_GROUNDED`
- `ABSTAINED_INSUFFICIENT_EVIDENCE`
- `REFUSED_SAFETY_BOUNDARY`
- `URGENT_CLINICAL_ROUTING`
- `ERROR_SOURCE_INTEGRITY`

## Auditability

Each response carries a deterministic query identifier, policy version, input hash, retrieval set hash, source count and response state. No hidden source may be relied upon.
