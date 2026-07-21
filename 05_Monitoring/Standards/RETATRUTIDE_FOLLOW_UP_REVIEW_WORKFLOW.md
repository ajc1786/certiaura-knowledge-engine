# Retatrutide Follow-Up Review Workflow

Build provenance: CERT-BUILD-0049

## States

- `FOLLOW_UP_NOT_DUE`
- `FOLLOW_UP_DUE`
- `FOLLOW_UP_COMPLETED`
- `FOLLOW_UP_OVERDUE`
- `LOCKED_URGENT_ROUTING`
- `CLOSED_NO_FURTHER_ACTION`

## Controls

1. The follow-up references one Build 0048 handoff bundle and one acknowledgement record.
2. Dates are explicit ISO 8601 values.
3. `LOCKED_URGENT_ROUTING` takes precedence over every routine state.
4. Routine closure requires a human reviewer role reference and rationale.
5. Missing information produces an abstention or review requirement, never an inferred clinical conclusion.
