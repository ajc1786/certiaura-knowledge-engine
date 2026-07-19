# CERTIAURA BUILD 0038 — READ FIRST

**Build ID:** CERT-BUILD-0038  
**Build title:** repository restoration canonical routing and Master Asset Register reconciliation for Builds 0035E to 0036  
**Package version:** 1.2.0 corrected reissue  
**Authorisation:** GREEN_AUTHORISED  
**Delivery state:** GENERATED / DELIVERED — canonical implementation requires transactional import, validation, commit, push and GitHub Actions green  
**Build date:** 2026-07-19

## Purpose

This all-in-one recovery pack restores the deleted outputs of Builds 0035E through 0036 directly into canonical repository paths and upgrades Project Genesis so the existing Master Asset Register is reconciled automatically in the same rollback-safe transaction.

## Critical controls

- No top-level build wrapper folder.
- Every package file is classified in `ASSET_INTENT_MANIFEST.json`.
- The existing canonical Master Asset Register must resolve uniquely; no replacement register is supplied.
- Existing Universal Asset Identifiers are preserved.
- New identifiers are allocated only when no genuine existing asset match exists.
- Non-identical collisions are blocked unless expressly listed in `CONFLICT_POLICY.json`.
- Dry-run routing and Asset Register Change Reports are mandatory before apply.
- File routing, register changes and checkpoint changes roll back together if validation fails.

## Project Genesis dry run

```text
python 13_Project_Genesis/Import/transactional_build_import.py <build_zip> <repository_path> --report <dry_run_report.json>
```

Review the routing plan and Asset Register Change Report. Resolve any ambiguous register location, duplicate identifier, path collision or asset identity conflict before apply.

## Project Genesis apply

```text
python 13_Project_Genesis/Import/transactional_build_import.py <build_zip> <repository_path> --apply --report <import_report.json>
```

## Locked commit message

```text
Add Certiaura Build 0038 repository restoration canonical routing and Master Asset Register reconciliation for Builds 0035E to 0036
```

## Next action

After successful import and repository validation, commit and push using the exact message above and confirm GitHub Actions green. Then reissue Build 0037 with flat routing and automatic Master Asset Register reconciliation.
