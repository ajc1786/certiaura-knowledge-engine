# Certiaura Build 0040 — Read First

**Build title:** automated build-package preflight synthetic repository import and release integrity controls
**Build ID:** CERT-BUILD-0040
**Build date:** 2026-07-20
**Status:** DELIVERED — corrected reissue; import pending
**Primary system:** SYS (Platform System)
**Dependency:** Build 0039 closed at commit `87624e9f1a9623d57c2ba583ecc5957754d8f527`

## Purpose

Build 0040 converts the release lessons from Build 0039 into executable, blocking controls for every future package.

This corrected reissue also closes the importer-compatibility defect found during the first Build 0040 installation attempt.

## Corrected capability

The package installs:

- a build-neutral transactional importer that discovers build number, title, package version and build-record paths from the candidate ZIP;
- a dedicated Build 0040 transactional runner;
- PowerShell-first dry-run and apply execution;
- real importer dry-run and apply testing inside the synthetic Git repository;
- realistic Master Asset Register reconciliation and automatic Universal Asset Identifier allocation;
- transaction backup and journal verification;
- rejection of prior-build hard-coded metadata or report routing;
- final-ZIP manifest, inventory, checksum, text and runtime-artefact controls;
- staged `git diff --check` and `git diff --cached --check` gates;
- regression tests including a deliberately defective prior-build importer.

## PowerShell import sequence

The corrected ZIP is executed from PowerShell without File Explorer navigation.

Dry run:

```powershell
& "Scripts\Invoke_Certiaura_Build_0040_Import.ps1" `
    -Package "<BUILD_0040_ZIP>" `
    -Repository "<CERTIAURA_REPOSITORY>"
```

Apply only after the dry-run report is verified:

```powershell
& "Scripts\Invoke_Certiaura_Build_0040_Import.ps1" `
    -Package "<BUILD_0040_ZIP>" `
    -Repository "<CERTIAURA_REPOSITORY>" `
    -Apply
```

## Acceptance result

The exact corrected ZIP must pass:

- package self-validation;
- actual transactional importer dry run;
- actual transactional importer apply transaction;
- current-build metadata verification;
- Master Asset Register reconciliation;
- transaction backup and journal checks;
- unrelated historical file preservation;
- both staged Git diff checks;
- zero deletions, residue or runtime artefacts.
