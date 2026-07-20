# Build 0045 Continuation Checkpoint Update

**Last closed build:** Build 0044 - `ACTIONS_GREEN_CLOSED`
**Current build:** Build 0045 - `CORRECTED_REISSUE_WINDOWS_PS51_GATE_REQUIRED`

## Immediate action

Run the Build 0045 Windows PowerShell 5.1 release regression.

## Hold point

Do not import Build 0045 until the release regression passes. Do not begin Build 0046 until Build 0045 is imported, validated, committed, pushed and GitHub Actions are green.

## Corrected reissue checkpoint

The first Windows PowerShell 5.1 attempt failed closed on raw seed event enrichment. A corrected same-build package is required to pass the complete release regression before canonical import. Build 0046 remains on hold.

## Second Windows regression correction

Build 0045 remains unimported. The second Windows PowerShell 5.1 regression correctly rejected identifiable input but the harness terminated on expected native stderr before inspecting the non-zero exit code. The same-build package now captures expected native failure explicitly and requires a fresh Windows PowerShell 5.1 pass before canonical import.
