
# Decision record — Build 0041

## Decision

Create the first compound-specific implementation of the Build 0039 evidence-ingestion and scientific-review controls using Retatrutide, the existing flagship asset `CERT-PKS-000001`.

## Rationale

The platform already contains generic evidence governance. The highest-leverage next work package is to convert those controls into a reusable, validated scientific corpus and citation graph for the flagship compound.

## Locked boundaries

- Preserve `CERT-PKS-000001`; do not renumber or overwrite the existing flagship file.
- Allocate new UAIs only during canonical Master Asset Register reconciliation.
- Keep peer-reviewed evidence, registry protocol records and sponsor topline communications separately labelled.
- Retain an explicit investigational-status warning.
- Require human scientific approval before public release.
- Do not provide personal dosing or self-administration instructions.
