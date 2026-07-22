# Build 0052 RC6 Lessons Learned Review

## Candidate history

- RC1: withdrawn because predecessor truth was candidate-authored.
- RC2: withdrawn because predecessor manifest parsing assumed only `repository_path`.
- RC3: withdrawn after canonical clean reapply rejected the valid Build 0041 historical lesson schema; rollback completed.
- RC4: withdrawn after a collection-valued PowerShell `-notmatch` assertion falsely rejected a valid rollback token.
- RC5: withdrawn after canonical runtime proved that Builds 0039, 0040 and 0043-0046 have no retained per-build lesson matrices; rollback completed and the repository returned to the approved six-file precursor state.
- RC6: active corrective candidate pending canonical Windows PowerShell 5.1 regression.

## RC5 root cause

The updater treated complete historical coverage as synonymous with discovering a physical `LESSONS_LEARNED_CONTROL_MATRIX.json` for every expected build. That rule was too narrow for legacy builds created before universal per-build matrix retention. The locked cumulative ledger already contains multiple exact lessons attributed to each affected build, but RC5 did not recognise that authoritative evidence mode.

## RC6 corrective action

RC6 uses a two-mode, fail-closed coverage contract:

1. A canonical per-build matrix is required and migrated with recorded provenance whenever it exists.
2. An explicitly declared legacy build without a canonical matrix may be covered only by the exact lesson-ID set already present in the authoritative cumulative ledger, bound by SHA-256 and validated for required fields and origin attribution.

RC6 does not create or infer replacement historical matrices. Undeclared missing builds, altered lesson sets, digest mismatches, missing lesson IDs and origin mismatches remain release-blocking. The current Build 0052 matrix remains strict and cannot use the historical adapter.

RC6 also retains the prior schema migration, same-build replay idempotence, transactional failure visibility and scalar native-output controls.

## Regression requirements

- Canonical matrices present for retained historical builds: pass through exact scan and version-aware migration.
- Canonical matrices absent for Builds 0039, 0040 and 0043-0046: pass only through the declared exact SHA-256-bound cumulative-ledger evidence.
- Undeclared missing build: fail.
- Altered lesson ID, digest or origin attribution: fail.
- Fabricated historical matrix: prohibited.
- Current Build 0052 missing any required field: fail.
- Forced post-apply rollback: return exit code 3 and display the stable failure code and exact reason.
- Clean transactional reapply after rollback: pass.
- Multi-line native output matching, both Git whitespace checks and raw index-byte equality: pass.
