# Build 0043 Lessons-Learned Baseline

The close-out review must record defects, root causes, time lost, corrective actions, preventive controls and regression tests. At generation, the following inherited lessons are mandatory:

- Test the complete operator workflow, not only the ZIP structure and unit tests.
- Use Windows PowerShell 5.1 StrictMode-compatible property handling; optional JSON properties must be added or updated safely rather than assigned blindly.
- Resolve the package deterministically and validate its content checksums.
- Stop and restart OneDrive around controlled writes.
- Preserve a transactional backup and recoverable Git checkpoint.
- Validate the canonical Master Asset Register before and after import.
- Reject wrapper folders, path collisions, silent overwrites, orphan assets, duplicate Universal Asset Identifiers and unexpected deletions.
- Disable Python bytecode and block runtime artefacts.
- Stage all package changes, then run `git diff --check` and `git diff --cached --check`.
- Do not declare closure until the import commit, close-out evidence, GitHub Actions and final continuation checkpoint are all evidenced.

## Build 0043 pre-release defect

- **Defect:** Windows PowerShell 5.1 parser rejected `Run_Certiaura_Build_0043.ps1`.
- **Root cause:** Unicode punctuation in a UTF-8-without-BOM PowerShell script.
- **Corrective action:** all release `.ps1` files are now ASCII-only with repository-normalised LF line endings.
- **Preventive control:** package preflight, native PS5.1 regression, repository validator and unit tests all block non-ASCII PowerShell scripts.
- **Regression requirement:** the corrected ZIP must repeat the complete Windows PowerShell 5.1 regression before import.
