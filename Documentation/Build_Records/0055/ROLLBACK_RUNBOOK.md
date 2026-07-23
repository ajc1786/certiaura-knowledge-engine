# Build 0055 Rollback Runbook

The importer creates an external transaction backup before apply. Forced failure must return `ROLLBACK_STATE_EXACT`. Any later canonical gate failure invokes automatic rollback and must restore the Build 0054 predecessor state with zero repository changes. Changes outside Build 0055 ownership block rollback rather than being overwritten.
