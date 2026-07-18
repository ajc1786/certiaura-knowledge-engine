# Build 0035H Implementation Notes

## Integration points

- Consume 0035G alert identifiers and source hashes when creating a remediation case.
- Link refreshed evidence to the existing 0035D submission and 0035E review structures.
- Apply passport transactions through the 0035F lifecycle controls.
- Apply marketplace transactions separately through the Marketplace System.
- Update existing registers rather than creating competing masters.

## Recommended Project Genesis sequence

1. Dry-run assessment and blocker display.
2. Case and action register user interface.
3. Evidence-refresh intake and reviewer routing.
4. Four-eyes approval workflow.
5. Audited passport transaction.
6. Separate marketplace transaction and acknowledgement.
7. Alert closure reconciliation.
8. Supplier dashboard and scheduled performance review.

## Data migration

No automatic migration is included. Historical alerts and supplier cases should be imported through a controlled mapping exercise so source identifiers, hashes and decisions remain traceable.

## Security

Approval roles, supplier identities, evidence files and marketplace transactions should be access-controlled. Production implementation should prevent the same account from acting as both primary reviewer and second approver.
