# CERTIAURA BUILD 0038 — READ FIRST

**Build ID:** CERT-BUILD-0038  
**Build title:** repository restoration canonical routing and complete historical Master Asset Register reconciliation  
**Package version:** 1.3.0 corrected reissue  
**Authorisation:** GREEN_AUTHORISED  
**Delivery state:** GENERATED / DELIVERED — canonical implementation requires transactional import, validation, commit, push and GitHub Actions green  
**Build date:** 2026-07-19

## Purpose

This superseding all-in-one recovery pack restores the deleted outputs of Builds 0035E through 0036 into canonical repository paths and performs a complete repository-wide Master Asset Register backfill for all prior registerable Certiaura items.

The backfill is not limited to the restored builds. It scans the existing repository, reads all available prior Build Records and file inventories, preserves established Universal Asset Identifiers, and allocates new identifiers only for genuinely unregistered assets.

## Registerable historical items

The census covers governance controls, knowledge assets, standards, schemas, templates, registers, validators, automation, scripts, dashboards, reports, calculators, controlled documentation, datasets and reusable media assets.

Build records, tests, examples, caches, temporary files and generated fixtures are excluded and reported rather than silently ignored.

## Critical controls

- No top-level build wrapper folder.
- Every package file is classified in `ASSET_INTENT_MANIFEST.json`.
- The existing canonical Master Asset Register must resolve uniquely; no replacement register is supplied.
- The whole existing repository is scanned for prior registerable items.
- Existing Universal Asset Identifiers are preserved.
- New identifiers are allocated only when no genuine existing asset match exists.
- Prior build provenance is recovered from Build Records and file inventories where available.
- Duplicate identifiers, ambiguous identity matches, orphan assets and active orphan register entries block import.
- Dry-run routing, historical census and Master Asset Register Change Reports are mandatory before apply.
- File routing, register changes, checkpoint changes and audit records roll back together if validation fails.

## Project Genesis dry run

```text
python 13_Project_Genesis/Import/transactional_build_import.py <build_zip> <repository_path> --report <dry_run_report.json>
```

Review:

- routing plan;
- full historical repository census;
- proposed UAI allocations;
- preserved identifiers;
- prior-build provenance;
- excluded non-assets;
- orphan and duplicate findings;
- complete Master Asset Register Change Report.

## Project Genesis apply

```text
python 13_Project_Genesis/Import/transactional_build_import.py <build_zip> <repository_path> --apply --report <import_report.json>
```

## Locked commit message

```text
Add Certiaura Build 0038 repository restoration canonical routing and complete historical Master Asset Register reconciliation
```

## Supersession

Do not import any earlier Build 0038 ZIP. Version 1.3.0 supersedes all earlier Build 0038 packages.

## Next action

After successful import and repository validation, commit and push using the exact message above and confirm GitHub Actions green. Then replace the GPT Project continuity source with the imported Version 1.3.1 checkpoint and reissue Build 0037 with flat routing and automatic Master Asset Register reconciliation.
