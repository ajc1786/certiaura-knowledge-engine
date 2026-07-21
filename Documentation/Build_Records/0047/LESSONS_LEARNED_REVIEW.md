# Build 0047 Lessons-Learned Review

## Carried-forward controls

- Full operator workflow, not package-only validation, is the release gate.
- Windows PowerShell 5.1 StrictMode requires array normalisation before `.Count` or indexing.
- Optional JSON properties must be created safely rather than assigned directly when absent.
- PowerShell and CMD files are ASCII-only.
- Text files use LF, no trailing whitespace and a final newline.
- Runtime artefacts are prohibited.
- Both Git whitespace checks are mandatory after staging.
- Transactional backups remain outside the repository.
- Asset ownership is based on exact manifest paths and exact build provenance.

## Build-specific preventive controls

- Clinical output is review-only and rejects autonomous treatment language.
- Direct identifiers are rejected from the default clinician export.
- Rule provenance and approval are mandatory.
- Sponsor topline results are explicitly separated from regulatory approval and peer-reviewed evidence.

## Corrected candidate release control

- The pre-release Windows PowerShell 5.1 regression is a separate executable gate and cannot perform the canonical import.
- The canonical operator refuses to proceed without a matching passed regression report and package SHA-256.
- The exact Build 0046 implementation commit is resolved by full commit subject and verified as an ancestor; build-number substring matching is prohibited.

## RC3 duplicate-package resolver defect

- Defect: the canonical launcher counted byte-identical ZIP copies found through Downloads, Dropbox Downloads or path aliases as separate conflicting packages.
- Root cause: candidate uniqueness was assessed by file occurrence rather than unique package content hash.
- Corrective action: candidates are now grouped by full package SHA-256 after the exact Asset Intent Manifest hash check.
- Preventive control: one unique package hash may have multiple physical copies; multiple revisions are resolved only through the latest PASS regression report package SHA-256; unmatched revisions remain fail-closed.
- Regression control: the test suite statically verifies the content-hash deduplication and distinct-package fail-closed branches.

## RC5 Windows PowerShell 5.1 generic-list conversion defect

- Defect: the canonical launcher failed at `$ApprovedMatches = @($Matches)` with `Argument types do not match` under Windows PowerShell 5.1.
- Root cause: the unary array operator was applied directly to a generic `System.Collections.Generic.List[object]`; package-level static checks did not execute that expression under Windows PowerShell 5.1.
- Corrective action: convert the list with `[object[]]$Matches.ToArray()` before `.Count` or indexing.
- Preventive control: prohibit direct `@($GenericList)` conversion in operator-critical PowerShell 5.1 paths.
- Regression control: the Python suite checks the canonical expression, and the Windows PowerShell 5.1 regression executes the same `.ToArray()` conversion and validates count, indexing and retained package data.
- Repository impact: none; the launcher failed before dry-run or canonical import.

## RC5 canonical path collision defect

- Defect: the RC4 apply transaction found a non-identical existing file at `Schemas/retatrutide_longitudinal_journey.schema.json`.
- Root cause: Build 0047 declared `CREATE` for a path already installed by Build 0045, while the synthetic repository did not include the predecessor path and the dry run did not inventory repository file collisions.
- Corrective action: preserve the Build 0045 schema unchanged; route the Build 0047 contract to `Schemas/retatrutide_longitudinal_dashboard_journey.schema.json`; route the ownership helper to `13_Project_Genesis/Validators/build_0047_asset_ownership.py`.
- Preventive control: every dry run now inventories all package paths against the canonical repository and blocks every unapproved non-identical collision before `APPLY`.
- Regression control: the synthetic repository includes predecessor schema and helper paths, verifies their hashes remain unchanged, and the test suite deliberately injects a non-identical collision that must fail during dry run.
- Repository impact: none; the RC4 transaction rolled back and reported `applied=false`, `valid=false`, and `FAILED_CLOSED`.


## RC6 canonical unittest invocation and post-apply rollback defect

- Defect: after a valid RC5 apply, the canonical launcher called `python -m unittest` with an absolute Windows `.py` path. Python interpreted the path as a module name and raised `ModuleNotFoundError`.
- Root cause: the pre-release regression executed the test file directly and did not mirror the exact canonical launcher invocation. The outer operator also treated apply as complete before all post-apply validators and tests had passed, so the failure left an uncommitted modified working tree.
- Corrective action: use `python -m unittest discover -s <absolute test directory> -p test_build_0047_retatrutide_dashboard.py`; add an exact static regression for the operator command; add a rollback helper invoked automatically after any post-apply, pre-commit failure.
- Preventive control: operator-critical command lines must be executed or mirrored exactly in the Windows PowerShell 5.1 regression, not replaced by semantically similar commands. Apply remains transactionally provisional until all validators, tests, runtime scans and Git hygiene gates pass.
- Rollback control: the helper uses the exact apply report and external backup, verifies imported file hashes before deletion or restoration, restores the Master Asset Register, resets the index and requires an empty `git status`.
- Repository impact: RC5 created 50 package paths and updated the Master Asset Register but did not stage, commit or push. The external backup at `Build_0047_Pre_Import_20260721_172826` remains available. Controlled rollback is mandatory before RC6 import.

## RC7 undefined synthetic backup-root defect

- Defect: RC6 failed during the second synthetic apply because `$BackupRoot` was referenced under StrictMode without being set.
- Root cause: the first synthetic apply used `$ExternalBackupRoot`, but the clean reapply used a stale variable name that was not exercised before the real Windows PowerShell 5.1 gate.
- Corrective action: reuse `$ExternalBackupRoot` for both synthetic applies and verify it is initialised immediately before the clean reapply.
- Preventive control: operator-critical variables must have one canonical name, be initialised before first use and be regression-checked for stale aliases.
- Regression control: the Python suite requires two exact `-BackupRoot $ExternalBackupRoot` invocations, prohibits `-BackupRoot $BackupRoot`, and requires the explicit initialisation guard.
- Repository impact: none. The RC5 controlled rollback completed before RC6 regression began, and RC6 failed in the temporary synthetic repository before canonical import.
