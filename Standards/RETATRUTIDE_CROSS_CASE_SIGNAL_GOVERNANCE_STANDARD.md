# Retatrutide Cross-Case Signal Governance Standard

**Build provenance:** CERT-BUILD-0052
**Status:** Controlled baseline
**Scope:** Aggregated post-closure surveillance only

## Purpose

This standard converts multiple governed Build 0051 case-surveillance records into a de-identified cohort signal while preserving case-level provenance, privacy boundaries and human review.

## Locked boundaries

- No autonomous diagnosis, treatment, dosing, prescribing or patient-specific recommendation.
- A cross-case signal is a review trigger, not proof of causation.
- Every contributing case must be traceable through controlled identifiers without exposing direct personal data.
- Case reopening remains governed by Build 0051; this build may propose escalation but may not silently reopen a case.
- Suppression applies where the minimum cohort threshold is not met.
- Evidence feedback is drafted and reviewed before any knowledge asset is changed.

## Workflow

1. Receive eligible closed-case surveillance events.
2. Validate predecessor provenance and case eligibility.
3. Remove direct identifiers and enforce minimum cohort size.
4. Group comparable events by controlled signal key.
5. Calculate recurrence, temporal clustering and severity distribution.
6. Classify as `NO_SIGNAL`, `WATCH`, `ESCALATE` or `INSUFFICIENT_DATA`.
7. Create a human-review packet with contributing-case references.
8. Record the governance decision.
9. Route approved findings to controlled evidence/knowledge feedback.
10. Retain an immutable audit trail.

## Minimum decision controls

- At least three eligible cases for an aggregate output.
- At least two independent reviewable sources before an evidence feedback proposal can be classified `READY_FOR_REVIEW`.
- Any emergency or serious-event flag routes to immediate human review regardless of aggregate threshold.
- Conflicting evidence blocks automated promotion.
