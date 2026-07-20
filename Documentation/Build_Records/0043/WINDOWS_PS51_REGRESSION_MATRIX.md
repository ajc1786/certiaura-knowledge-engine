# Windows PowerShell 5.1 Regression Matrix

| Gate | Required result |
|---|---|
| PowerShell version | Windows PowerShell 5.1 |
| PowerShell script encoding | ASCII-only `.ps1` files with repository-normalised LF line endings |
| CMD/parser precheck | PASS |
| Package content checksum | PASS |
| Synthetic repository with unrelated history | PASS |
| Master Asset Register resolution | PASS |
| Dry-run | DRY_RUN_VALIDATED |
| Transactional apply | APPLIED_VALIDATED |
| External backup | Created and readable |
| Report generator | Valid JSON and Markdown |
| AI query grounding | Valid response with provenance or explicit abstention |
| Safety refusal | Personal dosing request refused |
| Urgent routing | Urgent symptom query routed to professional assessment |
| Validators and tests | PASS |
| Runtime artefact check | Clean |
| Unexpected deletion check | None |
| `git diff --check` | PASS |
| `git diff --cached --check` | PASS |
| OneDrive restoration | Restored to prior state |


## Post-success cleanup and recovery path

The full Windows PowerShell 5.1 operator regression must verify:

- the implementation commit and push complete successfully;
- the `finally` block executes;
- a single resolved OneDrive executable remains an array;
- `Count` and indexed access succeed under StrictMode;
- OneDrive restarts after both successful and failed controlled workflows;
- a cleanup failure cannot misrepresent whether the implementation commit was pushed.

## Generated text and Git hygiene gate

The Windows PowerShell 5.1 regression must verify that every generated or amended Markdown, JSON, CSV, Python, PowerShell, command and text file has:

- UTF-8 without BOM where UTF-8 is required;
- ASCII-only content for PowerShell scripts where mandated;
- LF repository line endings;
- no trailing spaces or tabs;
- one final newline;
- a passing `git diff --check`;
- a passing `git diff --cached --check`.
