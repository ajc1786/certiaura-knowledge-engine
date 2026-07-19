# CERTIAURA BUILD 0037 — READ FIRST

**Build title:** Scientific content claims advertising AI recommendation and responsible communications controls  
**Build ID:** CERT-BUILD-0037  
**Package status:** GENERATED — CORRECTED REISSUE  
**Build date:** 2026-07-19  
**Dependency:** Build 0038 must be installed and `ACTIONS_GREEN_CLOSED`.  
**Canonical implementation:** Only after Project Genesis dry run, transactional apply, full validation, commit, push and GitHub Actions green.

## Purpose

Install the end-to-end control system for scientific claims, advertising, artificial intelligence recommendations and responsible communications without changing previously agreed governance.

## Import sequence

1. Pull the latest canonical repository and confirm Build 0038 is present.
2. Import this ZIP through Project Genesis.
3. Review `DRY_RUN_ROUTING_REPORT.json` and `DRY_RUN_REPORT.json` before applying.
4. Confirm the canonical register resolved uniquely at `Documentation/Master_Asset_Register.csv`.
5. Confirm existing Universal Asset Identifiers are preserved and genuinely new assets receive new identifiers only through the installed reconciler.
6. Apply the transaction.
7. Run the Build 0037 validators and the full repository validator.
8. Confirm no blank or duplicate Universal Asset Identifiers, no orphan formal assets, no unresolved collisions and no `NO NEW UAI` placeholder.
9. Commit and push with the exact commit message below.
10. Confirm GitHub Actions green before closing Build 0037 or starting Build 0039.

## Exact commit message

```text
Add Certiaura Build 0037 scientific content claims advertising AI recommendation and responsible communications controls
```

## Acceptance commands

```text
python -m unittest discover -s 13_Project_Genesis/Tests -p "test_build_0037*.py"
python 13_Project_Genesis/Validators/validate_scientific_claim.py 13_Project_Genesis/Tests/Fixtures/Build_0037/valid_scientific_claim.example.json
python 13_Project_Genesis/Validators/validate_communication_approval.py 13_Project_Genesis/Tests/Fixtures/Build_0037/valid_communication_approval.example.json
python 13_Project_Genesis/Validators/validate_ai_recommendation_output.py 13_Project_Genesis/Tests/Fixtures/Build_0037/valid_ai_educational_output.example.json
python 13_Project_Genesis/Validators/validate_build_0037_repository.py .
```
