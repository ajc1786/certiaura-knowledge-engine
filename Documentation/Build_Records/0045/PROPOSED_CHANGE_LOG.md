# Proposed Change Log - Build 0045

- Add pseudonymised Retatrutide longitudinal journey tracking.
- Add append-only event hash-chain integrity.
- Add deterministic review scheduling and urgent-routing lock.
- Add clinician handoff JSON and Markdown generation.
- Add local memory-only journey viewer.
- Add exact ownership validation, external backup enforcement and rollback controls.

## Corrected Windows negative-fixture handling

Correct the Build 0045 Windows PowerShell 5.1 harness so deliberate Python rejection is captured as an expected non-zero exit without allowing native stderr to terminate the harness. Preserve fail-closed handling for all unexpected commands.
