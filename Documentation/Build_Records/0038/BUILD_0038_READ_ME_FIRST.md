# BUILD 0038 — READ ME FIRST

**Conflict-resolution reissue:** Version 1.4.0
**Status:** Supersedes every prior Build 0038 ZIP.

## Why the previous repair was rolled back

The live repository census identified 2,879 registerable files. The earlier algorithm incorrectly treated every physical file as a separate formal asset while also preserving Universal Asset Identifiers embedded in canonical JSON records.

That created:

- 238 identifier collisions during allocation;
- the same 238 duplicate identifiers after reconciliation;
- 15 shared-UAI representation conflicts;
- 323 historical-file coverage failures;
- 814 total blocking conflicts.

Rollback was therefore the correct protective outcome.

## Corrected identity model

One Universal Asset Identifier represents one formal asset.

When several files explicitly represent the same asset:

- one file is selected as the canonical `Repository Path`;
- the remaining representations are retained in `Supporting Files`;
- no duplicate Master Asset Register row is created;
- every incoming explicit identifier is reserved before new identifiers are allocated.

The package also excludes downloaded duplicate-suffix files such as `(1)` and `(2)` from formal asset registration.

## Confirmed live target

`Documentation/Master_Asset_Register.csv`

The `NO NEW UAI` placeholder is removed only after the conflict-free transaction passes all gates.

## Required process

1. Import this ZIP through Project Genesis.
2. Run the dry run.
3. Confirm the report shows zero blocking register conflicts.
4. Apply the transaction.
5. Open the Master Asset Register from the Project Genesis button.
6. Validate, commit, push and confirm GitHub Actions green.

## Exact commit message

`Add Certiaura Build 0038 repository restoration canonical routing and complete historical Master Asset Register reconciliation`
