# Build 0054 Rollback Runbook

The importer creates an external transaction backup before apply. Forced failure must return `ROLLBACK_STATE_EXACT`. Any later canonical gate failure invokes automatic rollback and must restore the predecessor HEAD with zero status changes. Changes outside Build 0054 ownership block rollback rather than being overwritten.
