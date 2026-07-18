# BUILD 0035F IMPLEMENTATION NOTES

## Repository integration

Copy the contents beneath the build root into the matching canonical repository folders. Do not retain a second competing copy of an existing register where the repository already contains the live register; merge the proposed header or rows using normal change control.

## UAI allocation

Allocate Universal Asset Identifiers through the existing Master Asset Register for formal standards, schemas, templates and registers where required. The placeholder `UAI_ALLOCATION_REQUIRED` must not be treated as a final identifier.

## Validator integration

The validator uses only the Python standard library. Add it to the repository validation workflow after confirming path conventions. Schema validation and semantic validation are complementary; neither should silently replace the other.

## Data migration

No historical passport should be marked `PUBLISHED` solely because it exists in chat or a spreadsheet. It must be linked to a valid 0035E decision or remain draft/unassessed until reviewed.

## Public interface rule

The public interface must derive current status from the lifecycle record. It must not cache or display a passport as current after suspension, expiry, withdrawal or supersession.

## Marketplace integration

Marketplace state must be read from the separate marketplace decision fields or register. Do not map `VERIFIED` to `ELIGIBLE` automatically.

## Naming

The downloadable build archive follows the concise locked convention:

`Certiaura_Build_0035F_Passport_Lifecycle_Marketplace_Controls.zip`
