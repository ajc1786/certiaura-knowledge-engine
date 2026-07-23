# Build 0056 rollback runbook

The importer creates an external transactional backup before applying any owned path. A forced post-apply failure must return `ROLLBACK_STATE_EXACT`. If a later canonical gate fails, the launcher automatically invokes rollback using the returned backup path. Closure is prohibited unless the repository is clean.
