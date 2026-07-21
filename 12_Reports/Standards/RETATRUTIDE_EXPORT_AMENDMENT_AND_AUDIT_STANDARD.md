# Retatrutide Export Amendment and Audit Standard

Build provenance: CERT-BUILD-0049

An approved export is immutable. Corrections and clinician-requested changes create a new export identifier, new SHA-256, new approval decision and explicit predecessor reference.

## Required audit fields

- amendment identifier and reason;
- predecessor export identifier and SHA-256;
- replacement export identifier and SHA-256;
- feedback and follow-up references;
- human author and reviewer role references;
- created and approved timestamps;
- chain state and current-version flag.

Broken chains, cycles, in-place mutation and more than one current approved version are release-blocking defects.
