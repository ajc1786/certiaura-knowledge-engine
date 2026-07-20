
# Build 0041 lessons-learned review

## Inherited defects and root causes

1. **Build-specific importer assumptions** caused avoidable compatibility defects in Build 0040. Root cause: metadata and package identity were embedded in code rather than discovered from the package.
2. **Package-only validation was insufficient.** Root cause: earlier release checks did not reproduce installation into a Git repository containing unrelated history.
3. **Generated text normalisation and Git staging checks were too late.** Root cause: whitespace, line-ending and runtime-artifact controls were not a release-level gate.
4. **Scientific source maturity can be blurred.** Root cause: peer-reviewed papers, registry records and sponsor topline communications can be presented together without explicit status labels.
5. **Compound evidence can become detached from claims.** Root cause: documents may cite sources narratively without a machine-readable claim-to-evidence graph.

## Corrective actions implemented in Build 0041

- Package metadata is discovered from `BUILD_MANIFEST.json` and `ASSET_INTENT_MANIFEST.json`.
- The package includes a synthetic Git installation test with unrelated history, staged checks and preservation assertions.
- All generated text is UTF-8, LF normalised, trailing-whitespace free and final-newline controlled.
- Every evidence object records source type, publication status, peer-review status, primary identifier, limitations and provenance.
- Sponsor topline claims are conditional and registry records are prohibited from being represented as results.
- Every public claim is linked to one or more evidence IDs and to the Retatrutide flagship through a referentially validated graph.
- New UAIs remain unallocated until canonical register reconciliation.

## Time lost during this build

No canonical repository time was consumed because package production occurred outside the repository. The first pre-release pass identified two internal scientific-control defects: an exact investigational-status phrase mismatch and an incomplete registry/result regression assertion. Both were corrected before delivery, the package version was increased to 1.0.1, inventory and hashes were regenerated, and the complete gate was rerun.

## Preventive controls and regression evidence

- Evidence corpus validator and deliberately defective fixture.
- Unit tests for valid corpus, missing primary identifier, sponsor-topline conditional status and registry/result separation.
- Inventory, checksum, path-casing, wrapper-folder, runtime-artifact and normalisation checks.
- Synthetic dry-run and apply-mode transaction with external backup, register allocation, continuity delta, unrelated-history preservation and both Git diff checks.
- Release is blocked if any gate fails.

## Closure requirement

This review must be re-opened after the canonical import to record actual importer behaviour, defects, time lost, corrective actions and GitHub Actions evidence. Build 0041 must not reach `ACTIONS_GREEN_CLOSED` until that close-out section is completed and verified.

## Delivery integration correction â€” package v1.0.2

- **Defect:** The Build 0041 package and PowerShell implementation shortcut were initially issued as separate downloads.
- **Root cause:** The single-link delivery requirement had not yet been integrated into the build-generation template.
- **Time lost / exposure:** Additional download placement and package-selection steps were imposed on the founder, creating avoidable manual handling and wrong-ZIP risk.
- **Corrective action:** Retain Build 0041, add the shortcut under the canonical `Scripts/` route, issue one implementation bundle containing the importer-ready package and launcher, and pass the inner package SHA-256 to the launcher through a detached sidecar.
- **Preventive control:** Every future build generator and close-out checklist must produce and test the one-link implementation bundle as a mandatory delivery artefact.
- **Regression evidence:** Package v1.0.2 must pass package self-validation, Python compilation, corpus tests, synthetic dry-run/apply import, transactional register reconciliation, unrelated-history preservation and both Git whitespace checks.

## Windows PowerShell parser correction - package v1.0.3

- **Defect:** `Run_Certiaura_Build_0041.ps1` failed at parse time on Windows PowerShell 5.1 with a missing string terminator and closing-brace error.
- **Root cause:** The UTF-8 launcher had no byte-order mark and contained an em dash. Windows PowerShell 5.1 read the file using the active ANSI code page; one UTF-8 byte was interpreted as a smart double quote and terminated the string incorrectly.
- **Time lost / exposure:** One failed launch and the associated diagnosis. The script failed before repository verification or write operations, so no repository, register, backup or Git state was changed.
- **Corrective action:** Retain Build 0041, increase the package version to 1.0.3, replace non-ASCII executable-script characters, use the unittest discovery command in the launcher, regenerate inventory and hashes, and reissue the one-link bundle.
- **Preventive control:** Every `.ps1` and `.cmd` file must be ASCII-only unless a future explicit encoding standard and Windows PowerShell parser test supersedes this rule. Every bundle starter must run the native PowerShell parser against the launcher before execution.
- **Regression evidence:** Package preflight enforces ASCII compatibility; the test suite scans all executable Windows scripts; the corrected bundle includes a native parser precheck; and the complete package, synthetic import and Git validation gate is rerun.

## OneDrive scalar-path and interactive-paste correction - package v1.0.4

- **Defects:** The OneDrive restart function used `$Candidates[0]` after a pipeline that collapsed a single match to a scalar string, passing only `C` to `Start-Process`. During manual recovery, the full launcher was pasted into an interactive PowerShell session, so `param`, `try`, `catch` and `finally` no longer formed one script unit and required variables were never initialised. The import wrapper also attempted broad ZIP rediscovery instead of accepting the launcher-resolved package path.
- **Root causes:** Reliance on PowerShell pipeline cardinality semantics; an operator path that was not sufficiently constrained to the double-click starter; and duplicate package-discovery logic across launcher layers.
- **Time lost / exposure:** One failed OneDrive restart attempt and one invalid interactive paste sequence. The Build 0041 transaction did not begin, no package was applied, and no repository, Master Asset Register, backup, staging, commit or push state changed.
- **Corrective actions:** Retain Build 0041, increase package version to 1.0.4, iterate candidate executable paths directly, resolve the inner package only beside the launcher by exact SHA-256, pass its explicit path to the import wrapper, preserve and restore the prior backup environment variable, and make the starter pause on every exit.
- **Preventive controls:** No executable path may be selected by indexing an unnormalised pipeline result. One-click bundle launchers must use one package resolver and explicit path handoff. Instructions must prohibit pasting launcher source into an interactive shell. Static preflight gates and regression tests must enforce these controls.
- **Regression evidence:** Seven package tests, new full-path and explicit-package-handoff preflight gates, complete package self-validation, synthetic dry-run/apply, transactional backup and Master Asset Register reconciliation, and both mandatory Git whitespace checks.

<!-- CERTIAURA_BUILD_0041_CANONICAL_CLOSEOUT_BEGIN -->
## Canonical import and closure verification

**Verified on:** 2026-07-20T15:30:30
**Canonical import commit:** `a63fe923160e5bface3f794f068cbfaeb7a3cd9f`
**GitHub Actions verification method:** HUMAN_CONFIRMED_EXACT_COMMIT_CHECKS
**Dry-run report:** `C:\Users\enqui\OneDrive\Documents\CERTIAURA\Build_Reports\0041\BUILD_0041_DRY_RUN_20260720_135956.json`
**Apply report:** `C:\Users\enqui\OneDrive\Documents\CERTIAURA\Build_Reports\0041\BUILD_0041_APPLY_20260720_135956.json`
**Transactional backup:** `C:\Users\enqui\OneDrive\Documents\CERTIAURA\Backups\Build_0041_Pre_Import_20260720T130101Z`

### Actual canonical results

- Package files validated and applied: **49**
- Formal assets reconciled: **18**
- Universal Asset Identifiers allocated: **18**
- Allocated identifier range: **CERT-PKS-000433 to CERT-EKS-000776**
- Master Asset Register total after import: **2889**
- Evidence objects validated: **12**
- Regression tests passed: **7**
- Unexpected deletions: **0**
- Runtime artefacts: **0**
- Unstaged changes after staging: **0**
- `git diff --check`: **PASS**
- `git diff --cached --check`: **PASS**
- GitHub Actions for the canonical import commit: **GREEN**

### Actual defects and time lost

The real canonical import completed transactionally without repository, register or scientific validation failure. The implementation and close-out cycle exposed Windows PowerShell 5.1 encoding incompatibility, scalar executable-path indexing, broad package rediscovery, interactive source pasting, incorrect CMD caret escaping and generated Markdown trailing whitespace. The trailing-whitespace defect was blocked by git diff --cached --check before commit or push. The corrective controls are central trailing-whitespace normalisation, exact interrupted-run recovery, ASCII-only executables and native parser prechecks. The root causes, corrective actions, preventive controls and regression evidence are recorded in this review and the control matrix.

### Closure decision

All applicable Build 0041 lessons-learned controls are implemented and verified against the successful canonical import. Build 0041 is eligible for `ACTIONS_GREEN_CLOSED` after this close-out record is committed, pushed and its GitHub Actions workflow is confirmed green.
<!-- CERTIAURA_BUILD_0041_CANONICAL_CLOSEOUT_END -->
