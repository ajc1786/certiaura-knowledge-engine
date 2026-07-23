# Build 0059 rollback runbook

The Project Genesis importer creates a transaction backup before applying any owned path. Any post-apply validation failure restores prior bytes and removes newly created paths. A failed import must return `ROLLBACK_STATE_EXACT`; unresolved backups must be retained outside the repository.
