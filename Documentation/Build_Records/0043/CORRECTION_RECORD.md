# Build 0043 Correction Record

**Correction identity:** Build 0043 corrected reissue; no new build number consumed.
**Observed gate:** Real Windows PowerShell 5.1 parser precheck.
**Observed failure:** `Run_Certiaura_Build_0043.ps1` reported a missing string terminator and closing brace.

## Root cause

The script contained a Unicode em dash in an otherwise UTF-8-without-BOM `.ps1` file. Windows PowerShell 5.1 does not reliably interpret UTF-8 without a byte-order mark. The non-ASCII byte sequence was decoded unsafely and caused the native parser to lose the quoted-string boundary.

## Corrective action

- Replaced the Unicode em dash with an ASCII hyphen.
- Re-encoded every Build 0043 `.ps1` file as ASCII with repository-normalised LF line endings.
- Added package preflight rejection for any non-ASCII byte in a `.ps1` file.
- Added the same prohibition to the Windows PowerShell 5.1 regression script, repository validator and unit tests.
- Configured the synthetic Git repository to disable inherited automatic line-ending conversion warnings.

## Release effect

The earlier Build 0043 ZIP is superseded and must not be imported. The corrected reissue retains the same Build 0043 title and exact commit message. The real Windows PowerShell 5.1 end-to-end regression remains mandatory before canonical import.
