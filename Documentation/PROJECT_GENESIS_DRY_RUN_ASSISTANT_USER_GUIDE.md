# Project Genesis Dry Run Assistant — User Guide

## Build 0039 v1.3.2

1. Pause OneDrive before the dry run or import.
2. Confirm `git status --short --untracked-files=all` is empty.
3. Do not use any Build 0039 v1.3.0 package or the withdrawn `(3).zip`.
4. Run:

```text
python 13_Project_Genesis/Import/run_build_0039_import.py <ZIP_PATH> <REPOSITORY_PATH>
```

5. Review `Documentation/Build_Records/0039/GUIDED_DRY_RUN_REPORT.json`.
6. Apply only when `valid`, `apply_allowed`, routing, conflicts, register changes and recovery-safety controls pass.
7. Apply by adding `--apply`.
8. Validate, commit with the exact locked message, push and confirm GitHub Actions green.

Recovery uses `recover_failed_build_import.py` and the external transaction journal. It never performs recursive directory deletion.
