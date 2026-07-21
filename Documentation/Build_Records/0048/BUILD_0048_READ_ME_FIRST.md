# CERTIAURA BUILD 0048 - READ FIRST

**Build title:** retatrutide clinician review approval, export version control, controlled handoff and audit trail baseline
**Build ID:** CERT-BUILD-0048
**Authorisation:** GREEN_AUTHORISED
**Implementation state:** Generated candidate; canonical implementation only follows Windows PowerShell 5.1 regression, import, validation, commit, push and green GitHub Actions.
**Dependency:** Build 0047 `ACTIONS_GREEN_CLOSED`.

## Purpose

Build 0048 extends the Build 0047 clinician export baseline with human approval, immutable export versioning, controlled handoff bundles, acknowledgement receipts and an append-only audit boundary.

## Mandatory sequence

1. Run the separate Windows PowerShell 5.1 pre-release regression.
2. Confirm the exact PASS endpoint and package SHA-256.
3. Run `Scripts/START_BUILD_0048.cmd`.
4. Review dry-run collision and Master Asset Register reports.
5. Type `APPLY` only after review.
6. Complete validators, tests, runtime scan, staging and both Git checks.
7. Type `COMMIT` to use the locked commit message and push.
8. Confirm GitHub Actions green before `ACTIONS_GREEN_CLOSED`.

## RC2 correction

RC2 corrects the post-apply test scope. ASCII and LF hygiene assertions apply only to exact Build 0048 Asset Intent Manifest paths. Unrelated historical repository files remain governed by repository-wide validation and are not attributed to Build 0048.
