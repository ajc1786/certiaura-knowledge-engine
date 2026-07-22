# Build 0052 Decision Record

Build 0052 RC1, RC2, RC3 and RC4 are withdrawn and prohibited from import.

RC6 is the active corrective candidate. It retains runtime predecessor evidence derived only from canonical Git objects, preserves exact predecessor isolation, and introduces a version-aware cumulative-lessons adapter for valid historical matrices that predate the current schema.

Historical schema migration is permitted only for prior builds and must record the source path, build number, record index, alias or controlled default, and deterministic identifier basis. The current Build 0052 matrix remains strict and missing required fields block release.

Transactional rollback failures must be operator-visible without a separate diagnostic. The importer prints `BUILD_0052_TRANSACTION_ROLLED_BACK` with the exact reason, report and backup paths, and the Windows wrapper reads the failure report before throwing.
RC6 pre-delivery regression also corrected same-build cumulative lesson replay: replaying already embedded Build 0052 origins is idempotent, but a genuinely new recurrence without a strengthened control remains blocked.

## RC4 decision correction

RC4 is withdrawn because its Windows regression falsely failed a valid rollback token assertion. RC6 is the active candidate and does not weaken rollback or predecessor controls.

Build 0052 RC5 was withdrawn after canonical runtime proved that Builds 0039, 0040 and 0043-0046 have no retained per-build lessons matrices. RC6 validates those legacy builds through exact SHA-256-bound lesson-ID sets already present in the authoritative cumulative ledger and prohibits fabricated matrices.


## Matrix-or-ledger historical coverage decision

RC6 may treat a legacy build as covered without a physical matrix only when that build is explicitly declared in `ledger_only_historical_evidence`, the exact existing cumulative-ledger lesson-ID set matches, the SHA-256 binding matches, every lesson contains the required fields and every lesson retains that build in `origin_builds`. Synthetic replacement matrices are prohibited.
