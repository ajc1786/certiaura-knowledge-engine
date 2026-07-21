# Retatrutide Governed Case Reopening Workflow

**Build provenance:** CERT-BUILD-0051

1. Record a surveillance trigger with source and timestamp.
2. Verify the trigger is linked to the closed case and Build 0050 closure record.
3. Apply urgent-routing precedence.
4. Require an authorised human reviewer independent from the surveillance generator.
5. Record `REOPEN_APPROVED`, `REOPEN_REJECTED`, `MORE_INFORMATION_REQUIRED` or `LOCKED_URGENT_ROUTING`.
6. Where reopening is approved, create a new governed review cycle without altering the historical closure artefact.
7. Preserve trigger, evidence, reviewer and decision hashes in the audit bundle.

Administrative queries cannot reopen a case automatically. Artificial intelligence may summarise evidence but cannot make the reopening decision.
