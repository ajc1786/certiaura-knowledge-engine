# Build 0044 Lessons-Learned Baseline

## Controls inherited from Build 0043

### Windows PowerShell 5.1 encoding

**Prior defect:** non-ASCII punctuation in a UTF-8-without-BOM PowerShell script caused a parser failure.

**Build 0044 prevention:**

- every `.ps1` file is ASCII-only;
- package preflight rejects non-ASCII PowerShell bytes;
- native Windows PowerShell 5.1 parsing is mandatory;
- a CMD-launched parser harness is included in the full regression.

### Pipeline cardinality under StrictMode

**Prior defect:** a one-item pipeline became a scalar, causing `.Count` to fail during OneDrive restart.

**Build 0044 prevention:**

- variable-cardinality outputs are wrapped in `@(...)`;
- candidate paths use `System.Collections.Generic.List[string]`;
- the regression deliberately reduces the OneDrive candidate set to one item and checks `.Count`;
- success is printed only after cleanup and restart complete.

### Generated text and Git hygiene

**Prior defect:** Windows-generated Markdown failed `git diff --check` due to line-ending/trailing-whitespace behaviour.

**Build 0044 prevention:**

- repository text uses UTF-8 without BOM and LF;
- trailing spaces and tabs are prohibited;
- exactly one final newline is required;
- `git diff --check` runs before staging;
- `git diff --cached --check` runs after staging;
- tests scan Build 0044 text assets.

### Continuous-learning closure rule

Build 0044 cannot close until defects, root causes, time lost, corrective actions, preventive controls and new regression tests are added to the authoritative continuity source and the next build baseline.

## Build 0044 anticipated risk controls

- interface data remains in memory only;
- no request body is persisted or logged;
- direct identifiers are rejected before query execution;
- urgent responses lock the current conversation;
- PDF rendering is local and visually inspected;
- no production-security claim is made for the local baseline.

## Build 0044 validator ownership-scope defect

- **Defect:** the real Windows PowerShell 5.1 regression failed after a successful synthetic import because the repository validator reported historical files as Build 0044 text defects.
- **Root cause:** the validator and tests used the substring `0044` as a proxy for build ownership. This also matched unrelated Universal Asset Identifiers ending in `000044`.
- **Time lost:** the first real Windows regression had to be diagnosed, corrected, repackaged and repeated.
- **Repository effect:** none. The failure occurred in the temporary synthetic repository before canonical import authorisation.
- **Corrective action:** derive the validation set from exact Asset Intent Manifest paths and Master Asset Register rows carrying `CERT-BUILD-0044` provenance.
- **Preventive control:** build ownership must never be inferred from a numeric filename substring, identifier suffix or free-text occurrence.
- **Regression test:** the synthetic repository now commits an unrelated `CERT-BKS-000044` file containing CRLF and trailing whitespace. The validator must ignore it while still checking every Build 0044-owned text file.
