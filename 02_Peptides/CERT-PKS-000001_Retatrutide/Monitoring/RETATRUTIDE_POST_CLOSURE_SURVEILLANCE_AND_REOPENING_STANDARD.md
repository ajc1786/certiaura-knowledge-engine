# Retatrutide Post-Closure Surveillance and Governed Reopening Standard

**Build provenance:** CERT-BUILD-0051
**Status:** Controlled baseline

## Purpose

This standard governs monitoring after a case has reached controlled closure. It preserves the Build 0050 closure decision while allowing a new safety signal, recurrent issue, material evidence change, clinician request or verified data correction to trigger human review.

## Core controls

- Closure is never silently reversed.
- Every surveillance event uses a pseudonymous case identifier.
- Every reopening decision identifies an authorised human reviewer and a documented trigger.
- Urgent signals take precedence over routine periodic review.
- Receipt or administrative activity cannot downgrade urgent routing.
- The closed record remains immutable; reopening creates a new governed state transition.
- Insufficient data produces abstention rather than reassurance.
- The workflow cannot diagnose, prescribe or change treatment.

## Controlled states

`SURVEILLANCE_NOT_DUE`, `SURVEILLANCE_DUE`, `SURVEILLANCE_COMPLETED`, `SURVEILLANCE_OVERDUE`, `LOCKED_URGENT_ROUTING`, `SURVEILLANCE_ENDED`.

Reopening decisions are `REOPEN_APPROVED`, `REOPEN_REJECTED`, `MORE_INFORMATION_REQUIRED` or `LOCKED_URGENT_ROUTING`.
