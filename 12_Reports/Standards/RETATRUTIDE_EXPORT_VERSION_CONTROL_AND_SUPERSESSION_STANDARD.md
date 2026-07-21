# Retatrutide Export Version Control and Supersession Standard

**Build provenance:** `CERT-BUILD-0048`
**Version:** 1.0.0
**Status:** Controlled baseline

## Objective

Maintain an immutable and auditable chain for each Retatrutide clinician export.

## Version chain

Each version record must include:

- export identifier;
- semantic version;
- SHA-256;
- generated timestamp;
- source journey identifier and source-input hashes;
- generator version and build provenance;
- predecessor export identifier where applicable;
- change summary;
- current state;
- approval record identifier where approved.

## Rules

1. A version is immutable after hashing.
2. A changed export receives a new version and hash.
3. One version may supersede only its declared immediate predecessor.
4. A chain may not contain cycles, missing predecessors or duplicate versions.
5. Withdrawal does not delete the version.
6. Only one version per export family may be `CURRENT_APPROVED`.
7. An unapproved version cannot supersede the current approved version for handoff purposes.
8. Source input hashes and the generated export hash must be retained.
