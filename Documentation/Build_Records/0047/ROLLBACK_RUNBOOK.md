# Build 0047 Rollback Runbook

1. Stop the operator workflow and do not commit.
2. Confirm the backup path recorded in the apply report is outside the repository.
3. Restore overwritten files and `Documentation/Master_Asset_Register.csv` from that backup.
4. Remove newly created Build 0047 paths listed in the apply report.
5. Run repository validation, `git status`, `git diff --check` and `git diff --cached --check` as applicable.
6. Restart OneDrive only after repository integrity is confirmed.
7. Retain the failed backup and reports until the defect is resolved and lessons are recorded.

## RC5 correction

Build 0047 preserves the Build 0045 longitudinal journey schema and any pre-existing shared ownership helper. Build 0047 uses build-specific paths and performs complete canonical path collision inventory during dry run before any apply transaction.

## RC6 automatic rollback

The canonical runner now invokes `13_Project_Genesis/Import/rollback_build_0047_pending_import.py` automatically for any failure after apply and before commit. The helper verifies the package hash, refuses to delete imported files whose hashes changed, restores approved replacements and the Master Asset Register from the external backup, resets the Git index and requires a clean working tree. The backup and reports are retained.
