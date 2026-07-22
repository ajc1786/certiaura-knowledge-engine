# CERTIAURA LOCKED PREDECESSOR EVIDENCE AND RELEASE STANDARD

**Document ID:** CERT-GOV-PRED-001
**Version:** 1.4.0
**Status:** SUPERSEDED - CONTROLS RETAINED IN CUMULATIVE STANDARD
**Effective date:** 2026-07-21
**Authority:** Explicit founder instruction from Aidan Coleman
**Canonical repository path:** `00_Governance/CERTIAURA_LOCKED_PREDECESSOR_EVIDENCE_AND_RELEASE_STANDARD.md`
**Superseding source:** `00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md`

---

## Supersession notice

The predecessor-evidence controls in version 1.0.0 remain mandatory and have not been weakened or removed. They are now incorporated as the predecessor control family within the authoritative cumulative lessons source:

```text
00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md
```

Future builds must read and update the cumulative source. This file remains only as a canonical redirect and historical identity record so that no competing active lessons source exists.

Build 0052 RC1, RC2, RC3, RC4 and RC5 remain withdrawn and must not be imported. Build 0052 RC6 must implement the cumulative source, its companion JSON and its automatic updater before candidate release.

## RC2 manifest-schema compatibility amendment

Build 0052 RC2 is withdrawn after canonical runtime returned `PREDECESSOR_MANIFEST_PATH_INVALID`. Historical Asset Intent Manifests must be parsed through the strict version-aware adapter defined in the cumulative lessons source. The adapter may recognise path-bearing schema variants, but every path value must still originate from the canonical Git object and must pass normalisation, ambiguity, traversal, duplicate and case-collision controls. Build 0052 RC6 is the required corrective candidate.

## RC3 cumulative-lessons schema amendment

RC3 predecessor controls passed before the transaction rolled back on a historical lessons schema incompatibility. RC4 retains all predecessor controls unchanged and adds recorded migration of valid historical lesson matrices.

## RC4 PowerShell output assertion amendment

RC4 predecessor evidence and rollback controls passed, but the operator regression falsely rejected a valid rollback token because `-notmatch` was applied directly to a multi-line output collection. RC6 retains scalar output normalisation to a scalar before matching and run the locked multi-line positive and negative assertions.

Build 0052 RC5 was withdrawn after canonical runtime proved that Builds 0039, 0040 and 0043-0046 have no retained per-build lessons matrices. RC6 validates those legacy builds through exact SHA-256-bound lesson-ID sets already present in the authoritative cumulative ledger and prohibits fabricated matrices.
