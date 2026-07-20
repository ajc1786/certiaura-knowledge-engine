# Build 0040 Rollback Runbook

## Automatic transaction protection

The build-neutral importer creates an external pre-import backup and `TRANSACTION_JOURNAL.json` before modifying repository files or the Master Asset Register.

If apply validation fails, the importer restores replaced files and the register, removes only unchanged transaction-created files, and removes only empty directories created by the transaction.

Recursive directory deletion is prohibited.

## Manual recovery

1. Stop further repository changes.
2. Read `backup_root` and `transaction_journal` from the guided import report.
3. Run the existing recovery utility against the recorded journal.
4. Confirm the repository and Master Asset Register match the pre-import state.
5. Run `git status --short --untracked-files=all` and repository validation.
6. Preserve failed-build evidence outside the repository until the issue is closed.
