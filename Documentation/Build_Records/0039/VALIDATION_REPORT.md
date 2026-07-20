# Build 0039 v1.3.2 Validation Report

**Status:** FAIL

- Package has no build-named wrapper folder.
- All roots are canonical and repository-relative.
- Every package file is classified in the Asset Intent Manifest.
- Twelve formal assets are declared: two controlled updates and ten creations.
- Master Asset Register reconciliation preserves `CERT-SYS-000009` and `CERT-SYS-000082`.
- Python scripts compile.
- Build-specific unit tests pass.
- Valid fixtures pass and deliberately defective fixtures fail.
- Recovery uses transaction-owned directory tracking, proves emptiness and calls non-recursive `rmdir` only.
- Pre-existing sibling files, sibling folders and nested sibling content are preserved by regression tests.
- Package version is 1.3.2; v1.3.0 and v1.3.1 remain withdrawn.
- Manifest tests are safe in both isolated-package and installed-repository contexts.
