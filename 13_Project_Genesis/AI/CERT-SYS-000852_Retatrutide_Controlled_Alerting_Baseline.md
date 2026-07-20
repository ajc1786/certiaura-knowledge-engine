# Retatrutide Controlled Alerting Baseline

**Universal Asset Identifier:** CERT-SYS-000852
**Build provenance:** CERT-BUILD-0046
**Status:** BASELINE

## Purpose

Apply a deterministic policy to journey state, review schedule and evidence-linked analytics to produce bounded review alerts.

## Permitted states

- NO_ALERT
- INSUFFICIENT_DATA
- CLINICIAN_DISCUSSION_REQUIRED
- LOCKED_URGENT_ROUTING

## Prohibitions

The workflow must not diagnose, prescribe, recommend a personalised dose, alter titration, select treatment or provide procurement advice.
