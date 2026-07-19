> **Build 0038 restoration note — 2026-07-19:** This historical build record was repackaged into canonical repository-relative paths after the incorrectly routed root build folder was deleted. The build identity and original functional content are retained. Build-specific records now reside under `Documentation/Build_Records/0035G/`.

# CERTIAURA BUILD 0035G — READ FIRST

**Build title:** Product Passport™ expiry, trigger monitoring and alert automation  
**Build ID:** CERT-BUILD-0035G  
**Authorisation:** GREEN — founder authorised  
**Build date:** 2026-07-18  
**Implementation state:** Repository-ready build pack; canonical installation occurs after import, validation, register review, commit and push.  
**Primary systems:** PPS (Product Passport System), EKS (Evidence Knowledge System), MPS (Marketplace System), SYS (Platform System)

## Purpose

Build 0035G converts the lifecycle rules in 0035F into a read-only monitoring and alert engine. It scans lifecycle records, detects expiry and review thresholds, identifies open high or critical events, generates deduplicated alerts and outputs protective-action instructions.

## Critical rule

> The automation may restrict or escalate; it may not verify, publish, reinstate or approve.

## Dependencies

- `CERT-BUILD-0035D — Supplier Evidence and Product Passport™ Submission Standard`
- `CERT-BUILD-0035E — Supplier Evidence Review, Verification and Product Passport™ Approval Workflow`
- `CERT-BUILD-0035F — Product Passport™ Publication, Lifecycle Monitoring and Marketplace Eligibility Controls`

This build extends those controls and does not amend or replace them.

## Install order

1. Import the pack while preserving relative paths.
2. Allocate permanent Universal Asset Identifiers where marked.
3. Confirm 0035D, 0035E and 0035F remain installed and unchanged.
4. Run the engine against the supplied examples.
5. Validate the generated monitoring-run examples.
6. Run all 0035G unit tests.
7. Review proposed register and change-log entries.
8. Validate the full repository.
9. Commit and push only after all mandatory checks pass.

## Acceptance commands

```text
python 13_Project_Genesis/Validators/validate_passport_monitoring_run.py 08_Product_Passports/Examples/Output/valid_no_action_run.example.json
python 13_Project_Genesis/Validators/validate_passport_monitoring_run.py 08_Product_Passports/Examples/Output/valid_alert_run.example.json
python 13_Project_Genesis/Validators/validate_passport_monitoring_run.py 08_Product_Passports/Examples/Output/invalid_auto_reinstatement_run.example.json
python -m unittest discover -s 13_Project_Genesis/Tests -p "test_passport_monitor*.py"
```

## Expected result

- Valid no-action run: **PASS**
- Valid alert run: **PASS**
- Deliberately invalid automatic-reinstatement run: **FAIL**
- Unit tests: **all pass**

## Build contents

- Expiry, trigger monitoring and alert automation standard.
- Machine-readable monitoring-run JSON Schema.
- Read-only Project Genesis monitoring engine.
- Semantic validator and automated tests.
- Threshold, routing, action, schedule, run and alert registers.
- Notification, runbook and JSON templates.
- Current, expiring, expired and critical-trigger input examples.
- Valid no-action, valid alert and deliberately invalid output examples.
- Build manifest, decision record, proposed change log and file inventory.
