# Evidence Ingestion State Machine

**UAI:** CERT-EKS-000757

States: `DISCOVERED`, `RIGHTS_CHECKED`, `NORMALISED`, `DEDUPLICATED`, `INGESTED`, `TRIAGED`, `IN_REVIEW`, `APPROVED`, `CONDITIONAL`, `REJECTED`, `QUARANTINED`, `SUPERSEDED`, `RETRACTED`.

Transitions require actor, timestamp, reason and source state. Direct transition from `DISCOVERED` to `APPROVED` is prohibited. `RETRACTED` and `QUARANTINED` block claim use.
