# Build 0046 Lessons-Learned Baseline

## Carried forward

- Windows PowerShell 5.1 StrictMode requires array normalisation before `.Count` or indexing.
- PowerShell scripts remain ASCII-only.
- NativeCommandError from an expected negative Python fixture must be captured with temporary non-terminating error handling, explicit `LASTEXITCODE` inspection and restoration in `finally`.
- Raw and enriched longitudinal events must be normalised before sorting or hash-chain rebuilding.
- Validators must identify owned files through exact Asset Intent Manifest paths and exact build provenance, never numeric filename substrings.
- Transactional backups belong outside the canonical repository.
- Internal `.certiaura_backups` content blocks import even when Git ignores it.
- Canonical Master Asset Register discovery must be unique and exclude `.git` and prohibited backup paths.
- All repository text is UTF-8 without byte order mark, line feed-only, without trailing whitespace and with a final newline.
- Both `git diff --check` and `git diff --cached --check` are mandatory.

## Build 0046 preventive controls

- The exact Build 0045 commit is resolved from canonical history by exact subject, verified as an ancestor of HEAD and written to an external operator report before import.
- Analytics abstain when observations are insufficient.
- Direct identifiers are rejected before analysis or alert evaluation.
- Urgent routing lock takes precedence over all analytic or schedule rules.
- SVG output contains no scripts, remote resources or persistent state.
