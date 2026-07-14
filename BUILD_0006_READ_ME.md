# CERTIAURA BUILD 0006 — RETATRUTIDE PRIMARY SOURCE CLOSURE & INTEGRITY GATE

**Build:** 0006  
**Version:** 0.6.0  
**Date:** 2026-07-14

## Purpose

Close primary-source gaps only where the primary source is actually retrievable and verifiable.

This build deliberately distinguishes:

- **Closed** — primary source captured and extracted.
- **Identified / extraction blocked** — primary source identity is known but full extraction could not be completed.
- **Open / primary source not captured** — evidence lead remains unresolved.
- **Superseded** — an earlier lower-tier source has been replaced by stronger evidence.

## Build 0006 result

### CERT-EKS-000012 — Phase 3 Type 2 Diabetes

Primary article identity:

- Journal: The Lancet
- PII: `S0140-6736(26)00967-0`
- URL: `https://www.thelancet.com/journals/lancet/article/PIIS0140-6736%2826%2900967-0/fulltext`

Current status:

**Primary source identified; automated full-text extraction blocked by publisher access control.**

This is **not** marked Closed.

### CERT-EKS-000010 — Body Composition

Current status:

**Primary publication identity preserved; direct primary page / DOI still not captured.**

### CERT-EKS-000013 — TRIUMPH-4

Current status:

**Primary source still not captured.**

Secondary reporting remains an evidence lead only.

### CERT-EKS-000014 — Liver-Fat / MASLD

Current status:

**Primary source still not captured.**

Specific quantitative claims must not be promoted into the canonical primary-evidence layer until the primary source is captured.

## New controls

- Primary Source Closure Standard
- Evidence Integrity Gate
- Source Access Log
- Primary Source Closure Register
- Retatrutide Evidence Source Integrity Summary
- Updated Evidence Index
- Updated Evidence Maturity Assessment
- Updated Preservation Gap Register
- Updated Production Dashboard
- Updated Change Log

Suggested commit message:

`Add Certiaura Build 0006 primary source closure and integrity gate`
