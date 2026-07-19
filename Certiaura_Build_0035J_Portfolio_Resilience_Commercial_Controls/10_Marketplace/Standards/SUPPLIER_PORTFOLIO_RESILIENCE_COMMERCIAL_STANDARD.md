# CERTIAURA SUPPLIER PORTFOLIO RISK, SOURCING RESILIENCE, PERFORMANCE ANALYTICS AND COMMERCIAL CONTROLS STANDARD

**Build:** CERT-BUILD-0035J  
**Version:** 1.0.0  
**Status:** Repository-ready approved build  
**Depends on:** CERT-BUILD-0035D through CERT-BUILD-0035I  
**UAI:** UAI_ALLOCATION_REQUIRED

## 1. Purpose

This standard controls how Certiaura evaluates its supplier portfolio, protects critical supply, compares supplier performance and commercial value, and makes sourcing decisions without allowing price, automation or commercial pressure to bypass evidence, safety, qualification or human approval controls.

## 2. Scope and continuity

The standard extends the Product Passport System, Marketplace System, Cost Intelligence System, Evidence Knowledge System and Platform System. It does not create a new Supplier Knowledge System, procurement governance framework, register architecture or approval hierarchy.

Supplier-level qualification under Build 0035I remains a prerequisite. Product, batch, Certificate of Analysis and Product Passport claims remain governed by Builds 0035D–0035H.

## 3. Non-negotiable decision boundary

Automation may:

- calculate concentration metrics;
- assess category resilience;
- compare supplier performance;
- calculate total cost;
- score sourcing options;
- identify service-level breaches;
- create alerts and recommended protective actions; and
- generate decision-support dashboards.

Automation must not:

- award or renew business;
- approve a sole-source exception;
- qualify, suspend or reinstate a supplier;
- verify product or batch evidence;
- grant Marketplace commercial eligibility;
- waive a critical resilience requirement;
- suppress a material service or quality failure; or
- overwrite human decisions or immutable history.

Every positive commercial decision requires a named reviewer and an independent approver. Conflicts of interest must be declared and resolved before approval.

## 4. Portfolio concentration controls

Portfolio assessment must calculate at least:

- supplier spend percentage;
- largest-supplier concentration;
- top-three supplier concentration;
- Herfindahl-Hirschman Index (HHI);
- critical-category single-source count;
- approved alternative count;
- geographic, laboratory, manufacturer and logistics dependency where relevant; and
- concentration trend against the prior review.

Default thresholds:

| Metric | Green | Amber | Red |
|---|---:|---:|---:|
| Largest supplier share | <= 40% | >40% to 60% | >60% |
| HHI | <= 1,800 | >1,800 to 2,500 | >2,500 |
| Critical single-source categories without mitigation | 0 | 0 with time-bound mitigation | >=1 |
| Top-three share | <=75% | >75% to 90% | >90% |

A Red metric requires human review and a protective action plan. A supplier may exceed a threshold only where the dependency is transparent, a time-bound mitigation is approved, continuity arrangements are tested and the residual risk is accepted by named reviewers.

## 5. Critical-category resilience

Each critical category must normally have:

1. at least two qualified suppliers approved for the relevant scope;
2. one operational primary source and one demonstrably viable alternative;
3. documented lead time, minimum order, capacity and onboarding requirements;
4. tested business continuity and recovery arrangements;
5. a named category owner;
6. a current contingency or transition plan; and
7. a next resilience review date.

Where dual sourcing is not feasible, a sole-source mitigation must document the technical or market reason, continuity stock or substitute strategy, trigger points, owner, due date, approval and planned market retest.

## 6. Approved-panel controls

Approved-panel status is scoped by product category, activity, site, region and validity period. Panel inclusion does not guarantee work and does not imply product or batch approval.

The approved panel must distinguish:

- ACTIVE;
- CONDITIONAL;
- BACKUP_READY;
- ONBOARDING;
- RESTRICTED;
- SUSPENDED;
- EXPIRED; and
- REMOVED.

Only suppliers whose assurance status and approved scope remain current may receive a positive sourcing decision. Restricted, suspended, expired or out-of-scope suppliers must be blocked.

## 7. Performance and service-level analytics

Supplier scorecards may include:

- evidence quality and responsiveness;
- product or batch rejection rate;
- on-time-in-full delivery;
- service response time;
- complaint and corrective-action performance;
- audit findings;
- documentation expiry compliance;
- continuity testing;
- commercial accuracy;
- price stability; and
- total-cost variance.

Scores are decision support and must retain the underlying data period, sample size, data source, exclusions and reviewer. Missing data must not be converted into a positive score.

Critical safety, integrity or evidence failures override aggregate performance scores.

## 8. Cost Intelligence™ and commercial analysis

Commercial comparison must include relevant lifetime and total-cost factors, not only unit price. Applicable components include:

- unit and minimum-order cost;
- shipping, duty and handling;
- quality-control and testing cost;
- storage and cold-chain cost;
- payment terms and currency exposure;
- lead-time and continuity-stock cost;
- failure, rejection, delay and replacement cost;
- onboarding, audit and assurance cost;
- platform or transaction fees;
- forecast price movement; and
- switching and exit cost.

The cost model must state assumptions, currency, tax basis, period, confidence, source and exclusions. A low-cost result cannot override a supplier assurance, evidence, quality, safety or resilience blocker.

## 9. Sourcing decision controls

Every sourcing decision must contain:

- requirement and approved scope;
- candidate list and eligibility checks;
- controlled evaluation criteria and weights;
- source data and evaluation period;
- comparative total cost;
- assurance, quality, delivery, service and resilience assessment;
- conflict declarations;
- calculated recommendation clearly labelled as non-binding;
- reviewer rationale;
- independent approval;
- conditions, review date and exit provisions; and
- immutable decision history.

There should normally be at least two eligible candidates. A sole-source award requires an explicit exception, evidence of market limitation, a continuity mitigation, a retest date and independent approval.

## 10. Marketplace commercial eligibility

Marketplace commercial eligibility is separate from:

- supplier qualification;
- Product Passport approval;
- product or batch verification;
- inclusion on an approved panel; and
- selection for a sourcing event.

A positive commercial eligibility decision requires current supplier qualification, no blocking restriction, acceptable service and integrity performance, transparent commercial terms, named review and independent approval. Automation cannot create eligibility.

## 11. Protective actions and escalation

Material triggers include:

- critical category becoming single source;
- concentration threshold breach;
- supplier suspension or expiry;
- repeated service-level breach;
- material price or lead-time shock;
- critical evidence or integrity failure;
- business continuity test failure;
- unapproved subcontractor or site change; and
- unresolved corrective action.

Protective actions may include new-order hold, category restriction, alternative-source activation, contingency-stock review, accelerated audit, commercial review, Product Passport review or Marketplace suspension. Positive reinstatement remains a separate human decision.

## 12. Records and auditability

All calculations, source data, assumptions, recommendations, approvals, conditions, alerts, actions and superseded decisions must be retained in immutable history and linked to the relevant supplier, portfolio, category, Product Passport and Marketplace records.
