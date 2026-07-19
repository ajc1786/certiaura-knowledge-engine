# CERTIAURA PRODUCT PASSPORT™ REMEDIATION, EVIDENCE REFRESH, REINSTATEMENT AND SUPPLIER PERFORMANCE STANDARD

**Build:** CERT-BUILD-0035H  
**Version:** 1.0.0  
**Status:** Repository-ready approved build  
**Depends on:** CERT-BUILD-0035D, CERT-BUILD-0035E, CERT-BUILD-0035F and CERT-BUILD-0035G  
**UAI:** UAI_ALLOCATION_REQUIRED

## 1. Purpose

This standard controls the complete route from a Product Passport™ monitoring alert or protective restriction to remediation, refreshed evidence, independent re-review, controlled reinstatement, alert closure and supplier performance management.

It exists to prevent a suspended, expired, quarantined or ineligible record from returning to a positive state without demonstrable corrective action, verified evidence and accountable human approval.

## 2. Continuity and scope

This build consumes:

- supplier submissions from 0035D;
- review and verification decisions from 0035E;
- passport and marketplace lifecycle states from 0035F; and
- alerts and protective instructions from 0035G.

It does not replace the Master Asset Register, Decision Log, Universal Asset & Relationship Standard, release policy or any existing repository governance.

## 3. Non-negotiable approval boundary

> Automation may identify blockers, calculate readiness, maintain restrictions and recommend escalation. It may not create a positive assurance.

Automation must never:

- mark evidence as verified;
- approve a corrective action as effective;
- close a material alert;
- reinstate a passport;
- restore marketplace eligibility;
- reduce a legal, regulatory or data-integrity hold;
- waive four-eyes approval; or
- overwrite historical decisions.

Positive reinstatement requires an eligible primary reviewer and an independent second approver. Marketplace restoration requires its own decision and transaction record after passport reinstatement.

## 4. Case initiation

A remediation case is opened from one or more unresolved alerts, an expired review, supplier failure, evidence withdrawal, batch mismatch, integrity dispute, legal or regulatory event, marketplace incident or manual quality finding.

Every case requires:

- permanent case identifier;
- passport, supplier and source-alert identifiers;
- immutable source hashes;
- severity and priority;
- named owner;
- opened and target dates;
- root-cause classification;
- applicable holds;
- prior related cases and repeat-failure count; and
- initial protective state.

A critical alert cannot be downgraded at case creation.

## 5. Standard case states

| State | Meaning | Positive state permitted |
|---|---|---:|
| OPEN | Case accepted and triaged | No |
| PLAN_REQUIRED | Corrective action plan required | No |
| REMEDIATION_IN_PROGRESS | Actions underway | No |
| EVIDENCE_REFRESH_PENDING | Replacement or supplemental evidence awaited | No |
| UNDER_REVIEW | Refreshed evidence and actions under human review | No |
| REINSTATEMENT_READY | All gates met; approval not yet complete | No |
| PARTIALLY_REINSTATED | Passport restored with explicit restrictions; marketplace remains restricted unless separately approved | Limited |
| REINSTATED | Passport restored by authorised decision | Yes, subject to conditions |
| CLOSED_NO_REINSTATEMENT | Case closed without restoration | No |
| ESCALATED | Supplier, legal, regulatory or integrity escalation active | No |
| REJECTED | Remediation route rejected | No |

`REINSTATEMENT_READY` is a readiness state, not approval.

## 6. Corrective and preventive action plan

The corrective and preventive action plan must distinguish:

- immediate containment;
- root-cause correction;
- systemic preventive action;
- evidence replacement;
- supplier process change;
- marketplace or public-display correction; and
- effectiveness verification.

Every action requires an owner, due date, status, completion evidence and effectiveness result. An action is not complete merely because the supplier states it is complete.

Critical actions require objective completion evidence and an effectiveness check performed by an eligible reviewer.

## 7. Root-cause controls

At least one standard root-cause code is required:

- `DOCUMENT_CONTROL_FAILURE`
- `BATCH_TRACEABILITY_FAILURE`
- `LAB_PROVENANCE_FAILURE`
- `SPECIFICATION_MISMATCH`
- `DATA_INTEGRITY_FAILURE`
- `SUPPLIER_PROCESS_FAILURE`
- `IDENTITY_OR_AUTHORITY_FAILURE`
- `STORAGE_OR_LOGISTICS_FAILURE`
- `MARKETPLACE_DATA_FAILURE`
- `LEGAL_OR_REGULATORY_CHANGE`
- `COUNTERFEIT_OR_DUPLICATE_CONCERN`
- `REVIEW_OR_EXPIRY_FAILURE`
- `OTHER_DOCUMENTED`

`OTHER_DOCUMENTED` requires an explanatory note and cannot be the only root cause for a critical case without senior approval.

## 8. Evidence refresh

A refreshed evidence package is a new submission object linked to the original evidence and the remediation case. It must preserve, not overwrite, superseded records.

Minimum controls are:

- supplier submission identifier;
- evidence item identifier and SHA-256 hash;
- document type and source;
- batch linkage where the claim is batch-specific;
- issue, receipt and review dates;
- provenance and integrity checks;
- review outcome;
- reviewer identity;
- superseded evidence references; and
- critical-evidence designation.

The case cannot become reinstatement-ready while any mandatory critical item is missing, rejected, expired, quarantined or unverified.

## 9. Re-review

Re-review must test both the refreshed evidence and the effectiveness of corrective action. The reviewer must confirm:

1. source alerts are addressed;
2. root causes are supported by evidence;
3. containment is complete;
4. corrective actions are complete;
5. effectiveness checks passed;
6. critical evidence is verified;
7. public claims remain supportable;
8. passport validity dates are appropriate;
9. residual risk is acceptable and recorded; and
10. no unresolved hold prevents restoration.

Allowed primary decisions are:

- `REINSTATEMENT_APPROVED`
- `CONDITIONAL_REINSTATEMENT`
- `MORE_INFORMATION_REQUIRED`
- `REMEDIATION_REJECTED`
- `ESCALATE`

Approval requires a second approver whose identity differs from the primary reviewer.

## 10. Holds and hard blockers

The following are hard blockers to reinstatement:

- active legal or regulatory hold;
- active data-integrity hold;
- unresolved critical source alert;
- failed or absent critical corrective action;
- missing or unverified critical evidence;
- reviewer conflict of interest;
- missing second approval;
- expired proposed approval period;
- unrecorded residual risk; or
- active supplier suspension that covers the product or submission class.

Automation may add a blocker; it may not remove one without a recorded authorised decision.

## 11. Passport reinstatement

Passport reinstatement is a controlled lifecycle transaction. It requires:

- approved re-review decision;
- independent second approval;
- no hard blockers;
- explicit target passport state;
- effective-from and effective-until dates;
- conditions and public-display restrictions;
- transaction identifier;
- authorised executor; and
- immutable before-and-after state hashes.

A reinstatement transaction cannot silently restore claims that were excluded or conditionally approved.

## 12. Marketplace reinstatement

Marketplace eligibility is a separate downstream decision. Passport reinstatement alone does not restore a listing.

Marketplace restoration requires:

- passport state permitting marketplace consideration;
- separate marketplace decision;
- current supplier authority and availability information;
- no active marketplace-specific hold;
- required disclosures and conditions;
- separate transaction identifier; and
- acknowledgement that the listing was actually updated.

Where the passport is conditionally reinstated, the marketplace decision must explicitly assess whether those conditions permit a listing.

## 13. Alert closure

Every source alert must be individually reconciled. Allowed closure decisions are:

- `CLOSED_RESOLVED`
- `CLOSED_SUPERSEDED`
- `CLOSED_NO_REINSTATEMENT`
- `REMAINS_OPEN`
- `ESCALATED`

Alert closure requires a reason, evidence references, named closer, closure date, residual risk and recurrence-monitoring requirement. A case cannot be marked fully closed while any controlling alert remains open.

## 14. Supplier escalation

Supplier escalation is independent of a single passport decision. Escalation may apply at product, batch, evidence class, supplier or platform level.

| Level | Typical trigger | Minimum response |
|---|---|---|
| NONE | No material trend | Routine monitoring |
| WATCH | Emerging delays or one material failure | Increased review frequency |
| FORMAL_IMPROVEMENT | Repeat failure, missed remediation deadline or weak score | Supplier improvement plan and monthly review |
| RESTRICTED | Serious repeated failure or unresolved high-risk issue | Restrict new submissions or marketplace activity |
| SUSPENDED | Critical integrity, legal, counterfeit or persistent non-compliance | Suspend affected supplier activity pending senior review |

Legal, regulatory, counterfeit and material data-integrity events may bypass lower levels.

## 15. Repeat-failure tracking

A repeat failure exists where the same or materially similar root cause recurs within the configured lookback period. The default lookback is 365 days, subject to policy configuration.

Repeat-failure analysis must retain:

- related case identifiers;
- root-cause match basis;
- product and batch scope;
- recurrence date;
- prior corrective actions;
- reason prior controls failed; and
- escalation outcome.

Closing a case does not reset the repeat-failure history.

## 16. Supplier performance score

The supplied scoring engine produces a management indicator, not a quality certification. It uses a 0–100 scale and retains the component deductions.

Default deductions include:

- critical or high-severity case burden;
- repeat failures;
- overdue corrective actions;
- missing or unverified critical evidence;
- missed response service levels;
- legal or data-integrity holds; and
- weak response timeliness.

Performance tiers are:

- `A` — 90–100
- `B` — 75–89
- `C` — 60–74
- `D` — 40–59
- `E` — 0–39

A score must never override a hard blocker, legal hold or integrity finding.

## 17. Service levels

Service levels are held in `REMEDIATION_SLA_MATRIX.csv`. Default targets are:

- P0 containment: immediate;
- P1 plan submission: same business day;
- P2 plan submission: one business day;
- P3 plan submission: three business days;
- routine evidence refresh: five business days; and
- effectiveness review: within ten business days of action completion.

Missed service levels increase escalation and affect supplier performance scoring.

## 18. Supplier improvement plan

A formal improvement plan must contain:

- scope and accountable supplier owner;
- measurable actions;
- milestones and due dates;
- evidence requirements;
- success metrics;
- review cadence;
- consequences of failure; and
- exit criteria.

Exit from formal improvement status requires evidence that controls are effective over an appropriate observation period.

## 19. Dashboard and reporting

The operational dashboard should report:

- open cases by severity and state;
- overdue actions;
- evidence-refresh status;
- reinstatement-ready cases awaiting approval;
- reinstated and rejected cases;
- unresolved alerts;
- supplier score and tier;
- repeat failures;
- active escalation level; and
- approaching review dates.

Dashboard summaries must link back to immutable case and decision records.

## 20. Project Genesis implementation

Project Genesis should support:

1. case creation from 0035G alerts;
2. corrective-action and evidence-refresh tracking;
3. blocker and readiness calculation;
4. supplier score calculation;
5. approval routing and identity checks;
6. separate passport and marketplace transactions;
7. alert closure reconciliation;
8. portfolio dashboard generation; and
9. immutable audit export.

The supplied assessment engine is read-only. It returns blockers, readiness, proposed escalation and supplier score without changing the source case.

## 21. Validation gates

A remediation case fails validation where, among other controls:

- positive reinstatement is represented as automatic;
- the primary and second approver are the same person;
- critical evidence is unverified;
- a critical action lacks objective evidence or effectiveness approval;
- a legal or integrity hold exists alongside reinstatement;
- source alerts are missing or improperly closed;
- marketplace eligibility is restored without a separate decision and transaction;
- a case is closed while controlling alerts remain open;
- state transitions are contradictory;
- score components do not reconcile to the total;
- repeat failures are omitted or reset; or
- audit records are mutable or unhashed.

## 22. Acceptance criteria

Build 0035H is accepted when:

- the valid open-remediation case passes;
- the valid reinstated case passes;
- the valid supplier-escalation case passes;
- the deliberately invalid automatic-reinstatement case fails on multiple independent controls;
- readiness, blocker, scoring and dashboard tests pass;
- all code uses the Python standard library only; and
- the complete ZIP passes integrity testing.
