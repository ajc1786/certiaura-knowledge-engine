# Build 0047 Decision Record

## Decision

Implement the Retatrutide longitudinal dashboard as a controlled information and review workflow, not autonomous clinical decision support.

## Controls

- Exact Asset Intent Manifest path ownership.
- Exact `CERT-BUILD-0047` provenance ownership.
- No build-number substring ownership matching.
- Pseudonymous identifiers by default.
- No autonomous dose, treatment or diagnosis actions.
- Provenanced and approved alert rules only.
- Draft clinician export until authorised human approval.
- Transactional backup outside the repository.
- Windows PowerShell 5.1 regression required before release.

## RC3 package-resolution decision

Byte-identical package copies are one approved package identity and may be deterministically deduplicated. Different package SHA-256 values are accepted only when the latest PASS regression report uniquely identifies the approved package; otherwise they remain a blocking conflict.

## RC5 Windows PowerShell 5.1 collection decision

Generic .NET lists in operator-critical Windows PowerShell 5.1 paths must be converted with explicit `.ToArray()` normalisation. The unary-array form applied directly to `List[object]` is prohibited because it can throw `Argument types do not match`.

## RC5 correction

Build 0047 preserves the Build 0045 longitudinal journey schema and any pre-existing shared ownership helper. Build 0047 uses build-specific paths and performs complete canonical path collision inventory during dry run before any apply transaction.

## RC6 canonical test execution and rollback decision

The canonical operator must execute Build 0047 tests through `unittest discover` with an explicit start directory and pattern. Passing an absolute file path to `python -m unittest` is prohibited. Any post-apply failure before local commit must automatically restore the external transactional backup, remove exact `CREATE_FILE` paths from the apply report and verify a clean repository before stopping.

## RC7 regression variable decision

The Windows PowerShell 5.1 regression must use one canonical external backup-root variable for every synthetic apply. A stale or undeclared alias is prohibited under StrictMode. The variable must be explicitly validated before clean reapply.
