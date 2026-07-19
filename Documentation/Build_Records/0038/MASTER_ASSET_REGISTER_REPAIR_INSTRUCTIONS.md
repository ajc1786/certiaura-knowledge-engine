# Master Asset Register Repair Instructions

Use only the Build 0038 Version 1.4.0 conflict-resolution reissue.

The corrected import updates:

`Documentation/Master_Asset_Register.csv`

## Dry-run acceptance gate

Proceed to apply only when the dry-run report confirms:

- `total_conflicts` equals `0`;
- no duplicate incoming or allocated Universal Asset Identifier remains;
- all physical representations are covered by either `Repository Path` or `Supporting Files`;
- the `NO NEW UAI` placeholder is scheduled for removal;
- the target register is the exact CSV opened by Project Genesis.

After successful apply, select **Open Master Asset Register** in Project Genesis. The register must contain populated permanent identifiers and must not contain `NO NEW UAI`.

Do not manually edit or bypass a failed transaction.
