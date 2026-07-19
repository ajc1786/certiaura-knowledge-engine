# Build 0038 — Read Me First

**Title:** repository restoration and canonical routing for Builds 0035E to 0036  
**Status:** Repository-ready restoration package  
**Commit message:** `Add Certiaura Build 0038 repository restoration and canonical routing for Builds 0035E to 0036`

## Purpose

This is the single all-in-one recovery package requested after the incorrectly routed folders for Builds 0035E–0036 were deleted from the repository.

## Import behaviour

The ZIP has no outer build-name folder. Its root mirrors the canonical repository. Import it through Project Genesis, review the dry-run collision report, validate the repository, commit and push, then confirm GitHub Actions green.

## Restored builds

0035E, 0035F, 0035G, 0035H, 0035I, 0035J, 0035K and 0036.

## Collision decisions

Three paths differed between Builds 0035K and 0036. Build 0038 supplies compatible merged versions of:

- `13_Project_Genesis/Validators/control_library.py`
- `13_Project_Genesis/Schemas/audit_event.schema.json`
- `13_Project_Genesis/Registers/AUDIT_EVENT_REGISTER.csv`

No source was silently overwritten.
