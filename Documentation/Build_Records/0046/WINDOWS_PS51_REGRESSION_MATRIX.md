# Build 0046 Windows PowerShell 5.1 Regression Matrix

| Gate | Expected result |
|---|---|
| Package SHA-256 | Exact match |
| PowerShell parser precheck | PASS |
| ASCII-only PowerShell | PASS |
| Package preflight and checksums | PASS |
| Internal backup negative fixture | BLOCKED |
| Project Genesis dry-run | DRY_RUN_VALIDATED |
| Project Genesis apply | APPLIED_VALIDATED |
| External backup location | PASS |
| Exact-scope validator | PASS |
| Automated tests | 21 tests, PASS |
| Analytics CLI | READY_FOR_REVIEW |
| SVG trend render | PASS |
| Controlled alert | NO_ALERT |
| Identifier negative fixture | REJECTED, no output |
| Historical UAI 000046 fixture | PRESERVED and excluded |
| Git unstaged and staged checks | PASS |
