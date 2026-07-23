# Build 0053 Lessons-Learned Review

## Review outcome

No source-package defect was accepted as normal. The build converts two recurrent risk classes into executable controls:

1. Partial cross-surface propagation after an approved change.
2. Premature closure at publication without post-change effectiveness evidence.

## Preventive controls

- Exact expected/applied target-set equality.
- Human scientific and governance approval.
- Publication state transition gates.
- Evidence-linked effectiveness review.
- Reopening and rollback decisions.
- Canonical Git-derived predecessor evidence and explicit overlap controls.

## RC1 real-world regression defect

RC1 was withdrawn after the Windows PowerShell 5.1 temporary-clone regression proved that its synthetic Master Asset Register fixture had invented formal-asset rows for three governance control files. The real Build 0052 repository contains the files but does not register them as formal assets.

RC2 corrects their Asset Intent classification to `NON_ASSET_ADMIN`, preserves transactional ownership and rollback, and adds a regression requiring successful import when those predecessor governance paths are absent from the Master Asset Register.

## Permanent preventive control

Synthetic predecessor fixtures must reproduce both canonical predecessor files and canonical register topology. A test fixture must never create a Master Asset Register row merely to make an `UPDATE` test pass.

## RC2 Windows staged-byte defect

RC2 passed package validation, predecessor derivation, forced rollback and clean reapply, but the Windows PowerShell 5.1 temporary-clone gate detected four runtime-generated JSON reports whose CRLF working-tree bytes differed from Git-normalised LF index bytes. The canonical repository was not applied.

RC3 forces `newline="\n"` for every production Python `Path.write_text` call and introduces an AST regression that blocks any future production writer lacking the explicit LF policy. The raw staged-byte gate remains mandatory.

## RC3 post-import scope and rollback-order defect

RC3 passed package validation, rollback, clean reapply, staged-byte equality and the temporary-clone commit/push regression. Four tests then failed only after canonical apply because they scanned the entire historical repository rather than the exact Build 0053 Asset Intent Manifest scope. The transactional backup restored the canonical repository exactly to Build 0052; no commit or push occurred.

RC4 scopes examples, roots, inventory coverage and Python writer audits to Build 0053-owned package paths. The complete repository validator and `test_build_0053_*.py` suite now run in the temporary clone before canonical apply. If any later canonical validation, staging, Git hygiene or byte-equality gate fails, the runner invokes the transaction backup automatically and requires `ROLLBACK_STATE_EXACT` before returning the failure.
