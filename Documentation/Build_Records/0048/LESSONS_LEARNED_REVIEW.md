# Build 0048 Lessons-Learned Review

## Accumulated prior-build lessons reviewed: PASS

Build 0048 explicitly carries forward all controls through Build 0047, including realistic predecessor collision fixtures, exact operator command regression, external transactional backup, automatic post-apply rollback, exact path/provenance ownership, Windows PowerShell 5.1 collection normalisation, StrictMode-safe empty collection handling, one canonical variable name, ASCII-only PowerShell, LF hygiene, runtime-artifact exclusion and both Git whitespace checks.

## Current-build lessons recorded: PASS

### Pre-production design lesson

- Risk: a clinician export can be structurally valid yet still be handed off without human approval, immutable version binding or receipt evidence.
- Root cause class: workflow completeness gap rather than a defect in Build 0047.
- Corrective design: add human approval, separation of duties, immutable hashes, supersession chain, controlled handoff bundle and acknowledgement receipt.

## Lessons converted to regression controls: PASS

- Self-approval is blocked.
- Direct identifiers are blocked.
- Broken and cyclic supersession chains are blocked.
- Multiple current-approved versions are blocked.
- Bundle generation requires one approved version and matching review reference.
- Realistic Build 0047 predecessor paths are present in the synthetic repository and hash-verified unchanged.
- Package path collisions are inventoried and blocked during dry run.
- Exact canonical test commands are mirrored in the Windows PowerShell 5.1 regression.
- Post-apply failures trigger automatic rollback before commit.

## Continuity checkpoint updated: PASS

The checkpoint delta records Build 0047 as `ACTIONS_GREEN_CLOSED`, Build 0048 as the active candidate and the Windows PowerShell 5.1 regression as the release blocker.

### RC2 real-repository regression lesson

- Defect: the post-apply hygiene unit test recursively scanned every PowerShell and CMD file in the historical repository.
- Observed effect: an unrelated legacy CRLF file could fail Build 0048 even though every Build 0048-owned script was ASCII-only and LF-normalised.
- Root cause: the test scope used `ROOT.rglob("*")` rather than the exact paths declared in the Build 0048 Asset Intent Manifest.
- Time loss: a valid transactional apply was rolled back and the operator had to repeat the release gate.
- Corrective action: scope package hygiene assertions exclusively to exact manifest-owned paths and preserve unrelated predecessor files unchanged.
- Preventive control: the Windows PowerShell 5.1 synthetic repository now contains an unrelated historical CRLF PowerShell fixture; Build 0048 tests must pass while the fixture hash remains unchanged.
- Regression rule: repository-wide validation and build-owned package validation are separate controls. A build test must never claim ownership of unrelated historical paths through broad recursive matching.
