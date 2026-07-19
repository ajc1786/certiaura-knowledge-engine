# BUILD 0038 — READ ME FIRST

**Corrected reissue:** Canonical Master Asset Register repair

This package supersedes every prior Build 0038 ZIP.

## Confirmed live target

`Documentation/Master_Asset_Register.csv`

The current legacy row `NO NEW UAI` is treated as a placeholder, removed during reconciliation, and replaced by permanent `CERT-[SYSTEM]-[NUMBER]` records generated from the full live repository census.

## Import behaviour

1. Project Genesis dry-runs routing and the historical asset census.
2. It backs up repository files and the exact canonical CSV.
3. It restores Builds 0035E–0036 to canonical paths.
4. It repairs and populates the exact CSV in the same transaction.
5. It validates identifiers, canonical paths, orphan coverage and the Project Genesis button-open target.
6. It rolls back the entire transaction if any mandatory check fails.

## Fallback for an older Project Genesis interface

Run `13_Project_Genesis/Import/Run_Master_Asset_Register_Repair.cmd`.

## Exact commit message

`Add Certiaura Build 0038 repository restoration canonical routing and complete historical Master Asset Register reconciliation`
