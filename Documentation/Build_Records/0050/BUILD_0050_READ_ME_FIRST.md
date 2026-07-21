# Build 0050 Read Me First

Run the complete Windows PowerShell 5.1 regression before canonical import. The package is fail-closed, uses external transactional backups and requires exact Build 0049 commit ancestry.

## RC2 correction

The post-apply validator is restricted to exact Build 0050 example paths declared in the Asset Intent Manifest. Shared historical example-folder scans are prohibited.
