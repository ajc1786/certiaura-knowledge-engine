# CERTIAURA BUILD 0036 — READ FIRST

**Build title:** Marketplace customer eligibility jurisdiction consent privacy and post-market surveillance controls  
**Build ID:** CERT-BUILD-0036  
**Authorisation:** GREEN — founder authorised  
**Build date:** 2026-07-19  
**Implementation state:** Repository-ready integrated work package; canonical installation occurs only after import, validation, register review, commit and push.  
**Primary systems:** MPS (Marketplace System), PPS (Product Passport System), SKS (Safety Knowledge System), EKS (Evidence Knowledge System), CKS (Condition Knowledge System), SYS (Platform System)

## Purpose

Build 0036 establishes the controlled customer-side and post-market operating chain for Certiaura. It covers customer and organisation onboarding, jurisdiction and intended-use gating, identity and access controls, consent and privacy records, customer risk flags, responsible-use communications, complaint and safety-signal aggregation, post-market surveillance, escalation, regulatory-reporting assessment, closure, audit and dashboards.

It starts a new whole-number build because the capability is operationally distinct from the closed 0035 supplier and Product Passport™ chain. It depends on that chain without renaming or altering any installed 0035 build.

## Critical rule

> Automation may validate, calculate, monitor, restrict, block, pseudonymise, aggregate, alert and recommend. It may not determine legal eligibility, approve a customer, override a prohibited jurisdiction, infer consent, make a clinical diagnosis, close a surveillance case, decide whether a regulatory report is legally required, submit a regulatory report or reinstate access.

## Mandatory independent gates

1. Current jurisdiction-specific legal-route decision.
2. Verified customer or organisation identity appropriate to the route.
3. Recorded intended-use declaration and responsible-use acknowledgement.
4. Current privacy notice, recorded legal basis and data-minimisation controls.
5. Named human eligibility decision with conflict declaration.
6. Role-based access, least-privilege and multi-factor authentication requirements.
7. Product Passport™, batch, order and incident traceability where applicable.
8. Human surveillance triage and regulatory-reporting assessment.
9. Independent closure approval for serious or critical cases.
10. No automatic eligibility, reporting decision, case closure or access reinstatement.

Passing one gate never implies another gate has passed.

## Dependencies

- CERT-BUILD-0035D — Supplier evidence and Product Passport submission standard
- CERT-BUILD-0035E — Supplier evidence review, verification and Product Passport approval workflow
- CERT-BUILD-0035F — Product Passport publication, lifecycle monitoring and marketplace eligibility controls
- CERT-BUILD-0035G — Product Passport expiry trigger monitoring and alert automation
- CERT-BUILD-0035H — Product Passport remediation, evidence refresh, reinstatement and supplier performance controls
- CERT-BUILD-0035I — Supplier qualification, onboarding, risk tiering, audit and continuous assurance controls
- CERT-BUILD-0035J — Supplier portfolio risk, sourcing resilience, performance analytics and commercial controls
- CERT-BUILD-0035K — Marketplace contracting, order assurance, fulfilment, incident response, recall and settlement controls

## Integrated capability delivered

1. Individual and organisational onboarding and eligibility workflow.
2. Jurisdiction, intended-use and legal-route control matrix.
3. Identity, role-based access, least-privilege and account restriction controls.
4. Consent, privacy notice, legal-basis, retention and rights-request records.
5. Customer risk flags, manual review, conditions, suspension and review expiry.
6. Complaint, incident, quality and safety-signal intake and deduplication.
7. Trend aggregation, severity escalation, protective restrictions and traceability.
8. Human regulatory-reporting assessment, deadline monitoring and report register.
9. Controlled investigation, corrective action, effectiveness review and case closure.
10. Project Genesis validators, automation, dashboards, examples and tests.

## Installation order

1. Import the pack while preserving relative paths.
2. Confirm Builds 0035D–0035K remain installed and unchanged.
3. Allocate permanent Universal Asset Identifiers where marked.
4. Review the standards, schemas, templates and proposed registers.
5. Replace illustrative jurisdiction entries with approved legal determinations before production use.
6. Validate all valid and defective examples.
7. Run eligibility, jurisdiction, privacy, signal and reporting monitors.
8. Generate all four dashboards.
9. Run the complete Build 0036 test suite.
10. Validate the complete repository, then commit and push.

## Acceptance commands

Run from the build root:

```text
python 13_Project_Genesis/Validators/validate_customer_eligibility.py 10_Marketplace/Examples/valid_individual_eligibility.example.json
python 13_Project_Genesis/Validators/validate_customer_eligibility.py 10_Marketplace/Examples/invalid_automatic_eligibility.example.json
python 13_Project_Genesis/Validators/validate_customer_eligibility.py 10_Marketplace/Examples/invalid_prohibited_jurisdiction.example.json
python 13_Project_Genesis/Validators/validate_privacy_record.py 10_Marketplace/Examples/valid_privacy_request.example.json
python 13_Project_Genesis/Validators/validate_privacy_record.py 10_Marketplace/Examples/invalid_privacy_auto_close.example.json
python 13_Project_Genesis/Validators/validate_surveillance_case.py 10_Marketplace/Examples/valid_critical_signal.example.json
python 13_Project_Genesis/Validators/validate_surveillance_case.py 10_Marketplace/Examples/invalid_signal_auto_close.example.json
python 13_Project_Genesis/Automation/eligibility_gate.py 10_Marketplace/Examples/valid_individual_eligibility.example.json Documentation/ELIGIBILITY_GATE.generated.json
python 13_Project_Genesis/Automation/jurisdiction_access_monitor.py 10_Marketplace/Examples Documentation/JURISDICTION_ALERTS.generated.json
python 13_Project_Genesis/Automation/privacy_retention_monitor.py 10_Marketplace/Examples Documentation/PRIVACY_ALERTS.generated.json
python 13_Project_Genesis/Automation/signal_aggregator.py 10_Marketplace/Examples Documentation/SIGNAL_AGGREGATION.generated.json
python 13_Project_Genesis/Automation/reporting_deadline_monitor.py 10_Marketplace/Examples Documentation/REPORTING_ALERTS.generated.json
python 13_Project_Genesis/Dashboards/generate_eligibility_dashboard.py 10_Marketplace/Examples Documentation/ELIGIBILITY_DASHBOARD.generated.md
python 13_Project_Genesis/Dashboards/generate_privacy_dashboard.py 10_Marketplace/Examples Documentation/PRIVACY_DASHBOARD.generated.md
python 13_Project_Genesis/Dashboards/generate_surveillance_dashboard.py 10_Marketplace/Examples Documentation/SURVEILLANCE_DASHBOARD.generated.md
python 13_Project_Genesis/Dashboards/generate_reporting_dashboard.py 10_Marketplace/Examples Documentation/REPORTING_DASHBOARD.generated.md
python -m unittest discover -s 13_Project_Genesis/Tests -p "test_0036_*.py"
```

## Expected release gate

- Valid individual eligibility: PASS
- Valid conditional organisation eligibility: PASS
- Deliberately invalid automatic eligibility: FAIL
- Deliberately invalid prohibited-jurisdiction eligibility: FAIL
- Valid privacy rights request: PASS
- Deliberately invalid automated privacy closure: FAIL
- Valid critical surveillance signal: PASS
- Valid trend signal: PASS
- Deliberately invalid automated signal closure: FAIL
- All automation and dashboards: PASS
- Unit tests: all pass

## Repository update principle

Extend the existing MPS, PPS, SKS, EKS, CKS and SYS structures. Do not create a parallel customer, privacy, surveillance, regulatory, governance, decision-log, register or dashboard architecture.
