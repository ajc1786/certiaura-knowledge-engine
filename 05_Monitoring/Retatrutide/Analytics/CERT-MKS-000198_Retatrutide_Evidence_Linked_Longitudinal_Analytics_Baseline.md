# Retatrutide Evidence-Linked Longitudinal Analytics Baseline

**Universal Asset Identifier:** CERT-MKS-000198
**Build provenance:** CERT-BUILD-0046
**Status:** BASELINE

## Purpose

Provide deterministic descriptive analytics across pseudonymised Retatrutide journey events while retaining event, policy and evidence references.

## Boundary

The asset describes recorded values and change over time. It does not diagnose, recommend treatment, select a dose, alter titration or advise procurement.

## Controls

- Direct identifiers are rejected.
- Source event identifiers and evidence references remain attached to every calculated metric.
- Insufficient data produces an explicit abstention state.
- An urgent journey lock propagates to analytics outputs.
- Results are deterministic for identical canonical inputs.
