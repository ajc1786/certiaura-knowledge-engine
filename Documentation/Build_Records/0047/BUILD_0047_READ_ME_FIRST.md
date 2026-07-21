# Certiaura Build 0047 - Read First

**Build ID:** `CERT-BUILD-0047`
**Build title:** retatrutide controlled longitudinal dashboard, alert review workflow and clinician export baseline
**Status:** `GENERATED_CANDIDATE_WINDOWS_PS51_GATE_REQUIRED`
**Package version:** `1.0.0-rc7`
**Date:** 2026-07-21

## Purpose

Build 0047 adds an operational, evidence-provenanced Retatrutide longitudinal dashboard, controlled alert review workflow, clinician export contract, generator, validators, examples, tests and transactional import controls.

## Safety boundary

The package does not diagnose, prescribe, change dose, authorise use or establish that review is unnecessary. It produces auditable trend summaries and human-review states only.

## Mandatory pre-release gate

Run `Scripts/Invoke_Certiaura_Build_0047_Windows_PS51_Regression.ps1` through the approved delivery command before canonical import.

Required endpoint:

`BUILD 0047 WINDOWS POWERSHELL 5.1 REGRESSION: PASS`

The regression uses a temporary synthetic Git repository and local bare remote. It does not modify the canonical repository.

## Canonical operator entry point after regression PASS

Extract the approved ZIP outside the repository and run:

`Scripts\START_BUILD_0047.cmd`

The canonical operator script verifies the passed regression report and matching package SHA-256 before allowing dry-run or import.

## RC3 operator-resilience correction

The canonical package resolver now treats multiple byte-identical copies of the approved ZIP as one package identity and selects the newest copy deterministically. Where multiple package revisions exist, the latest PASS regression report selects the approved full package SHA-256; unmatched or unapproved revisions remain fail-closed.

## RC5 Windows PowerShell 5.1 collection correction

The canonical package resolver converts its generic `List[object]` using explicit `.ToArray()` normalisation before `.Count` or indexing. The incompatible `$ApprovedMatches = @($Matches)` expression is prohibited and regression-tested.

## RC5 correction

Build 0047 preserves the Build 0045 longitudinal journey schema and any pre-existing shared ownership helper. Build 0047 uses build-specific paths and performs complete canonical path collision inventory during dry run before any apply transaction.


## RC6 canonical test and rollback correction

- The canonical launcher uses `python -m unittest discover` with an explicit test root and filename pattern; an absolute Windows path is never passed as a module name.
- Any failure after apply and before local commit automatically invokes the Build 0047 rollback helper.
- Rollback uses the exact apply report and external transactional backup, verifies imported file hashes before deletion or restoration, resets the index, restores the Master Asset Register and requires a clean Git working tree.
- The uncommitted RC5 transaction must be rolled back before RC6 regression and canonical import.

## RC7 Windows PowerShell 5.1 regression correction

- RC6 completed the controlled RC5 rollback and reached the isolated synthetic regression.
- The clean synthetic reapply referenced an undeclared `$BackupRoot` variable under StrictMode.
- RC7 reuses the defined `$ExternalBackupRoot` for both synthetic applies and validates it before the second apply.
- The canonical repository remains clean and unmodified by RC6.
- The full Windows PowerShell 5.1 regression must be rerun for the RC7 package SHA-256 before canonical import.
