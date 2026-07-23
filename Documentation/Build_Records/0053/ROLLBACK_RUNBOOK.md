# Build 0053 Rollback Runbook

1. Stop before commit or push.
2. Use the external transaction backup recorded in the import report.
3. Restore every pre-existing owned path from `files/<repository-relative-path>`.
4. Delete a Build 0053-created path only when its current SHA-256 still equals the transaction-applied SHA-256.
5. Restore the Master Asset Register with the same transaction.
6. Verify `git status --porcelain` is empty and `HEAD` remains the Build 0052 canonical commit.
7. Retain failed-import reports and copy the backup outside the repository.

The automated forced-failure regression must return `ROLLBACK_STATE_EXACT` before canonical apply.
