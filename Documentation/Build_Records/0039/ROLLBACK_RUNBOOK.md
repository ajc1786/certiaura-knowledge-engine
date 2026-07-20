# Build 0039 Rollback and Recovery Runbook

1. Stop further repository writes.
2. Keep OneDrive paused.
3. Locate the external `TRANSACTION_JOURNAL.json` reported by the importer.
4. Run `python 13_Project_Genesis/Import/recover_failed_build_import.py <journal> <repository> --apply --report <external-report-path>`.
5. Confirm replaced files and the Master Asset Register were restored.
6. Confirm created files were removed only when their hashes were unchanged.
7. Confirm only transaction-created directories proven empty were removed.
8. Confirm pre-existing sibling files, folders and nested content remain.
9. Retain failed-import evidence outside the repository until resolved.

Never manually run recursive deletion against a canonical repository folder as part of Build 0039 recovery.
