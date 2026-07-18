# CERTIAURA BUILD 0035E — READ FIRST

**Build title:** Add Certiaura Build 0035E supplier evidence review, verification and Product Passport™ approval workflow  
**Build ID:** CERT-BUILD-0035E  
**Authorisation:** PRODUCTION STARTED — awaiting founder GREEN after review  
**Build date:** 2026-07-18  
**Implementation state:** Repository-ready build pack; canonical implementation occurs only after successful import, validation, commit and push.  
**Primary systems:** PPS (Product Passport System), EKS (Evidence Knowledge System), MPS (Marketplace System), SYS (Platform System)

## Purpose

Build 0035D controls what suppliers submit. Build 0035E controls what Certiaura does with that submission: intake review, evidence verification, claim-level decisions, risk escalation, final approval, public-display permission and marketplace eligibility.

## Dependency

This build requires the installed outputs of:

- `CERT-BUILD-0035D — Supplier Evidence and Product Passport™ Submission Standard`

It extends 0035D. It does not amend, supersede or duplicate it.

## Critical rule

> A structurally valid supplier submission is not a verified Product Passport. Verification is a separate, recorded and reviewable Certiaura decision.

## Install order

1. Import this build pack into the canonical Certiaura repository while preserving relative paths.
2. Allocate permanent Universal Asset Identifiers through the Master Asset Register where marked `UAI_ALLOCATION_REQUIRED`.
3. Confirm Build 0035D schema and validator remain installed and unchanged.
4. Run the 0035E validator against all three examples.
5. Run the unit test suite.
6. Review proposed register and change-log entries.
7. Validate the full repository.
8. Commit and push only after all mandatory checks pass.

## Acceptance commands

```text
python 13_Project_Genesis/Validators/validate_product_passport_review_decision.py 08_Product_Passports/Examples/valid_verified_review.example.json
python 13_Project_Genesis/Validators/validate_product_passport_review_decision.py 08_Product_Passports/Examples/valid_conditional_review.example.json
python 13_Project_Genesis/Validators/validate_product_passport_review_decision.py 08_Product_Passports/Examples/invalid_verified_review.example.json
python -m unittest discover -s 13_Project_Genesis/Tests -p "test_product_passport_review_decision_validator.py"
```

## Expected result

- Valid verified review: **PASS**
- Valid conditional review: **PASS**
- Invalid verified review: **FAIL**
- Unit tests: **all pass**

## Build contents

- Review, verification and approval workflow standard.
- Machine-readable review-decision JSON Schema.
- Review-decision template.
- Reviewer checklist.
- State-transition matrix.
- Risk and escalation matrix.
- Review decision and claim review registers.
- Project Genesis validator and unit tests.
- Valid verified, valid conditional and deliberately invalid examples.
- Build manifest, decision record, proposed change log and file inventory.
