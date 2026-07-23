# Certiaura PowerShell Closure Evidence Output Standard

Build: `0059`

Every canonical close script must print one clearly delimited, copy-ready plain-text evidence block after exact commit, push and GitHub Actions verification. It must include build, candidate, title, commit, subject, run ID, workflow, attempt, branch, event, status, conclusion, timestamps, Actions URL, local/remote alignment, clean status, Git guard status, no-prompt status, final green endpoint and founder-ready status.

The same JSON evidence must be written to the external Build Reports directory and to the canonical local build-record path `Documentation/Build_Records/0059/Closure_Evidence/BUILD_0059_CLOSURE_EVIDENCE.json`. The local runtime report is intentionally ignored by Git so the repository remains clean while the evidence remains recoverable.
