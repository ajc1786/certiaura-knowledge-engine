# Retatrutide Unresolved-Action Escalation Workflow

Build provenance: `CERT-BUILD-0050`

Open actions are classified as `INFORMATION`, `DATA_CORRECTION`, `CLINICAL_REVIEW`, `EXPORT_AMENDMENT` or `URGENT_ROUTING`. Each action has an owner role, due date, evidence link and status.

Overdue clinical-review or export-amendment actions escalate to `ESCALATION_REQUIRED`. Urgent-routing actions remain `LOCKED_URGENT_ROUTING` until an authorised human resolution is recorded. Administrative closure cannot downgrade an urgent state.
