# BUILD 0035E — IMPLEMENTATION NOTES

## Dependency check

Build 0035E assumes Build 0035D is already installed. Do not replace or edit the 0035D submission schema during this import.

## Repository integration

Suggested locations are already represented in the pack. Preserve them unless the canonical repository has a later explicit path standard.

## Universal Asset Identifiers

Allocate permanent Universal Asset Identifiers on import for formal standards, schemas, registers, validator assets and decision records where required by the Master Asset Register.

## Project Genesis integration sequence

1. Validate the source 0035D submission.
2. Freeze and hash the reviewed submission snapshot.
3. Create a 0035E review decision from the template.
4. Validate the review decision.
5. Write claim-level decisions to the claim review register.
6. Write overall decision to the review decision register.
7. Update the 0035D submission status register.
8. Update Product Passport public-display state.
9. Update marketplace eligibility only through its separate field and decision basis.
10. Commit the immutable decision record.

## Automation boundary

Project Genesis may automate:

- structural checks;
- identifier and cross-reference checks;
- allowed transition checks;
- missing field detection;
- date and expiry warnings;
- four-eyes identity mismatch checks;
- register updates; and
- generation of review worklists.

Project Genesis must not automatically assert:

- document authenticity;
- laboratory independence;
- scientific validity;
- regulatory approval;
- legal marketability;
- clinical suitability; or
- final claim verification without the required human decision.

## Backwards compatibility

The 0035E decision object references the 0035D submission by identifier, schema version and SHA-256 snapshot hash. The source submission remains unchanged.

## Acceptance criteria

- All JSON files parse.
- Valid verified example passes.
- Valid conditional example passes.
- Invalid verified example fails on multiple independent controls.
- Unit tests pass.
- VERIFIED requires four-eyes approval.
- Public display requires a VERIFIED claim.
- VERIFIED claims require E4 or E5 evidence.
- Batch-specific VERIFIED claims require batch linkage.
- High or critical risk blocks VERIFIED status.
- Marketplace eligibility remains separate.
- Audit record is immutable.
