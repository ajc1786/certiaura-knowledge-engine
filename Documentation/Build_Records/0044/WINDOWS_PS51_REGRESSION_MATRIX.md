# Build 0044 Windows PowerShell 5.1 Regression Matrix

The release regression must complete all rows before the package is authorised for canonical import.

| Gate | Required evidence |
|---|---|
| Package identity | Exact SHA-256 match |
| CMD parser precheck | CMD launches Windows PowerShell 5.1 parser harness successfully |
| PowerShell source control | All package `.ps1` files are ASCII-only and parser-clean |
| Build 0043 dependency | Implementation commit and unique correction prefix are ancestors/present |
| Source repository | Clean canonical working tree |
| Synthetic repository | Local clone preserves unrelated historical content |
| Project Genesis dry-run | `DRY_RUN_VALIDATED`, zero conflicts and errors |
| Transactional apply | External backup and `APPLIED_VALIDATED` |
| Master Asset Register | Two formal assets, preserved existing rows, no duplicate UAI/path |
| Patient journey | Build 0043 report generator passes |
| Branded report | Deterministic HTML and valid local PDF pass |
| Controlled conversation | Grounded/abstained, refused, urgent-locked and identifier-rejected states pass |
| Interface security | Loopback-only, no remote dependencies, no unsafe DOM or browser storage |
| Automated tests | All Build 0044 tests pass |
| Runtime hygiene | No `__pycache__`, `.pyc`, `.pyo` or guided runtime artefacts |
| Git working diff | `git diff --check` passes before staging |
| Git staged diff | `git diff --cached --check` passes after staging |
| Cleanup | Temporary repository removed |
| OneDrive recovery | Restart completes when it was stopped |
| Success declaration | Printed only after cleanup/recovery succeeds |

| Exact validator ownership scope | Asset Intent Manifest paths and `CERT-BUILD-0044` register provenance only |
| UAI/build-number collision regression | Unrelated non-compliant `CERT-BKS-000044` fixture is preserved and ignored |
