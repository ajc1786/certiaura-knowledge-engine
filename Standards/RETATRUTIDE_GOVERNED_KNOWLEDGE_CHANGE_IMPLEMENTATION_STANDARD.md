# Retatrutide Governed Knowledge Change Implementation Standard

**Build:** 0053
**Status:** Controlled baseline
**Applies to:** Retatrutide knowledge, safety, monitoring, evidence, reporting, artificial-intelligence and publication outputs

## 1. Purpose

This standard closes the operational loop established by Build 0052. A governed cross-case signal may recommend a knowledge change, but no live Certiaura output may be changed until the proposal, cross-asset impact assessment, human approval, controlled implementation, publication release and post-change effectiveness review are complete and traceable.

## 2. Mandatory lifecycle

```text
Build 0052 signal-governance decision
-> knowledge-change proposal
-> cross-asset impact assessment
-> human scientific and governance approval
-> transactional implementation package
-> controlled publication release
-> post-change effectiveness review
-> close, watch, reopen or roll back
```

## 3. Non-negotiable controls

1. The originating signal-governance decision must be identifiable and in an authorised state.
2. Artificial intelligence may assist routing, comparison, completeness checking and draft generation, but may not independently approve a scientific, clinical, warning, contraindication, monitoring or publication change.
3. Every affected canonical asset, report, interface, relationship and artificial-intelligence response surface must be assessed.
4. Partial propagation is prohibited. An implementation is complete only when the applied target set equals the approved expected target set.
5. Universal Asset Identifiers are preserved for existing assets. New identifiers are allocated only for genuinely new formal assets.
6. Publication cannot precede approved implementation.
7. Patient-facing and professional-facing wording must remain within the existing responsible-communications controls.
8. Every implemented change requires defined effectiveness measures, evidence references, review timing and rollback triggers.
9. Ineffective, partially effective, contradictory or defectively implemented changes must be reopened or rolled back through a recorded human decision.
10. Repository files, the Master Asset Register, relationships, registers, governance updates and build records form one rollback-safe transaction.

## 4. Change classifications

- `CLARIFICATION`
- `EVIDENCE_RATING_CHANGE`
- `MONITORING_ENHANCEMENT`
- `WARNING_UPDATE`
- `CONTRAINDICATION_UPDATE`
- `REPORT_WORDING_UPDATE`
- `AI_RESPONSE_RESTRICTION`
- `TEMPORARY_PUBLICATION_HOLD`
- `SUPERSESSION`
- `NO_CHANGE_WATCH`

## 5. State controls

A change may use the states `DRAFT`, `SUBMITTED`, `UNDER_ASSESSMENT`, `QUARANTINED`, `APPROVED`, `STAGED`, `IMPLEMENTED`, `PUBLISHED`, `WITHDRAWN`, `SUPERSEDED`, `ROLLED_BACK`, `EFFECTIVE`, `PARTIALLY_EFFECTIVE`, `INEFFECTIVE`, `REOPENED` and `CLOSED` only where the corresponding evidence and predecessor states exist.

## 6. Required records

- Knowledge Change Proposal
- Cross-Asset Impact Assessment
- Controlled Change Approval
- Change Implementation Package
- Publication Release
- Post-Change Effectiveness Review
- Change Reopening Decision

## 7. Closure rule

A Build 0052 feedback recommendation is not operationally closed merely because it was accepted. Closure requires complete propagation, controlled publication where applicable, effectiveness evidence and a final close/watch/reopen decision.
