# Collision Resolution Report

## Summary

Three non-identical canonical path collisions were identified across the restoration sources. Each was resolved through an explicit compatible merge.

| Canonical path | Sources | Resolution |
|---|---|---|
| `13_Project_Genesis/Validators/control_library.py` | 0035K, 0036 | Combined helper library retaining both public function sets |
| `13_Project_Genesis/Schemas/audit_event.schema.json` | 0035K, 0036 | `oneOf` schema supporting both transition and general action audit events |
| `13_Project_Genesis/Registers/AUDIT_EVENT_REGISTER.csv` | 0035K, 0036 | Superset column structure supporting both event models |

Python cache files and compiled `.pyc` files were excluded as generated artefacts.
