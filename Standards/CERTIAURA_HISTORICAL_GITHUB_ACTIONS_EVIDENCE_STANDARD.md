# Certiaura Historical GitHub Actions Evidence Standard

## Purpose

This standard governs retrospective reconciliation of GitHub Actions evidence for Certiaura Builds 0001 onward.

## Required accounting

Every build must have exactly one historical evidence record containing the selected canonical commit, the selection basis, workflow availability at that commit and either:

1. a verified GitHub Actions run ID tied to the canonical commit; or
2. a controlled exception classification explaining why no successful run ID can be recorded.

Allowed controlled exception classifications are `NO_WORKFLOW_AT_COMMIT`, `NO_RUN_FOUND`, `RUN_FOUND_NOT_SUCCESS` and `BUILD_COMMIT_NOT_FOUND`. The last classification records that no canonical Git commit could be resolved for an early or non-repository build; it is an accounted exception, not a fabricated run ID. API failures and structurally incomplete records block Build 0055.

## Capture provenance

Evidence must distinguish `CONTEMPORANEOUS_HISTORY_CONFIRMED`, `CURRENT_REPOSITORY_RECORD_ONLY`, `BACKFILLED_BY_BUILD_0055` and `RESOLVED_EXCEPTION`. Backfilled evidence must never be represented as having been captured before the original closure.

## Canonical selection

The latest exact `Add Certiaura Build [NUMBER]` commit on first-parent `main` history is preferred. A broader Certiaura build-subject match may be used only as an explicit fallback and must remain visible in the audit record.

## Closure control

Build 0055 cannot reach canonical staging unless Builds 0001 through 0054 are all accounted for and the historical audit result is `HISTORICAL_ACTIONS_AUDIT_COMPLETE`. Future builds must continue to record their exact run ID contemporaneously before `ACTIONS_GREEN_CLOSED`.
