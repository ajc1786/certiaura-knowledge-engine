# CERTIAURA SUPPLIER QUALIFICATION, ONBOARDING, RISK TIERING, AUDIT AND CONTINUOUS ASSURANCE STANDARD

**Build:** CERT-BUILD-0035I  
**Version:** 1.0.0  
**Status:** Repository-ready approved build  
**Depends on:** CERT-BUILD-0035D through CERT-BUILD-0035H  
**UAI:** UAI_ALLOCATION_REQUIRED

## 1. Purpose

This standard establishes the controls by which a supplier may be identified, assessed, onboarded, qualified, conditionally approved, restricted, suspended, rejected, expired and continuously monitored within Certiaura.

The standard is designed to prevent a supplier from gaining a positive platform status solely through self-declaration, commercial relationship, document upload or automated scoring.

## 2. Continuity and scope

This build extends the existing Product Passport System (PPS), Evidence Knowledge System (EKS), Marketplace System (MPS) and Platform System (SYS). It does not create a separate Supplier Knowledge System and does not alter the Universal Asset & Relationship Standard, Master Asset Register, Decision Log, repository structure, naming standard or release process.

Supplier qualification is organisation-level assurance. It does not verify a product, batch, concentration, Certificate of Analysis, laboratory result or marketing claim. Those matters remain subject to the evidence, review, publication, monitoring and remediation controls established in Builds 0035D–0035H.

## 3. Non-negotiable approval boundary

> Automation may calculate risk, identify deficiencies, recommend a status, schedule audits and maintain protective restrictions. It may not create a positive supplier assurance decision.

Automation must never:

- qualify or conditionally approve a supplier;
- waive required due diligence or evidence;
- verify a supplier declaration as true;
- close a critical or major audit finding;
- remove a legal, regulatory, integrity or safety hold;
- reinstate a restricted, suspended, rejected or expired supplier;
- make a supplier marketplace-eligible;
- bypass reviewer independence or four-eyes approval; or
- overwrite prior decisions or audit history.

Positive qualification requires a named primary reviewer and an independent second approver. Any subsequent Product Passport™ approval and Marketplace eligibility decision remains separate.

## 4. Supplier assurance lifecycle

| State | Meaning | Positive participation permitted |
|---|---|---:|
| PROSPECT | Supplier identified but not assessed | No |
| ONBOARDING | Questionnaire and evidence being collected | No |
| DUE_DILIGENCE | Evidence under integrity and completeness review | No |
| RISK_REVIEW | Risk scoring and human assessment underway | No |
| AUDIT_REQUIRED | Qualification cannot proceed until audit completion | No |
| CONDITIONAL | Limited scope approved with time-bound conditions | Limited |
| QUALIFIED | Approved within an explicit scope and validity period | Yes, subject to downstream controls |
| RESTRICTED | Existing activity limited while issues are resolved | Limited or no new activity |
| SUSPENDED | Participation paused pending formal remediation | No |
| REJECTED | Qualification refused | No |
| EXPIRED | Approval period or required evidence has lapsed | No new activity |
| WITHDRAWN | Supplier voluntarily or administratively removed | No |

A state transition must be recorded as an immutable decision event. A positive transition cannot be inferred from elapsed time, score, document upload or supplier response.

## 5. Minimum due-diligence scope

Every qualification case must address, where applicable:

1. Legal identity, registration and operating addresses.
2. Trading names, ownership and beneficial ownership declarations.
3. Supplier role: manufacturer, distributor, laboratory, fulfilment provider or other.
4. Product and activity scope requested.
5. Manufacturing and storage sites.
6. Subcontractors and material third parties.
7. Quality-management documentation.
8. Laboratory relationships and testing arrangements.
9. Supply-chain and batch traceability.
10. Complaint, adverse-event, withdrawal and recall processes.
11. Data-integrity controls and record-retention commitments.
12. Material regulatory, enforcement, litigation or integrity disclosures.
13. Insurance or financial-resilience information where the approved scope requires it.
14. Contact, escalation and emergency-response details.

A declaration is not independent evidence. Supplier-provided records must remain identified as supplier claims until reviewed and, where required, corroborated.

## 6. Required evidence classes

The baseline qualification record requires the following evidence categories unless a documented scope-specific exception is approved:

- `LEGAL_REGISTRATION`
- `OWNERSHIP_DECLARATION`
- `QUALITY_SYSTEM`
- `LAB_RELATIONSHIP`
- `SUPPLY_CHAIN_TRACEABILITY`
- `COMPLAINT_RECALL_PROCESS`

Additional categories may include site licences, insurance, audit reports, accreditation records, subcontractor lists, storage controls, logistics controls, information-security controls and financial-resilience evidence.

Every evidence item must include:

- evidence identifier and category;
- issuer or source;
- issue date and, where applicable, expiry date;
- immutable SHA-256 hash;
- supplier-provided versus independently obtained status;
- verification reviewer and date;
- scope and site applicability;
- status: current, expiring, expired, withdrawn, disputed or superseded.

Expired, withdrawn, disputed or untraceable evidence cannot support a positive qualification decision.

## 7. Risk model

Risk is calculated from a 100-point baseline using controlled deductions across:

- corporate identity and ownership;
- quality-management maturity;
- evidence and data integrity;
- laboratory assurance;
- supply-chain traceability;
- complaint, recall and incident handling;
- responsiveness and remediation history; and
- financial or operational resilience where applicable.

Calculated tiers are:

| Score / override | Tier | Maximum routine review interval | Default position |
|---|---:|---:|---|
| 85–100, no critical flag | LOW | 365 days | Qualification may be considered |
| 70–84, no critical flag | MODERATE | 180 days | Qualification or conditions may be considered |
| 50–69, no critical flag | HIGH | 90 days | Conditional approval or restriction normally required |
| 0–49 or any critical flag | CRITICAL | 30 days | No positive decision; suspension or rejection normally required |

Critical flags override the numeric score. Examples include suspected document falsification, unresolved identity mismatch, critical audit finding, undisclosed manufacturing site, evidence tampering, material legal or regulatory hold, or serious traceability failure.

A calculated tier is decision support, not approval.

## 8. Qualification decision controls

A positive decision requires:

- due diligence marked complete;
- all mandatory evidence categories current and verified;
- no unresolved critical flags;
- acceptable audit status where audit is required;
- no open critical or major findings blocking qualification;
- a recorded risk score, tier and rationale;
- an explicit approved scope and sites;
- a validity start and end date;
- a named primary reviewer;
- an independent second approver;
- conditions and expiry dates where conditional;
- confirmation that automatic positive action is disabled; and
- a separate downstream decision for Product Passport™ and Marketplace participation.

`CONDITIONAL` status requires measurable, time-bound conditions. Failure to meet a condition by its deadline must generate a review trigger and protective restriction.

## 9. Audit controls

Audit requirements are risk- and scope-based. Audit types may include remote document review, targeted evidence audit, site audit, laboratory relationship audit, traceability audit, incident audit or requalification audit.

Every audit record must define:

- audit identifier, type, scope and objective;
- lead auditor and independence declaration;
- planned and completed dates;
- sites, processes and evidence sampled;
- findings by severity;
- corrective action owners and deadlines;
- effectiveness checks;
- closure decision and approver; and
- next audit or follow-up date.

Critical findings prohibit positive qualification. Major findings prohibit qualification unless formally accepted within a documented conditional decision with protective restrictions and a short review interval.

Audit findings may not be closed automatically.

## 10. Continuous assurance

Qualification remains valid only while continuous-assurance controls remain active. Monitoring must cover:

- document expiry and withdrawal;
- ownership, legal-entity, site or key-contact change;
- manufacturer, laboratory or subcontractor change;
- product quality, safety, complaint or recall events;
- evidence-integrity disputes;
- audit findings and overdue corrective actions;
- repeated Product Passport™ deficiencies;
- supplier performance deterioration;
- material regulatory or legal information;
- non-response to critical requests; and
- commercial exit or supplier withdrawal.

The system may generate alerts, recommend escalation, block new submissions or suspend marketplace visibility where predefined protective rules are met. Any positive restoration requires a controlled human decision under Build 0035H and this standard.

## 11. Review and audit cadence

The next assurance review and audit due date must not exceed the maximum interval for the current risk tier. Shorter periods are mandatory where:

- conditions remain open;
- evidence is due to expire earlier;
- audit findings require follow-up;
- a critical monitoring trigger is active;
- supplier performance is deteriorating; or
- the approved scope materially changes.

The earliest applicable date controls.

## 12. Restrictions and suspension

Protective controls may include:

- block all new Product Passport™ submissions;
- allow evidence updates only;
- prevent new product or batch onboarding;
- hide or suspend Marketplace listings;
- require pre-approval of every submission;
- limit approved sites or product categories;
- require enhanced testing or independent evidence; and
- mandate a remediation or improvement plan.

`SUSPENDED`, `REJECTED`, `EXPIRED` and `WITHDRAWN` suppliers must not be treated as qualified. Marketplace eligibility must be false and new Product Passport™ submissions must be blocked except for remediation evidence.

## 13. Approved Supplier List control

The Approved Supplier List is a controlled view, not an independent source of truth. A supplier may appear only where:

- the qualification state is `QUALIFIED` or valid `CONDITIONAL`;
- the decision is within its effective period;
- mandatory evidence remains current;
- no blocking trigger, finding or hold exists;
- continuous monitoring is active; and
- the approved scope is explicit.

Removal or restriction must be reflected promptly. Historical status must remain auditable.

## 14. Product Passport™ and Marketplace integration

Supplier status is a prerequisite gate only.

- A qualified supplier may submit Product Passport™ evidence, but every product and batch still requires its own evidence review.
- A qualified supplier is not automatically Marketplace-eligible.
- A conditional supplier may be limited to specified products, sites, activities or evidence-update actions.
- A restricted, suspended, rejected, expired or withdrawn supplier must be blocked from new positive publication and marketplace actions.
- Supplier status changes must generate relationship and downstream-impact review tasks for affected Product Passport™ and Marketplace records.

## 15. Data and audit requirements

Each record must preserve:

- immutable decision and change history;
- source-record hashes;
- reviewer and approver identities;
- independence and conflict declarations;
- before-and-after state hashes for status changes;
- evidence supersession links;
- active conditions, restrictions and triggers;
- affected Product Passport™ and Marketplace references; and
- last and next review dates.

Historical records must not be overwritten.

## 16. Project Genesis role

Project Genesis may:

- check completeness and semantic consistency;
- calculate risk scores and tiers;
- identify blockers and critical flags;
- recommend a protective status;
- calculate review and audit dates;
- generate expiry and assurance alerts;
- maintain registers and dashboards; and
- prepare decision packs.

Project Genesis may not create a positive qualification, close material findings, remove restrictions or reinstate a supplier.

## 17. Acceptance criteria

A supplier assurance record is valid only when:

1. identity, scope and evidence are complete;
2. required evidence categories are current and traceable;
3. score, tier and critical-flag logic reconcile;
4. positive decisions meet independence and approval rules;
5. audit status and findings support the decision;
6. cadence and expiry dates satisfy the earliest-date rule;
7. restrictions match the supplier state and triggers;
8. downstream eligibility is separately controlled;
9. automated positive action is explicitly prohibited; and
10. immutable audit history is present.
