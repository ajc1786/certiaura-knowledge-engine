# Build 0048 Rollback Runbook

The canonical runner automatically invokes `13_Project_Genesis/Import/rollback_build_0048_pending_import.py` after any post-apply, pre-commit failure. The helper requires the exact apply report, package SHA-256 and external transactional backup, verifies imported file hashes, restores the Master Asset Register, resets the Git index and requires a clean Git status. Do not manually delete imported files or edit the register during rollback.
