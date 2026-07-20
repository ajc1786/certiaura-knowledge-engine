# Evidence Ingestion, Citation, Living Evidence and Scientific Review Standard

**UAI:** CERT-EKS-000751
**Version:** 1.0.0
**Status:** Active
**Owner:** Certiaura Evidence Knowledge System

## Control objective

Create an auditable chain from source discovery to approved scientific use. No evidence item may support a public claim, recommendation, report conclusion or Product Passport statement until identity, provenance, rights, duplicate status, evidence quality and human scientific review are recorded.

## Mandatory workflow

`DISCOVERED → RIGHTS_CHECKED → IDENTITY_NORMALISED → DEDUPLICATED → INGESTED → TRIAGED → HUMAN_REVIEWED → APPROVED / CONDITIONAL / REJECTED → SURVEILLED`

## Required records

- Evidence ingestion record
- Citation provenance record
- Duplicate assessment
- Evidence quality and limitations assessment
- Scientific review record
- Living evidence surveillance query and event
- Retraction or correction event where applicable
- Evidence update impact assessment where a source changes

## Non-negotiable controls

1. Preserve DOI, PMID, trial registry identifier and canonical URL where available.
2. Store full text only where the recorded rights basis permits it.
3. Treat artificial intelligence extraction as assistive; final scientific approval requires an accountable human reviewer.
4. Keep source interpretation separate from source metadata.
5. Link each approved claim to the exact evidence object and review decision.
6. Quarantine unresolved identity, rights, duplicate, retraction or conflict issues.
7. Reassess dependent assets when evidence is corrected, retracted or materially updated.

## Closure gate

An evidence object is not claim-ready until all mandatory records validate and the scientific review decision is `APPROVED` or `CONDITIONAL` with explicit limitations.
