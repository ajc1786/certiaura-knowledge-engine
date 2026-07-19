# CERTIAURA BUILD 0035K — READ FIRST

**Build title:** Marketplace contracting, order assurance, fulfilment, incident response, recall and settlement controls  
**Build ID:** CERT-BUILD-0035K  
**Authorisation:** GREEN — founder authorised  
**Build date:** 2026-07-19  
**Implementation state:** Repository-ready integrated work package; canonical installation occurs only after import, validation, register review, commit and push.  
**Primary systems:** PPS (Product Passport System), MPS (Marketplace System), CIS (Cost Intelligence System), EKS (Evidence Knowledge System), SKS (Safety Knowledge System), SYS (Platform System)

## Purpose

Build 0035K establishes an end-to-end operating control chain from marketplace contract approval through order release, batch and Product Passport™ gating, fulfilment, cold-chain and chain-of-custody assurance, goods receipt, non-conformance and complaint handling, incident response, withdrawal and recall, payment holds, commercial reconciliation and controlled settlement.

It operationalises the qualified-supplier and sourcing decisions delivered by Builds 0035I–0035J. It does not approve any final legal route for direct peptide sales and cannot override jurisdiction-specific legal, regulatory, clinical, product or safety requirements.

## Critical rule

> Automation may validate, calculate, monitor, restrict, quarantine, alert and recommend. It may not approve contracts, release orders, accept excursions, close incidents, initiate or terminate recalls, release payment holds, approve credits, settle claims, reinstate listings or create legal authority to sell.

## Mandatory independent gates

1. Supplier qualification and current assurance status.
2. Approved contract and quality agreement.
3. Jurisdiction-specific legal sale-route approval.
4. Active Product Passport™ with approved public and marketplace status.
5. Verified batch-level evidence and unbroken product/batch traceability.
6. No blocking critical incident, withdrawal or recall.
7. Named human order-release approval with conflict declarations.
8. Controlled fulfilment, receipt and exception disposition.
9. Independent incident/recall and financial settlement approvals.

Passing one gate never implies another gate has passed.

## Dependencies

- CERT-BUILD-0035D — Supplier evidence and Product Passport submission standard
- CERT-BUILD-0035E — Supplier evidence review, verification and Product Passport approval workflow
- CERT-BUILD-0035F — Product Passport publication, lifecycle monitoring and marketplace eligibility controls
- CERT-BUILD-0035G — Product Passport expiry trigger monitoring and alert automation
- CERT-BUILD-0035H — Product Passport remediation, evidence refresh, reinstatement and supplier performance controls
- CERT-BUILD-0035I — Supplier qualification, onboarding, risk tiering, audit and continuous assurance controls
- CERT-BUILD-0035J — Supplier portfolio risk, sourcing resilience, performance analytics and commercial controls

## Integrated capability delivered

1. Marketplace contract, quality agreement and legal-route controls.
2. Human-controlled purchase/order release with supplier, passport, batch and incident gates.
3. Dispatch, chain-of-custody, cold-chain, tamper and delivery assurance.
4. Goods receipt, quarantine, excursion, rejection and non-conformance workflows.
5. Complaint intake, severity triage, incident command and corrective/preventive action linkage.
6. Batch traceability, withdrawal, recall, customer notification and effectiveness checks.
7. Listing suspension, passport restriction and order-block propagation.
8. Payment holds, credits, returns, recovery, commercial settlement and audit trail.
9. Project Genesis validators, monitoring, recall tracing and dashboards.
10. Valid and deliberately defective examples, registers, tests and release evidence.

## Installation order

1. Import the pack while preserving relative paths.
2. Confirm Builds 0035D–0035J remain installed and unchanged.
3. Allocate permanent Universal Asset Identifiers where marked.
4. Review the standard, schemas, templates and proposed registers.
5. Validate all valid and defective examples.
6. Run the order-release gate, fulfilment monitor, recall trace and settlement-hold engine.
7. Generate all three dashboards.
8. Run the full Build 0035K unit-test suite.
9. Validate the complete repository.
10. Commit and push only after every mandatory check passes.

## Acceptance commands

Run from the build root:

```text
python 13_Project_Genesis/Validators/validate_contract_order.py 10_Marketplace/Examples/valid_contract_order.example.json
python 13_Project_Genesis/Validators/validate_contract_order.py 10_Marketplace/Examples/invalid_automatic_order_release.example.json
python 13_Project_Genesis/Validators/validate_fulfilment_receipt.py 10_Marketplace/Examples/valid_fulfilment_excursion.example.json
python 13_Project_Genesis/Validators/validate_incident_recall.py 10_Marketplace/Examples/valid_critical_recall.example.json
python 13_Project_Genesis/Validators/validate_incident_recall.py 10_Marketplace/Examples/invalid_recall_without_traceability.example.json
python 13_Project_Genesis/Validators/validate_settlement.py 09_Cost_Intelligence/Examples/valid_settlement.example.json
python 13_Project_Genesis/Validators/validate_settlement.py 09_Cost_Intelligence/Examples/invalid_settlement_open_incident.example.json
python 13_Project_Genesis/Automation/order_release_gate.py 10_Marketplace/Examples/valid_contract_order.example.json Documentation/ORDER_RELEASE_GATE.generated.json
python 13_Project_Genesis/Automation/monitor_fulfilment.py 10_Marketplace/Examples Documentation/FULFILMENT_ALERTS.generated.json
python 13_Project_Genesis/Automation/trace_recall.py 10_Marketplace/Examples/valid_critical_recall.example.json Documentation/RECALL_TRACE.generated.json
python 13_Project_Genesis/Automation/settlement_hold_engine.py 09_Cost_Intelligence/Examples Documentation/SETTLEMENT_HOLDS.generated.json
python 13_Project_Genesis/Dashboards/generate_operations_dashboard.py 10_Marketplace/Examples Documentation/OPERATIONS_DASHBOARD.generated.md
python 13_Project_Genesis/Dashboards/generate_incident_dashboard.py 10_Marketplace/Examples Documentation/INCIDENT_RECALL_DASHBOARD.generated.md
python 13_Project_Genesis/Dashboards/generate_settlement_dashboard.py 09_Cost_Intelligence/Examples Documentation/SETTLEMENT_DASHBOARD.generated.md
python -m unittest discover -s 13_Project_Genesis/Tests -p "test_0035k_*.py"
```

## Expected release gate

- Valid contract and human-released order: PASS
- Deliberately invalid automatic order release: FAIL
- Valid controlled temperature-excursion receipt: PASS
- Valid critical recall: PASS
- Deliberately invalid recall without traceability: FAIL
- Valid closed-case settlement: PASS
- Deliberately invalid settlement during open incident: FAIL
- All automation and dashboards: PASS
- Unit tests: all pass

## Repository update principle

Extend the existing PPS, MPS, CIS, EKS, SKS and SYS structures. Do not create a parallel supplier, marketplace, safety, incident, finance, governance, decision-log or dashboard architecture.
