# CERT-RKS-000003 — Retatrutide Patient Journey Report Generation Baseline

**Version:** 1.0.0
**Status:** Baseline — not scientifically complete
**Knowledge System:** RKS
**Build provenance:** CERT-BUILD-0043

## Capability

This asset defines the reusable report object generated from pseudonymised patient context, the reviewed retatrutide evidence corpus and the Build 0042 safety/monitoring integration layer.

## Relationship declarations

- `HAS_EVIDENCE` → Build 0041 retatrutide evidence corpus assets.
- `HAS_MONITORING` → Build 0042 monitoring assets.
- `HAS_CONTRAINDICATION` → Build 0042 contraindication assets.
- `HAS_SAFETY` → Build 0042 safety assets.
- `GENERATES` → patient journey report JSON, Markdown and print-ready HTML.
- `REQUIRES` → canonical Master Asset Register and validated source provenance.

## Certification limit

This baseline is operational infrastructure. It does not certify retatrutide as approved, safe for an individual, clinically appropriate or scientifically complete.
