> **Build 0038 restoration note — 2026-07-19:** This historical build record was repackaged into canonical repository-relative paths after the incorrectly routed root build folder was deleted. The build identity and original functional content are retained. Build-specific records now reside under `Documentation/Build_Records/0035H/`.

# CERTIAURA BUILD 0035H — READ FIRST

**Build title:** Product Passport™ remediation, evidence refresh, reinstatement and supplier performance controls  
**Build ID:** CERT-BUILD-0035H  
**Authorisation:** GREEN — founder authorised  
**Build date:** 2026-07-18  
**Implementation state:** Repository-ready integrated work package; canonical installation occurs after import, validation, register review, commit and push.  
**Primary systems:** PPS (Product Passport System), EKS (Evidence Knowledge System), MPS (Marketplace System), SYS (Platform System)

## Purpose

Build 0035H converts alerts and protective restrictions from Build 0035G into a controlled end-to-end remediation process. It governs corrective action, refreshed evidence, re-review, alert closure, passport reinstatement, separate marketplace reinstatement, supplier escalation, repeat-failure tracking and supplier performance scoring.

## Critical rule

> Automation may calculate readiness, score performance and maintain restrictions; it may not approve evidence, close alerts, reinstate a passport or restore marketplace eligibility.

## Dependencies

- `CERT-BUILD-0035D — Supplier Evidence and Product Passport™ Submission Standard`
- `CERT-BUILD-0035E — Supplier Evidence Review, Verification and Product Passport™ Approval Workflow`
- `CERT-BUILD-0035F — Product Passport™ Publication, Lifecycle Monitoring and Marketplace Eligibility Controls`
- `CERT-BUILD-0035G — Product Passport™ Expiry, Trigger Monitoring and Alert Automation`

This build extends those controls and does not amend or replace them.

## Integrated capability delivered

1. Alert-to-remediation case creation.
2. Corrective and preventive action planning and effectiveness checks.
3. Evidence-refresh submission and verification controls.
4. Independent re-review and four-eyes approval.
5. Separate passport and marketplace reinstatement decisions.
6. Alert closure with residual-risk and recurrence controls.
7. Supplier response deadlines, escalation and improvement plans.
8. Repeat-failure tracking and supplier performance scoring.
9. Portfolio dashboard and supplier performance report generation.
10. Project Genesis assessment, validation and automated tests.

## Install order

1. Import the pack while preserving relative paths.
2. Allocate permanent Universal Asset Identifiers where marked.
3. Confirm Builds 0035D–0035G remain installed and unchanged.
4. Run the readiness assessment against the supplied examples.
5. Validate all output examples.
6. Run the full Build 0035H unit-test suite.
7. Generate the example supplier dashboard.
8. Review proposed register and change-log entries.
9. Validate the full repository.
10. Commit and push only after every mandatory check passes.

## Acceptance commands

Run from this build root:

```text
python 13_Project_Genesis/Validators/validate_remediation_case.py 08_Product_Passports/Examples/Output/valid_open_remediation.example.json
python 13_Project_Genesis/Validators/validate_remediation_case.py 08_Product_Passports/Examples/Output/valid_reinstated_case.example.json
python 13_Project_Genesis/Validators/validate_remediation_case.py 08_Product_Passports/Examples/Output/valid_supplier_escalation.example.json
python 13_Project_Genesis/Validators/validate_remediation_case.py 08_Product_Passports/Examples/Output/invalid_auto_reinstatement.example.json
python -m unittest discover -s 13_Project_Genesis/Tests -p "test_0035h_*.py"
python 13_Project_Genesis/Dashboards/generate_supplier_dashboard.py 08_Product_Passports/Examples/Output Documentation/SUPPLIER_PERFORMANCE_DASHBOARD.generated.md
```

## Expected result

- Valid open-remediation case: **PASS**
- Valid reinstated case: **PASS**
- Valid supplier-escalation case: **PASS**
- Deliberately invalid automatic-reinstatement case: **FAIL**
- Unit tests: **all pass**
- Dashboard generation: **PASS**

## Repository update principle

Import into the existing systems and registers. Do not create parallel governance, a replacement Product Passport System or a separate supplier knowledge system.
