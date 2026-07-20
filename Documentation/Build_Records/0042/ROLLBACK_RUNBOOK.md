# Rollback runbook

The importer creates an external transactional backup before repository writes. On mandatory validation failure it restores existing files, removes newly created package files, and restores the Master Asset Register and continuity checkpoint together.
