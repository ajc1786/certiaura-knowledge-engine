# Project Genesis v1.1 — Build Pack Import

## Status

Functional desktop Build Pack import added.

## New capability

The **Import Build Pack** button now:

1. Requires the Certiaura repository to be selected.
2. Prompts for an extracted Build Pack folder.
3. Validates that the Build Pack is outside the repository.
4. Scans the pack before importing.
5. Shows:
   - New files
   - Files that will replace existing files
   - Directories scanned
6. Requires confirmation before copying.
7. Copies files while preserving repository-relative paths.
8. Refreshes the repository dashboard after import.

## Safety controls

- The repository and Build Pack cannot be the same folder.
- The Build Pack cannot be inside the repository.
- The repository cannot be inside the Build Pack.
- The selected repository must contain `.git`.
- `.git`, `__pycache__` and `.pytest_cache` content are excluded.
- No Git commit or push occurs in v1.1.

## Next planned version

**Project Genesis v1.2 — Commit & Push**

The next version will add reviewed Git commit and push controls inside the desktop application.
