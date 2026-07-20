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


## Post-push OneDrive restart StrictMode defect

- **Observed stage:** after the Build 0043 implementation commit and push had succeeded.
- **Failure:** `Start-OneDriveIfRequired` evaluated `.Count` on a scalar string.
- **Root cause:** the candidate-path pipeline was not wrapped around its complete output. Windows PowerShell 5.1 returned a scalar when exactly one executable path resolved.
- **Repository effect:** none; the implementation commit and remote push completed before the failure.
- **Operational effect:** OneDrive restart did not complete automatically and the wrapper workflow returned exit code 1.
- **Corrective action:** force the complete candidate pipeline into an array before evaluating `Count`.
- **Closure effect:** Build 0043 remains open until the correction commit and its GitHub Actions run are green.

## Correction-stage text normalisation defect

- **Observed gate:** `git diff --check`.
- **Failure:** generated Markdown contained line-ending characters interpreted as trailing whitespace.
- **Repository effect:** none; Git blocked the correction before staging, commit and push.
- **Corrective action:** normalise affected text files to UTF-8 without BOM, LF line endings, no trailing spaces or tabs, and exactly one final newline.
- **Preventive control:** every generated or amended text file must be normalised before either Git whitespace check.
