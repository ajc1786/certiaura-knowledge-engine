# Build 0038 rollback runbook

The transactional importer creates `.certiaura_backups/build_0038_<UTC timestamp>/` before modifying the repository. The backup includes every overwritten file, the canonical Master Asset Register and a rollback manifest. Any routing, reconciliation or validation failure triggers automatic restoration of previous files and deletion of newly created files.

Do not delete the backup until the commit has been pushed and GitHub Actions are green.
