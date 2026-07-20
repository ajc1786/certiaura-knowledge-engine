# Living Evidence Surveillance and Update Standard

**UAI:** CERT-EKS-000752
**Version:** 1.0.0

## Purpose

Maintain evidence-backed assets as living knowledge rather than static publications.

## Surveillance design

Every material scientific asset must declare:

- surveillance question;
- controlled search expression;
- source connectors;
- cadence and next-run date;
- accountable owner;
- escalation threshold;
- affected assets and claims;
- last successful run and completeness status.

## Event triage

New results are classified as `NO_CHANGE`, `POTENTIAL_UPDATE`, `URGENT_SAFETY`, `RETRACTION_OR_CORRECTION`, or `METHOD_ONLY`.

`URGENT_SAFETY` and `RETRACTION_OR_CORRECTION` events require immediate human escalation and temporary claim restrictions where impact is unresolved.

## Update control

A material update must produce an impact assessment, identify all dependent assets and relationships, state whether public outputs require correction, and preserve the previous evidence state in history.
