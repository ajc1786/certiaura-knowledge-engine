# Build 0045 Lessons Learned Baseline

## Carried forward from Builds 0043 and 0044

- Windows PowerShell 5.1 scripts remain ASCII-only and parser checked.
- Any variable-cardinality collection is array-normalised before `Count` or indexing.
- Generated repository text is UTF-8 without BOM, LF-only, free of trailing whitespace and has one final newline.
- Both Git whitespace checks are mandatory.
- Cleanup and OneDrive restart complete before success is declared.
- Build ownership is derived from exact Asset Intent Manifest paths and Build Provenance, never numeric filename substrings.
- Transactional backup folders must be outside the repository. Internal `.certiaura_backups` content is a release blocker.
- Canonical Master Asset Register discovery must resolve exactly one active register.

## Build 0045 preventive tests

- A deliberately unrelated `CERT-BKS-000045` historical text fixture is preserved and excluded from Build 0045 hygiene scope.
- An internal backup duplicate register is deliberately created and must block dry-run.
- The same synthetic repository must pass after the internal backup is removed.
- Post-import validation failure is rollback-capable before commit.

## Build-generation runtime artefact prevention

- Example generation initially created a Python `__pycache__` directory inside the package staging tree.
- The package was corrected before release and the preflight now rejects `__pycache__`, `.pyc` and `.pyo` content.
- Build-generation commands must run with bytecode suppression or remove runtime artefacts before inventory and checksum sealing.

## Raw seed event enrichment defect

- The first real Windows PowerShell 5.1 regression failed closed while appending an urgent event to the packaged raw journey seed.
- The seed contained valid source events that had not yet been enriched with deterministic `event_id`, `prior_chain_hash` and `event_hash` fields.
- The append path sorted all prior events as though they were already enriched, causing `KeyError: event_id`.
- The correction normalises every existing and incoming event from its canonical core fields, recalculates the deterministic event identifier, sorts the complete set and rebuilds the hash chain.
- The exact command-line path is now covered by an automated test and by the Windows regression, including event-count, event-identifier and event-hash assertions.
- Future append-only ledger engines must accept their documented raw seed format as well as previously enriched ledger state.
## Expected native-command failure under Windows PowerShell 5.1

- The second real Windows PowerShell 5.1 regression reached the direct-identifier negative fixture and failed closed before the harness could inspect the expected non-zero Python exit code.
- The Python command correctly rejected the identifiable input, but wrote its traceback to the native stderr stream.
- With `$ErrorActionPreference = "Stop"`, Windows PowerShell 5.1 promoted that stderr record to a terminating `NativeCommandError`, bypassing the subsequent `$LASTEXITCODE` assertion.
- The correction temporarily changes `$ErrorActionPreference` to `Continue` only around the deliberately failing native command, captures `$LASTEXITCODE`, restores the original preference in `finally`, and verifies that no output file was created.
- Expected-negative native processes must be executed through an explicit non-terminating capture boundary; unexpected native failures remain fail-closed.
- A static automated regression now verifies that the Windows harness contains the preference save, temporary override, exit-code capture, restoration and rejected-output assertion.
