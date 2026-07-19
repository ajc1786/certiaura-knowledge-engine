# Build 0037 Transactional Rollback Runbook

Build 0037 must be imported through the transactional importer installed by Build 0038.

Before apply, the importer must create a recoverable checkpoint covering:

- every incoming or overwritten repository file;
- `Documentation/Master_Asset_Register.csv`;
- relationship and applicable system registers;
- change log, Production Dashboard, build records and continuity checkpoint.

Any routing, collision, identifier, register, relationship, validator or repository-validation failure must restore the full pre-import state and delete newly created files.

Do not delete the backup or recoverable Git checkpoint until the exact commit is pushed and GitHub Actions are green.
