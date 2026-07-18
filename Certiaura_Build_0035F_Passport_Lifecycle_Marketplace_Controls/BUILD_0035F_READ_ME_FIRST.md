# CERTIAURA BUILD 0035F — READ FIRST

**Build title:** Product Passport™ publication, lifecycle and marketplace controls  
**Build ID:** CERT-BUILD-0035F  
**Authorisation:** GREEN — founder authorised  
**Build date:** 2026-07-18  
**Implementation state:** Repository-ready build pack; canonical installation occurs after import, validation, register review, commit and push.  
**Primary systems:** PPS (Product Passport System), EKS (Evidence Knowledge System), MPS (Marketplace System), SYS (Platform System)

## Purpose

Build 0035D controls supplier submission. Build 0035E controls review and verification. Build 0035F controls approved public release, ongoing lifecycle state, trigger-led suspension or expiry, supersession and separate marketplace eligibility.

## Critical rule

> A verified Product Passport may be published only within its approved claim scope and effective period; marketplace eligibility remains a separate decision.

## Dependencies

- `CERT-BUILD-0035D — Supplier Evidence and Product Passport™ Submission Standard`
- `CERT-BUILD-0035E — Supplier Evidence Review, Verification and Product Passport™ Approval Workflow`

This build extends those controls and does not amend or replace them.

## Install order

1. Import the pack while preserving relative paths.
2. Allocate permanent Universal Asset Identifiers where marked.
3. Confirm 0035D and 0035E remain installed and unchanged.
4. Run the 0035F validator against all examples.
5. Run the 0035F unit tests.
6. Review proposed register and change-log entries.
7. Validate the full repository.
8. Commit and push only after all mandatory checks pass.

## Acceptance commands

```text
python 13_Project_Genesis/Validators/validate_passport_lifecycle.py 08_Product_Passports/Examples/valid_published.example.json
python 13_Project_Genesis/Validators/validate_passport_lifecycle.py 08_Product_Passports/Examples/valid_suspended.example.json
python 13_Project_Genesis/Validators/validate_passport_lifecycle.py 08_Product_Passports/Examples/invalid_active_listing.example.json
python -m unittest discover -s 13_Project_Genesis/Tests -p "test_passport_lifecycle_validator.py"
```

## Expected result

- Valid published example: **PASS**
- Valid suspended example: **PASS**
- Deliberately invalid active-listing example: **FAIL**
- Unit tests: **all pass**

## Build contents

- Publication, lifecycle and marketplace control standard.
- Machine-readable lifecycle JSON Schema.
- Publication and lifecycle event templates.
- Public-field, lifecycle-state and trigger matrices.
- Publication, lifecycle event and marketplace registers.
- Project Genesis semantic validator and unit tests.
- Valid published, valid suspended and deliberately invalid examples.
- Build manifest, decision record, proposed change log and file inventory.
