
# Build 0041 rollback runbook

- The apply runner requires `CERTIAURA_BACKUP_ROOT` and creates a timestamped external backup before writing.
- The backup covers the canonical Master Asset Register, continuity checkpoint and every existing target file.
- Any write, register, checkpoint or validation exception triggers restoration of backed-up files and deletion of newly created paths.
- A failed or unresolved transaction backup must be retained outside the repository under the locked Certiaura backup path.
- Commit and push are prohibited until post-import validation passes.
