# BUILD 0035G IMPLEMENTATION NOTES

## Integration target

The supplied monitoring engine is intentionally read-only. It produces an immutable monitoring-run object and alert queue. Project Genesis should later apply protective state changes only through repository-backed transactions that preserve the initiating run, alert, prior state, new state, actor and timestamp.

## Recommended first implementation

1. Run the engine daily against all current Product Passport lifecycle records.
2. Store each output under a date-partitioned monitoring-run path.
3. Validate the output before routing any alert.
4. Append run and alert summaries to the supplied registers.
5. Deliver P0/P1 notifications and record acknowledgement.
6. Keep automatic positive state changes disabled.

## Important limitations

- The included script does not send email, messages or external notifications.
- It does not mutate source lifecycle records.
- It does not perform legal or regulatory interpretation.
- It does not replace evidence review or marketplace approval.
- Production locking, retries, transaction application and secret management remain integration tasks.
