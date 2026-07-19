# Certiaura Responsible Communications Approval Workflow

**Document ID:** CERT-GOV-COMMS-001  
**Version:** 1.0.0  
**Status:** ACTIVE  
**Owner:** Certiaura  
**Build provenance:** CERT-BUILD-0037

## Workflow

1. **Capture** — record exact wording, audience, channel, jurisdiction, objective and commercial context.
2. **Classify** — assign claim classes, product/regulatory status, AI involvement and risk level.
3. **Link evidence** — attach evidence object identifiers, source dates, limitations and evidence strength.
4. **Screen prohibitions** — check prescription-only medicine, unlicensed medicinal claim, absolute safety, guarantee, diagnosis, treatment, data-protection and vulnerable-audience controls.
5. **Draft disclosures** — affiliate, sponsorship, supplier, uncertainty, AI involvement and professional-care disclosures.
6. **Review** — route to the required scientific, medical, legal/regulatory, data-protection and responsible-communications approvers.
7. **Decide** — approve, approve with conditions, reject, quarantine or withdraw.
8. **Publish from the approved record** — use only the approved wording and channel scope.
9. **Monitor** — track evidence, regulation, safety signals, complaints, wording drift and model behaviour.
10. **Correct or withdraw** — propagate changes to all downstream copies and registers.

## Release gates

A communication cannot be released where:

- a material claim has no claim record;
- evidence references are absent or do not support the wording;
- required approval is missing or expired;
- the proposed channel is outside the approved scope;
- a material commercial interest is undisclosed;
- artificial intelligence involvement is misrepresented;
- a high-risk personalisation lacks human review and applicable data-protection controls;
- a blocked claim pattern is detected.

## Decision states

`DRAFT → EVIDENCE_PENDING → REVIEW_PENDING → APPROVED | APPROVED_WITH_CONDITIONS | REJECTED | QUARANTINED`

After release:

`APPROVED → REVIEW_REQUIRED → CORRECTED | SUSPENDED | WITHDRAWN | SUPERSEDED | EXPIRED`

## Segregation of duties

The person or system proposing a commercial claim must not be the sole approver of its evidence sufficiency. Supplier verification, scientific review and public-display approval remain separate decisions.

## Emergency correction

A safety, regulatory or material accuracy issue may be suspended immediately by an authorised owner before full review. The reason, affected channels and follow-up action must be recorded within the same business day.
