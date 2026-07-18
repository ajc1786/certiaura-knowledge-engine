# CERTIAURA SUPPLIER EVIDENCE REVIEW, VERIFICATION AND PRODUCT PASSPORT™ APPROVAL WORKFLOW

**Build:** CERT-BUILD-0035E  
**Version:** 1.0.0  
**Status:** Repository-ready proposed standard  
**Depends on:** CERT-BUILD-0035D  
**UAI:** UAI_ALLOCATION_REQUIRED

## 1. Purpose

This standard governs how Certiaura reviews a supplier submission created under Build 0035D and reaches a controlled Product Passport™ decision.

It ensures that:

- structural validity is not confused with truth;
- documents are not approved as a bundle without claim-level assessment;
- evidence provenance, applicability and limitations are recorded;
- reviewers and approvers are accountable;
- high-risk or conflicting material is escalated;
- public display and marketplace eligibility are separately controlled; and
- every final decision can be audited, expired, quarantined or superseded.

## 2. Scope

### 2.1 Included

- intake validation;
- duplicate and supersession checks;
- evidence integrity review;
- provenance and issuer verification;
- product and batch applicability checks;
- claim-to-evidence assessment;
- evidence-class award;
- claim verification status;
- risk grading;
- clarification, quarantine and rejection;
- conditional acceptance;
- final Product Passport verification;
- public-display approval;
- expiry and re-review;
- separate marketplace eligibility decision; and
- immutable audit records.

### 2.2 Excluded

This workflow does not by itself establish:

- legal authority to sell a product;
- regulatory approval;
- clinical effectiveness;
- safety for any person;
- prescribing or treatment suitability;
- manufacturing quality beyond the evidenced scope;
- equivalence between batches; or
- marketplace admission without a separate eligibility decision.

## 3. Core principles

1. **Submission is not verification.**
2. **A document supports claims; it is not approved in the abstract.**
3. **Identity, strength, purity, sterility, endotoxin and mass are separate claims.**
4. **Batch-level claims require batch-linked evidence.**
5. **Evidence class reflects provenance and verification strength, not the importance of the claim.**
6. **Public display is claim-specific.**
7. **Verified does not mean regulator-approved or suitable for human use.**
8. **Marketplace eligibility is a separate decision.**
9. **Final VERIFIED status requires independent approval under the four-eyes rule.**
10. **Review records are immutable; corrections create a superseding decision.**

## 4. Review object

Each review creates one `product_passport_review_decision` object linked to one immutable snapshot of a 0035D submission.

Minimum identity controls:

- review decision identifier;
- supplier submission identifier;
- source schema version;
- SHA-256 hash of the reviewed submission snapshot;
- source submission status;
- target submission status;
- review start and completion timestamps;
- lead reviewer;
- final approver where required; and
- relationship links to the submission, claims, evidence and Product Passport.

## 5. Workflow stages

### Stage 1 — Intake

Confirm:

- the submission passes the installed 0035D structural validator;
- declarations are complete;
- supplier, product and batch can be identified;
- evidence files have hashes and provenance metadata;
- claim-to-evidence links resolve;
- duplicate and supersession checks have been completed; and
- no immediate quarantine trigger is present.

Permitted outcomes:

- proceed to evidence review;
- clarification required;
- quarantine; or
- reject.

### Stage 2 — Evidence review

For each evidence object assess:

- file integrity;
- alteration or redaction concerns;
- source channel;
- issuer traceability;
- direct issuer confirmation where applicable;
- laboratory identity;
- report number and dates;
- accreditation scope where claimed;
- product applicability;
- batch applicability;
- method and result scope;
- validity or expiry; and
- conflicts with other evidence.

Evidence outcomes:

- `ACCEPTED`;
- `ACCEPTED_WITH_LIMITATIONS`;
- `CLARIFICATION_REQUIRED`;
- `QUARANTINED`; or
- `REJECTED`.

### Stage 3 — Claim review

Each claim receives its own decision:

- `UNVERIFIED`;
- `PARTIALLY_VERIFIED`;
- `VERIFIED`;
- `DISPUTED`;
- `REJECTED`; or
- `EXPIRED`.

A VERIFIED claim must include:

- linked accepted evidence;
- an awarded evidence class;
- a named reviewer;
- review date;
- scope and limitations;
- next review date where time-sensitive;
- batch-link confirmation for batch-specific claims; and
- explicit public-display approval or refusal.

For Build 0035E, a VERIFIED supplier claim requires evidence class `E4` or `E5`. Lower evidence classes may support conditional or partial verification but not full verification.

## 6. Evidence class decision

The reviewer must award the class actually achieved after review, not the class asserted by the supplier.

- **E0:** unsupported assertion.
- **E1:** supplier-controlled statement or marketing material.
- **E2:** traceable supplier or manufacturer evidence without independent confirmation.
- **E3:** traceable third-party evidence with incomplete independence, applicability or scope confirmation.
- **E4:** independently verified, batch-applicable or directly issuer-confirmed evidence adequate for the specific claim.
- **E5:** authoritative primary evidence or verified regulator/accreditation source adequate for the specific claim.

No evidence class may be raised because a document appears professional or contains a logo, signature, stamp or QR code.

## 7. Risk assessment

Rate each domain as `LOW`, `MEDIUM`, `HIGH` or `CRITICAL`:

- integrity risk;
- supplier identity risk;
- manufacturer identity risk;
- product identity risk;
- batch traceability risk;
- evidence independence risk;
- expiry risk;
- regulatory misrepresentation risk; and
- conflict-of-interest risk.

The overall risk cannot be lower than the highest unresolved critical domain.

A VERIFIED decision is prohibited where:

- overall risk is `HIGH` or `CRITICAL`;
- any critical flag remains open;
- evidence alteration is suspected and unresolved;
- batch applicability is missing for a batch-specific verified claim;
- the final approver has a conflict of interest; or
- a required four-eyes approval has not occurred.

## 8. Clarification

Use `CLARIFICATION_REQUIRED` where the gap may be resolved without evidence of misconduct.

The decision record must state:

- each missing or unclear item;
- the responsible party;
- the evidence or response required;
- the deadline or next review date; and
- whether public display remains blocked.

## 9. Quarantine

Use `QUARANTINED` where there is a material integrity, identity, provenance, tampering, batch mismatch, undisclosed alteration or safety-significant inconsistency concern.

While quarantined:

- public display is prohibited;
- marketplace eligibility is prohibited;
- claims must not be represented as verified;
- related passports and supplier listings must be reviewed; and
- escalation actions must be recorded.

## 10. Rejection

Use `REJECTED` where:

- mandatory evidence is absent and cannot be remedied;
- material claims are demonstrably false;
- identity or batch linkage fails;
- issuer verification contradicts the submission;
- the supplier refuses necessary verification; or
- a prohibited or misleading representation cannot be corrected.

Rejection reasons must be specific and evidence-linked.

## 11. Conditional acceptance

`CONDITIONALLY_ACCEPTED` may be used where:

- the submission is sufficiently traceable for restricted internal or labelled use;
- unresolved gaps are non-critical;
- all limitations are prominently recorded;
- public display is restricted or blocked as appropriate;
- a next review date is set; and
- conditions and required actions are explicit.

Conditional acceptance is not a VERIFIED Product Passport.

## 12. VERIFIED approval gate

A submission may enter VERIFIED only when all mandatory conditions are met:

1. 0035D structural validation passed.
2. Intake controls passed.
3. No unresolved quarantine or rejection trigger exists.
4. Every publicly displayed claim is VERIFIED.
5. Every VERIFIED claim has accepted E4 or E5 evidence.
6. Batch-specific VERIFIED claims have confirmed batch linkage.
7. Evidence scope supports the exact claim wording.
8. Limitations and expiry are recorded.
9. Overall risk is LOW or MEDIUM.
10. No critical flag remains open.
11. Lead reviewer and final approver are different people.
12. Both have declared conflicts and the final approver has no conflict.
13. Final approval date and effective-until date are recorded.
14. The review record is marked immutable.

## 13. Four-eyes approval

For VERIFIED status:

- the lead reviewer performs the evidence and claim review;
- a separate final approver reviews the decision basis;
- the final approver must not merely rubber-stamp the lead review;
- both identities and roles are recorded; and
- the final approver must reject or return the decision where mandatory controls are missing.

## 14. Public display

A claim may be shown publicly only where:

- that exact claim has `public_display_approved = true`;
- the claim decision is VERIFIED;
- limitations are shown where material;
- the Product Passport is not quarantined, rejected, expired, withdrawn or superseded; and
- the wording does not imply regulatory approval, clinical safety or suitability beyond the evidence.

## 15. Marketplace eligibility

Marketplace eligibility values:

- `NOT_ASSESSED`;
- `NOT_ELIGIBLE`;
- `RESTRICTED`; or
- `ELIGIBLE`.

A VERIFIED Product Passport does not automatically become marketplace eligible.

`ELIGIBLE` requires:

- VERIFIED review status;
- a separate explicit marketplace decision;
- no open critical risk;
- no legal or regulatory route marked unresolved for the proposed listing; and
- any required commercial or supplier onboarding controls completed elsewhere.

Build 0035E records the eligibility outcome but does not create the final legal route for direct peptide sales.

## 16. Expiry and re-review

Time-sensitive claims must have a next review date.

Expiry triggers include:

- evidence validity date reached;
- batch expiry or retest date reached;
- supplier or manufacturer material change;
- regulator, accreditation or licence change;
- contradictory new evidence;
- product, label, formulation, method or site change; or
- unresolved post-approval integrity concern.

An expired decision must not remain publicly represented as current.

## 17. Supersession and immutability

A completed review decision is immutable.

Corrections, new evidence or changed conclusions require:

- a new review decision identifier;
- a `SUPERSEDES` relationship to the prior decision;
- retention of the prior record;
- clear effective dates; and
- synchronized status updates to the Product Passport and relevant registers.

## 18. Required relationships

Applicable relationships include:

- `REVIEWS` submission;
- `HAS_EVIDENCE` evidence objects;
- `VERIFIES` or `REJECTS` claims;
- `HAS_PASSPORT` Product Passport;
- `HAS_WARNING` risk or limitation objects;
- `REQUIRES` clarification or corrective action;
- `SUPERSEDES` prior review decision; and
- `GENERATES` public Product Passport output.

Where repository relationship types have not yet been formally extended to include review-specific verbs, use the existing closest locked type and record the proposed relationship extension through normal change control rather than silently inventing production relationships.

## 19. Registers

Update, as applicable:

- submission status register from 0035D;
- review decision register;
- claim review register;
- Master Asset Register;
- Decision Log;
- Production Dashboard; and
- change log.

## 20. Audit minimum

The audit record must preserve:

- reviewed submission hash;
- reviewer and approver identities;
- timestamps;
- all evidence and claim outcomes;
- risk grading;
- conditions and required actions;
- public-display decisions;
- marketplace eligibility decision;
- decision expiry; and
- supersession links.

## 21. Validation notice

Passing the Project Genesis validator confirms only that the review-decision object satisfies defined structural and logical controls. It does not authenticate evidence, reproduce laboratory analysis or make a legal, regulatory, medical or commercial determination.
