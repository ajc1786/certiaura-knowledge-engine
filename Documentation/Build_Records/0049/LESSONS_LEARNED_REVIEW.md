# Build 0049 Lessons-Learned Review

## Accumulated prior-build lessons reviewed: PASS

Build 0049 carries forward all durable controls through Build 0048, including exact manifest path and provenance ownership, realistic predecessor fixtures, collision detection during dry run, external transactional backup, automatic post-apply rollback, exact canonical command regression, Windows PowerShell 5.1 collection normalisation, StrictMode-safe empty collections, ASCII-only PowerShell, LF hygiene, memory-only Python validation, no runtime artefacts and both Git whitespace checks.

## Current-build lessons recorded: PASS

### Pre-production workflow lesson

- Risk: a controlled handoff can be acknowledged or followed up without preserving the meaning boundary between receipt and clinical agreement.
- Corrective design: acknowledgement is explicitly receipt-only; urgent routing remains locked; feedback is triaged; amendments create new immutable versions.

### Build 0048 carry-forward lesson

- Risk: build-specific tests can fail on unrelated historical files when ownership is inferred through broad repository scanning.
- Preventive control: every Build 0049 hygiene test is limited to exact Asset Intent Manifest paths. The synthetic repository includes an unrelated historical CRLF PowerShell fixture and realistic Build 0048 predecessor assets whose hashes must remain unchanged.

## Lessons converted to regression controls: PASS

- Direct identifiers and autonomous treatment language are blocked.
- Urgent routing cannot be downgraded.
- Amendment self-cycles, in-place export mutation and same-actor approval are blocked.
- Exact Build 0048 predecessor paths are present and hash-verified unchanged.
- All package collisions are inventoried during dry run.
- Exact canonical operator commands are mirrored in Windows PowerShell 5.1 regression.
- Post-apply failures trigger automatic rollback before commit.

## Continuity checkpoint updated: PASS

Build 0048 is recorded as `ACTIONS_GREEN_CLOSED`; Build 0049 is the active generated candidate and the Windows PowerShell 5.1 regression is the release blocker.

### RC2 Windows PowerShell 5.1 scope-assertion lesson

- Defect: the pre-release regression required an exact one-line literal `manifest=self.load(...)`, while the correctly scoped Python test used PEP 8 spacing and a multiline call.
- Root cause: a formatting-sensitive static assertion was used as a proxy for semantic ownership scope.
- Effect: the real Windows PowerShell 5.1 regression failed closed before canonical import even though the Build 0049 hygiene test correctly used exact Asset Intent Manifest paths.
- Corrective action: replace the brittle literal assertion with whitespace- and newline-tolerant regular expressions that verify both the exact manifest load and derivation of `owned_paths` from `manifest["files"]`.
- Preventive control: future operator regressions must validate code semantics robustly and must not require incidental formatting such as spaces or line breaks.
- Regression test: the package test suite now requires the tolerant manifest-scope patterns and prohibits the obsolete exact literal.
