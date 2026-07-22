# Certiaura Build 0052 RC6 - Read Me First

Build 0052 title: Retatrutide cross-case signal aggregation, cohort surveillance, governed escalation and controlled knowledge feedback baseline.

RC1, RC2 and RC3 are withdrawn and must not be imported. RC3 passed canonical predecessor evidence, dry run and forced rollback, but clean reapply correctly rolled back because the cumulative updater imposed the current `control_family` field on the valid historical Build 0041 lessons matrix.

RC6 retains canonical Git-derived predecessor evidence and adds a strict version-aware historical lessons migration adapter. Historical aliases and backfilled fields are recorded with source provenance; the current Build 0052 lesson matrix remains strict. Transactional failures now emit the stable failure code, rollback reason, report path and backup path directly to the operator.

Run the delivered Windows PowerShell 5.1 regression. Do not perform canonical import unless it returns exactly:

```text
BUILD_0052_RC6_READY_FOR_CANONICAL_IMPORT
```
RC6 pre-delivery regression also corrected same-build cumulative lesson replay: replaying already embedded Build 0052 origins is idempotent, but a genuinely new recurrence without a strengthened control remains blocked.

RC1, RC2, RC3, RC4 and RC5 are withdrawn. RC6 additionally corrects PowerShell collection-comparison semantics for captured native output.

Build 0052 RC5 was withdrawn after canonical runtime proved that Builds 0039, 0040 and 0043-0046 have no retained per-build lessons matrices. RC6 validates those legacy builds through exact SHA-256-bound lesson-ID sets already present in the authoritative cumulative ledger and prohibits fabricated matrices.
