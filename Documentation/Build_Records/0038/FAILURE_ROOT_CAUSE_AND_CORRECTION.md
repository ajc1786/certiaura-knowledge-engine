# Build 0038 failure root cause and correction

## Observed live result

The transaction remained unapplied and the canonical register was preserved.

Live report summary:

- Repository files considered: 3,089
- Registerable files: 2,879
- Original register rows: 1
- Legacy placeholders identified: 1
- Total blocking conflicts: 814
- Duplicate incoming UAI groups: 15
- Duplicate UAI allocation conflicts: 238
- Duplicate UAI post-reconciliation conflicts: 238
- Unregistered historical asset coverage failures: 323

## Root cause 1 — identifiers were allocated before incoming identifiers were reserved

New identifiers were allocated while later census items already held those identifiers. This caused legitimate historical identifiers to collide with newly generated identifiers.

**Correction:** scan and reserve every valid existing and incoming identifier before allocating any new identifier.

## Root cause 2 — one asset was treated as several assets

Several JSON, Markdown and mapping files represented the same formal asset and explicitly used the same UAI. The prior logic treated this as an invalid duplicate and repeatedly replaced the canonical path.

**Correction:** consolidate all explicit shared-UAI representations into one Master Asset Register row. Select one canonical path and store the remaining paths in `Supporting Files`.

## Root cause 3 — coverage validation expected one row per file

Coverage validation required every physical representation to have its own register row.

**Correction:** coverage accepts a path when it is either the canonical `Repository Path` or appears in `Supporting Files`.

## Protective outcome

Rollback was correct. No manual register edits should be made. The corrected Version 1.4.0 importer must be used.
