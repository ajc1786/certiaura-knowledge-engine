> **Build 0038 restoration note — 2026-07-19:** This historical build record was repackaged into canonical repository-relative paths after the incorrectly routed root build folder was deleted. The build identity and original functional content are retained. Build-specific records now reside under `Documentation/Build_Records/0035J/`.

# CERTIAURA BUILD 0035J — READ FIRST

**Build title:** Supplier portfolio risk, sourcing resilience, performance analytics and commercial controls  
**Build ID:** CERT-BUILD-0035J  
**Authorisation:** GREEN — founder authorised  
**Build date:** 2026-07-19  
**Implementation state:** Repository-ready integrated work package; canonical installation occurs after import, validation, register review, commit and push.  
**Primary systems:** PPS (Product Passport System), MPS (Marketplace System), CIS (Cost Intelligence System), EKS (Evidence Knowledge System), SYS (Platform System)

## Purpose

Build 0035J establishes an end-to-end portfolio and sourcing control layer above the supplier qualification controls delivered by Build 0035I. It manages supplier concentration, approved panels, alternative-source readiness, continuity risk, comparative performance, service-level monitoring, total-cost analysis, controlled sourcing decisions and separate commercial eligibility for Marketplace participation.

## Critical rule

> Automated analytics may calculate, compare, rank, alert and recommend. They may not award business, approve a sole source, alter supplier assurance status, or create Marketplace commercial eligibility.

Lowest price is never sufficient on its own. A sourcing decision must consider supplier assurance, evidence integrity, quality, delivery, resilience, service and total cost, and must be approved by named independent human decision-makers.

## Dependencies

- CERT-BUILD-0035D — Supplier evidence and Product Passport submission standard
- CERT-BUILD-0035E — Supplier evidence review, verification and Product Passport approval workflow
- CERT-BUILD-0035F — Product Passport publication, lifecycle monitoring and marketplace eligibility controls
- CERT-BUILD-0035G — Product Passport expiry trigger monitoring and alert automation
- CERT-BUILD-0035H — Product Passport remediation, evidence refresh, reinstatement and supplier performance controls
- CERT-BUILD-0035I — Supplier qualification, onboarding, risk tiering, audit and continuous assurance controls

This build extends the installed chain and does not replace supplier qualification or product-level evidence controls.

## Integrated capability delivered

1. Supplier portfolio concentration and dependency assessment.
2. Critical-category dual-source and resilience controls.
3. Approved-panel and alternative-source readiness management.
4. Comparative supplier performance and service-level analytics.
5. Total-cost and commercial comparison using Cost Intelligence™ principles.
6. Controlled multi-criteria sourcing decisions with conflict declarations.
7. Sole-source exception and time-bound mitigation controls.
8. Separate Marketplace commercial eligibility decisions.
9. Project Genesis assessment, ranking, monitoring, dashboarding and validation.
10. Valid, mitigated and deliberately defective examples.
11. Automated tests, registers, audit trail and change-control records.

## Installation order

1. Import the pack while preserving relative paths.
2. Allocate permanent Universal Asset Identifiers where marked.
3. Confirm Builds 0035D–0035I remain installed and unchanged.
4. Review the standard, matrices and proposed registers.
5. Validate the supplied portfolio and sourcing-decision examples.
6. Run the portfolio assessment and sourcing ranking engines.
7. Run the service-level monitor and inspect generated alerts.
8. Generate the portfolio dashboard and comparative supplier scorecard.
9. Run the full Build 0035J unit-test suite.
10. Validate the complete repository.
11. Commit and push only after every mandatory check passes.

## Acceptance commands

Run from the build root:

```text
python 13_Project_Genesis/Validators/validate_supplier_portfolio.py 10_Marketplace/Examples/valid_diversified_portfolio.example.json
python 13_Project_Genesis/Validators/validate_supplier_portfolio.py 10_Marketplace/Examples/valid_concentrated_mitigated_portfolio.example.json
python 13_Project_Genesis/Validators/validate_supplier_portfolio.py 10_Marketplace/Examples/invalid_uncontrolled_portfolio.example.json
python 13_Project_Genesis/Validators/validate_sourcing_decision.py 10_Marketplace/Examples/valid_sourcing_decision.example.json
python 13_Project_Genesis/Validators/validate_sourcing_decision.py 10_Marketplace/Examples/invalid_automatic_sole_source_award.example.json
python 13_Project_Genesis/Automation/monitor_service_levels.py 10_Marketplace/Examples Documentation/SERVICE_LEVEL_ALERTS.generated.json --as-of 2026-07-19T12:00:00+00:00
python 13_Project_Genesis/Dashboards/generate_portfolio_dashboard.py 10_Marketplace/Examples Documentation/SUPPLIER_PORTFOLIO_DASHBOARD.generated.md
python 13_Project_Genesis/Dashboards/generate_supplier_scorecard.py 10_Marketplace/Examples/valid_diversified_portfolio.example.json Documentation/SUPPLIER_SCORECARD.generated.md
python -m unittest discover -s 13_Project_Genesis/Tests -p "test_0035j_*.py"
```

## Expected release gate

- Valid diversified portfolio: PASS
- Valid concentrated portfolio with controlled mitigation: PASS
- Deliberately uncontrolled portfolio: FAIL
- Valid sourcing decision: PASS
- Deliberately invalid automatic sole-source award: FAIL
- Service-level monitoring: PASS
- Dashboard and scorecard generation: PASS
- Unit tests: all pass

## Repository update principle

Extend the existing PPS, MPS, CIS, EKS and SYS structures. Do not create a parallel supplier system, commercial governance structure, decision log or dashboard architecture.
