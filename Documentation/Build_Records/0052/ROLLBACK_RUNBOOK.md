# Build 0052 RC6 Rollback Runbook

Build 0052 uses an external transactional backup and preserves the pre-import Git index.

A forced post-apply failure must return exit code 3, emit `BUILD_0052_TRANSACTION_ROLLED_BACK`, record `transaction_status=ROLLED_BACK`, `rollback_completed=true`, the exact `rollback_reason`, report path and backup path, and restore every build-owned path and the Git index.

RC6 must also prove the clean reapply succeeds after rollback. If any apply stage fails, do not manually edit the repository; retain the external backup and failure report for diagnosis.
