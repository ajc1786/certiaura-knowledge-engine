# Decision Record 0048

## Decision

Create an integrated clinician approval and controlled handoff layer after Build 0047 rather than adding autonomous clinical decision support.

## Rationale

The preceding build can generate a structurally valid draft clinician export. The next operational risk is approval integrity, version ambiguity, uncontrolled transfer and loss of audit evidence. Build 0048 addresses those risks while retaining human clinical authority.

## Locked boundary

No software approval, diagnosis, prescription, dose selection, medicine-access recommendation, contraindication clearance or emergency reassurance.
