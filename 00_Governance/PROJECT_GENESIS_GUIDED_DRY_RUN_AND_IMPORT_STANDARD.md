# Project Genesis Guided Dry Run and Import Standard

**UAI:** CERT-SYS-000848
**Version:** 1.1.0

## Purpose

Provide a controlled operator workflow for package inspection, dry run, transactional import, validation and recovery.

## Mandatory sequence

1. Pause synchronisation software that can race repository writes.
2. Confirm the repository branch and clean working tree.
3. Inspect package roots, wrapper status, duplicate paths and case collisions.
4. Resolve one canonical Master Asset Register.
5. Validate complete Asset Intent Manifest coverage.
6. Produce routing, collision and register-change reports.
7. Create an external transactional backup or recoverable Git checkpoint.
8. Apply approved actions only.
9. Run package, repository, register and relationship validation.
10. Recover the entire transaction if any mandatory gate fails.

## Directory cleanup safety amendment — Build 0039 v1.3.2

Recovery may call only non-recursive `rmdir` against a directory that the current transaction journal proves it created and that is proven empty immediately before removal. Existing repository directories, sibling files, sibling folders and nested sibling content must never be recursively deleted.
