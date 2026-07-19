# Collision Resolution Report

## Summary

Three non-identical canonical path collisions were identified across the restoration sources. Each was resolved through an explicit compatible merge.

| Canonical path | Sources | Resolution |
|---|---|---|
| `13_Project_Genesis/Validators/control_library.py` | 0035K, 0036 | Combined helper library retaining both public function sets |
| `13_Project_Genesis/Schemas/audit_event.schema.json` | 0035K, 0036 | `oneOf` schema supporting both transition and general action audit events |
| `13_Project_Genesis/Registers/AUDIT_EVENT_REGISTER.csv` | 0035K, 0036 | Superset column structure supporting both event models |

Python cache files and compiled `.pyc` files were excluded as generated artefacts.


## Live Master Asset Register reconciliation correction

The previous repair run identified two systemic identity-model conflicts:

| Conflict | Previous effect | Version 1.4.0 resolution |
|---|---|---|
| New UAI allocation collided with explicit historical UAI values appearing later in the census | 238 duplicate allocations and 238 post-reconciliation duplicates | Reserve every valid incoming UAI before allocating any new identifier |
| Several repository files explicitly represented the same formal asset and UAI | 15 duplicate incoming UAI groups and 323 coverage failures | Consolidate to one canonical register row and record other representations in `Supporting Files` |

The transaction remains blocked for genuine duplicate register rows, ambiguous identities, orphan active entries and non-identical file collisions.
