# Master Asset Register Canonical Repair Standard

**Build:** 0038  
**Status:** Active corrective control

## Canonical target

`Documentation/Master_Asset_Register.csv` is the only register updated and the only file opened by the Project Genesis Master Asset Register button.

## Mandatory repair behaviour

- Read and preserve valid existing `CERT-[SYSTEM]-[NUMBER]` identifiers.
- Recognise the legacy `Asset Name` column.
- Remove the `NO NEW UAI` placeholder row after its underlying repository assets are discovered.
- Scan all canonical repository roots, excluding tests, examples, build records, caches and temporary files.
- Allocate identifiers only to genuinely unregistered formal assets.
- Write the CSV atomically using a same-directory temporary file.
- Back up and roll back the register when validation fails.
- Verify that the exact canonical CSV contains at least ten valid asset rows, no placeholder, no invalid identifier, no duplicate identifier and no duplicate canonical path.
- Produce the repair, census and button-verification reports under `Documentation/Build_Records/0038/`.

## Fallback

If an older Project Genesis interface does not execute the package post-apply hook, run:

`13_Project_Genesis/Import/Run_Master_Asset_Register_Repair.cmd`
