# Certiaura Build 0043 — Read First

**Build title:** retatrutide patient journey report generation and AI query integration baseline
**Build ID:** CERT-BUILD-0043
**Version:** 1.0.1
**Build state:** CORRECTED REISSUE CANDIDATE - Windows PowerShell 5.1 release regression required
**Dependencies:** Build 0041 and Build 0042 at `ACTIONS_GREEN_CLOSED`

## Correction notice

The earlier Build 0043 ZIP is superseded and must not be imported. This reissue corrects a Windows PowerShell 5.1 parsing defect caused by Unicode punctuation in a UTF-8-without-BOM `.ps1` file. All Build 0043 PowerShell scripts are now ASCII-only with repository-normalised LF line endings, and the package includes permanent encoding regression controls.

## Purpose

Introduce a deterministic patient-journey report generator and a repository-grounded artificial intelligence query baseline for retatrutide. The implementation consumes the existing evidence, safety, monitoring, contraindication and clinical-outcome baselines and does not recreate them.

## Mandatory operator sequence

1. Use Windows PowerShell 5.1.
2. Confirm the canonical repository is clean and current.
3. Verify Build 0042 ancestry and closure checkpoint.
4. Run the bundled Windows PowerShell 5.1 synthetic-repository regression.
5. Run package preflight.
6. Run Project Genesis dry-run and review all reports.
7. Type `APPLY` only after the dry-run passes.
8. Stop OneDrive for transactional repository writes.
9. Apply with external backup and rollback controls.
10. Run validators and tests with Python bytecode disabled.
11. Confirm no runtime artefacts or unexpected deletions.
12. Stage all changes and run both Git whitespace checks.
13. Type `COMMIT` only after reviewing staged changes.
14. Push and verify GitHub Actions.
15. Complete lessons learned and closure evidence before recording `ACTIONS_GREEN_CLOSED`.

## Pre-release Windows PowerShell 5.1 regression command

After extracting the ZIP to a temporary folder, run the regression only:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Scripts\Invoke_Certiaura_Build_0043_Windows_PS51_Regression.ps1 -Package "<FULL_PATH_TO_ZIP>" -ReportRoot "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0043\Pre_Release"
```

Do not run the canonical import workflow unless `BUILD_0043_WINDOWS_PS51_REGRESSION.json` records `valid: true`.

## Exact commit message

`Add Certiaura Build 0043 retatrutide patient journey report generation and AI query integration baseline`
