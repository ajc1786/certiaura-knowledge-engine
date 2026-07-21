# Build 0049 Rollback Runbook

If any post-apply, pre-commit validation fails, the canonical launcher invokes `rollback_build_0049_pending_import.py` using the exact apply report and external transactional backup. Do not manually delete files or edit the Master Asset Register.
