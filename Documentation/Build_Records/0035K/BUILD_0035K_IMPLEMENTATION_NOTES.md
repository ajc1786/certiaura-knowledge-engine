# Build 0035K Implementation Notes

- Import into the existing PPS, MPS, CIS, EKS, SKS and SYS folders.
- Reconcile proposed registers with canonical registers; do not create duplicates.
- Replace TBA identifiers with permanent Universal Asset Identifiers.
- Connect order gate checks to canonical supplier, contract, passport, batch, incident and legal-route records.
- Preserve human approval identity and append-only audit events.
- Configure alert delivery separately; this package generates files and does not send external notifications.
- Do not enable direct-sale order release until the applicable legal route has been explicitly approved and recorded.
