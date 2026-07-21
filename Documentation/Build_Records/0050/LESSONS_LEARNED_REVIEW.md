# Build 0050 Lessons-Learned Review

## Accumulated prior-build lessons reviewed: PASS

All durable controls through Build 0049 were applied: exact Asset Intent Manifest ownership, exact provenance, realistic predecessor fixtures, dry-run collision inventory, external backup, automatic rollback, exact canonical command regression, Windows PowerShell 5.1 collection normalisation, StrictMode-safe empty collections, ASCII-only PowerShell, LF hygiene, memory-only Python compilation, no runtime artefacts and both Git checks.

## Current-build lessons recorded: PASS

### Closed-loop governance lesson

- Risk: a case may be administratively closed while urgent routing, open actions, export amendments or evidence gaps remain unresolved.
- Corrective design: closure readiness is deterministic and fail-closed; urgent routing has precedence; open actions and evidence snapshots are reconciled; quality assurance is independent.

### Build 0049 semantic-regression lesson

- Risk: static regression checks may reject correct code because of formatting differences.
- Preventive control: Build 0050 uses semantic, whitespace-tolerant checks for exact manifest ownership and prohibits brittle one-line literal assertions.

## Lessons converted to regression controls: PASS

- Closure with urgent routing or open blocking actions is rejected.
- Direct identifiers and autonomous treatment language are rejected.
- Invalid reconciliation hashes are rejected.
- Generator/reviewer role separation is enforced.
- Exact Build 0049 predecessor assets are preserved unchanged.
- Unrelated historical CRLF content is preserved and excluded from build-owned hygiene.
- Post-apply failure automatically rolls back before commit.

## Continuity checkpoint updated: PASS

Build 0049 is recorded as `ACTIONS_GREEN_CLOSED`; Build 0050 is the active generated candidate.


## RC2 real-world validator ownership lesson

- Defect: the first canonical apply passed, but the post-apply validator scanned every JSON file in the shared `12_Reports/Retatrutide/Examples` directory.
- Root cause: the validator used `glob('*.json')` instead of resolving exact Build 0050 `EXAMPLE` paths from the Asset Intent Manifest.
- Real-world effect: legitimate Build 0048 and Build 0049 examples were evaluated as if they were Build 0050-owned and caused the validator to fail.
- Transaction outcome: automatic post-apply rollback completed with `BUILD 0050 POST-APPLY ROLLBACK: PASS`; no Build 0050 commit or push occurred.
- Corrective action: the validator now loads `Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json` and validates only paths classified `EXAMPLE` with exact `CERT-BUILD-0050` provenance.
- Preventive control: the synthetic repository now contains a Build 0049 predecessor example deliberately carrying language that would fail Build 0050 rules if a shared-folder scan returned.
- Release regression: RC2 requires the predecessor example to remain unchanged and excluded while all Build 0050-owned examples are checked.
