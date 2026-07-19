> **Build 0038 restoration note — 2026-07-19:** This historical build record was repackaged into canonical repository-relative paths after the incorrectly routed root build folder was deleted. The build identity and original functional content are retained. Build-specific records now reside under `Documentation/Build_Records/0035I/`.

# CERTIAURA BUILD 0035I — READ FIRST

**Build title:** Supplier qualification, onboarding, risk tiering, audit and continuous assurance controls  
**Build ID:** CERT-BUILD-0035I  
**Authorisation:** GREEN — founder authorised  
**Build date:** 2026-07-19  
**Implementation state:** Repository-ready integrated work package; canonical installation occurs after import, validation, register review, commit and push.  
**Primary systems:** PPS (Product Passport System), EKS (Evidence Knowledge System), MPS (Marketplace System), SYS (Platform System)

## Purpose

Build 0035I establishes the end-to-end supplier assurance route before and throughout participation in Certiaura. It governs due diligence, onboarding, evidence collection, risk tiering, qualification decisions, audit planning, continuous assurance, document-expiry monitoring, restrictions, suspension and controlled integration with Product Passport™ and Marketplace records.

## Critical rule

> Automation may calculate risk, identify blockers, schedule reviews and impose protective restrictions; it may not qualify, approve, reinstate or positively endorse a supplier.

Supplier qualification is a prerequisite control only. It does not verify any product, batch, Certificate of Analysis or Product Passport™ claim. Product and batch evidence must still pass Builds 0035D–0035H.

## Dependencies

- `CERT-BUILD-0035D — Supplier Evidence and Product Passport™ Submission Standard`
- `CERT-BUILD-0035E — Supplier Evidence Review, Verification and Product Passport™ Approval Workflow`
- `CERT-BUILD-0035F — Product Passport™ Publication, Lifecycle Monitoring and Marketplace Eligibility Controls`
- `CERT-BUILD-0035G — Product Passport™ Expiry, Trigger Monitoring and Alert Automation`
- `CERT-BUILD-0035H — Product Passport™ Remediation, Evidence Refresh, Reinstatement and Supplier Performance Controls`

This build extends the installed chain and does not amend or replace it.

## Integrated capability delivered

1. Supplier due-diligence and onboarding workflow.
2. Required evidence and declaration controls.
3. Risk scoring, tiering and critical-flag overrides.
4. Independent qualification and conditional-approval decisions.
5. Audit scope, cadence, findings and closure controls.
6. Continuous-assurance triggers and document-expiry monitoring.
7. Restriction, suspension, rejection and expiry controls.
8. Approved Supplier List and Product Passport™ / Marketplace integration gates.
9. Project Genesis assessment, scheduling, dashboarding and validation.
10. Valid, conditional, suspended and deliberately defective examples.
11. Automated tests, registers, audit trail and change-control records.

## Install order

1. Import the pack while preserving relative paths.
2. Allocate permanent Universal Asset Identifiers where marked.
3. Confirm Builds 0035D–0035H remain installed and unchanged.
4. Review the standard, matrices and proposed registers.
5. Run the assessment engine against supplied examples.
6. Validate all output examples.
7. Run the assurance scheduler and inspect generated alerts.
8. Generate the example supplier assurance dashboard.
9. Run the full Build 0035I unit-test suite.
10. Validate the full repository.
11. Commit and push only after every mandatory check passes.

## Acceptance commands

Run from this build root:

```text
python 13_Project_Genesis/Validators/validate_supplier_assurance.py 08_Product_Passports/Examples/Output/valid_qualified_supplier.example.json
python 13_Project_Genesis/Validators/validate_supplier_assurance.py 08_Product_Passports/Examples/Output/valid_conditional_supplier.example.json
python 13_Project_Genesis/Validators/validate_supplier_assurance.py 08_Product_Passports/Examples/Output/valid_suspended_supplier.example.json
python 13_Project_Genesis/Validators/validate_supplier_assurance.py 08_Product_Passports/Examples/Output/invalid_auto_qualified_supplier.example.json
python 13_Project_Genesis/Automation/schedule_supplier_assurance.py 08_Product_Passports/Examples/Output Documentation/SUPPLIER_ASSURANCE_ALERTS.generated.json --as-of 2026-07-19T12:00:00+00:00
python 13_Project_Genesis/Dashboards/generate_supplier_assurance_dashboard.py 08_Product_Passports/Examples/Output Documentation/SUPPLIER_ASSURANCE_DASHBOARD.generated.md
python -m unittest discover -s 13_Project_Genesis/Tests -p "test_0035i_*.py"
```

## Expected result

- Valid qualified supplier: **PASS**
- Valid conditional supplier: **PASS**
- Valid suspended supplier: **PASS**
- Deliberately invalid auto-qualified supplier: **FAIL**
- Assurance scheduler: **PASS**
- Dashboard generation: **PASS**
- Unit tests: **all pass**

## Repository update principle

Import into the existing Product Passport, Evidence, Marketplace and Platform systems and their established registers. Do not create a parallel supplier knowledge system or replacement governance architecture.
