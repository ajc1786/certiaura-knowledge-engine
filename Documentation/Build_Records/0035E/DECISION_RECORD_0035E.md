# DECISION RECORD — CERT-BUILD-0035E

**Decision ID:** CERT-DEC-0035E  
**Date:** 2026-07-18  
**Status:** Proposed for GREEN  
**Decision owner:** Founder / Certiaura

## Decision

Implement a controlled supplier evidence review, verification and Product Passport™ approval workflow as the operational successor to Build 0035D.

## Existing decision retained

Build 0035D remains the authoritative supplier submission standard. Its rule that submission is not verification is retained without amendment.

## Reason

A submission schema alone cannot establish:

- evidence authenticity;
- issuer provenance;
- batch applicability;
- claim-level sufficiency;
- reviewer independence;
- public-display permission;
- approval duration; or
- marketplace eligibility.

Build 0035E creates the auditable decision layer required to resolve those matters.

## Controls adopted

1. Controlled state transitions only.
2. Immutable review-decision records; corrections require a superseding decision.
3. Claim-level verification rather than blanket document approval.
4. Evidence provenance, integrity, applicability, scope and expiry review.
5. Mandatory risk assessment and escalation.
6. Four-eyes approval for a VERIFIED Product Passport.
7. Conflict-of-interest declaration and exclusion from approval where a conflict is present.
8. Public display prohibited unless the specific claim is approved.
9. Marketplace eligibility assessed separately from evidence verification.
10. No implication that a verified supplier claim equals regulatory approval, clinical suitability or legal marketability.

## Effect on locked architecture

This build extends the existing Product Passport System, Evidence Knowledge System, Marketplace System and Project Genesis validation capability. It creates no new Knowledge System and no parallel governance framework.

## Supersession

None. Build 0035D is retained in full.
