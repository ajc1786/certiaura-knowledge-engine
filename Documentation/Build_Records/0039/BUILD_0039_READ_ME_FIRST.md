# CERTIAURA BUILD 0039 — READ FIRST

**Build title:** evidence ingestion citation management living evidence surveillance and scientific review controls
**Build ID:** CERT-BUILD-0039
**Package version:** 1.3.2
**State:** GENERATED — awaiting controlled dry run/import
**Prerequisite:** Build 0038 closed and repository clean at its green baseline.

## Withdrawal notice

Build 0039 package v1.3.0 is withdrawn because of the recovery cleanup defect. Build 0039 package v1.3.1 is withdrawn because its manifest regression test scanned the full installed repository. Do not dry-run or apply either package again.

## v1.3.2 correction

Manifest validation now compares package-owned declarations with the package inventory and verifies those declared paths exist after installation, while ignoring unrelated repository content. The v1.3.1 empty-only, non-recursive recovery controls remain retained.

## Exact commit message

```text
Add Certiaura Build 0039 evidence ingestion citation management living evidence surveillance and scientific review controls
```

## Installation sequence

Pause OneDrive → confirm clean repository → dry run → review all reports → apply → validate → commit and push → confirm GitHub Actions green.
