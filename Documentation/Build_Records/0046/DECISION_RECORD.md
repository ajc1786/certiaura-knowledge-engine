# Build 0046 Decision Record

## Decision

Implement descriptive, evidence-linked longitudinal analytics and bounded review alerts without diagnostic or treatment-selection functionality.

## Rationale

This extends Build 0045 journey data into reviewable outputs while preserving pseudonymisation, provenance, deterministic behaviour and safety boundaries.

## Locked controls

- Exact Asset Intent Manifest and build-provenance validation scope.
- External-only transactional backups.
- Windows PowerShell 5.1 full-path regression.
- Expected native failures handled without terminating the harness.
- No persistent browser storage or network resources.
