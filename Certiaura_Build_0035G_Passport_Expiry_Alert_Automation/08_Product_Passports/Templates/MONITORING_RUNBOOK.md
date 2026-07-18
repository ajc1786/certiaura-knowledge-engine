# PRODUCT PASSPORT™ MONITORING RUNBOOK

## Before each production run

- Confirm 0035D, 0035E and 0035F are installed and repository validation is passing.
- Confirm the monitoring policy version and threshold matrices are current.
- Use Coordinated Universal Time and record the as-of timestamp.
- Acquire the production run lock.
- Snapshot or hash all source lifecycle records.
- Confirm alert routes are available.

## Execute

```text
python 13_Project_Genesis/Automation/run_passport_monitor.py INPUT_PATH --output monitoring_run.json --as-of 2026-07-18T09:00:00Z --run-id PPS-MON-20260718-001
```

The supplied engine is read-only and does not modify lifecycle records.

## Validate

```text
python 13_Project_Genesis/Validators/validate_passport_monitoring_run.py monitoring_run.json
```

## Release gate

- Review all P0 and P1 alerts first.
- Confirm protective transactions are separately recorded before treating them as applied.
- Confirm notification acknowledgement for critical alerts.
- Append accepted run and alert records to the relevant registers.
- Commit only after repository validation passes.

## Failure handling

- `FAILED`: investigate; do not claim the portfolio was checked.
- `PARTIAL`: identify unscanned records and rerun.
- `STALE_INPUT`: discard automatic-action instructions and scan the latest source version.
- Notification delivery failure: route through the fallback operations queue.
