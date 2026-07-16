# CERTIAURA BUILD 0028A — BIOCHEMICAL & RESEARCH ANCILLARY PRODUCTS

**Build:** 0028A  
**Date:** 2026-07-16  
**Filename mode:** SHORT-PATH COMPATIBLE

## Architecture decision implemented

These items are intentionally classified outside the Peptide Knowledge System.

### New Marketplace Product System assets

- `CERT-MPS-000001` — AICAR Supplier Product Family
- `CERT-MPS-000002` — Melatonin Supplier Vial Family
- `CERT-MPS-000003` — Glutathione Supplier Vial Family
- `CERT-MPS-000004` — 5-Amino-1MQ Supplier Product Family
- `CERT-MPS-000005` — NAD Supplier Product Family
- `CERT-MPS-000006` — SLU-PP-322 Identity-Candidate Product Family

### New Product Passport System assets

- `CERT-PPS-000001`–`CERT-PPS-000006`

## Catalogue SKUs

- `AR50` — AICAR — 50 mg x 10 vials — USD 63
- `AR100` — AICAR — 100 mg x 10 vials — USD 99
- `MT10` — Melatonin — 10 mg x 10 vials — USD 56
- `GTT` — Glutathione — 1,500 mg x 10 vials — USD 108
- `5AM` — 5-amino-1MQ — 5 mg x 10 vials — USD 32
- `10AM` — 5-amino-1MQ — 10 mg x 10 vials — USD 42
- `50AM` — 5-amino-1MQ — 50 mg x 10 vials — USD 65
- `NJ3100` — NAD — 100 mg x 10 vials — USD 37
- `NJ250` — NAD — 250 mg x 10 vials — USD 56
- `NJ500` — NAD — 500 mg x 10 vials — USD 78
- `NJ1000` — NAD — 1,000 mg x 10 vials — USD 126
- `SLU5` — supplier-labelled SLU-PP-322 — 5 mg x 10 vials — USD 121

## Critical controls

- AICAR requires separation of AICA riboside/acadesine from the phosphorylated AICAR/ZMP identity.
- Melatonin authorised oral products do not validate an injectable or unspecified supplier vial.
- Glutathione requires reduced-versus-oxidised form, route, sterility and endotoxin closure.
- 5-amino-1MQ is a small-molecule NNMT inhibitor with preclinical animal evidence and no validated human dose.
- NAD requires NAD+, NADH, salt, concentration, route and sterile-grade identity.
- The code is preserved exactly as `NJ3100` for the 100 mg entry.
- `SLU-PP-322` is not silently corrected to `SLU-PP-332`.
- Evidence for SLU-PP-332 cannot transfer to an unresolved SLU-PP-322 product.
- No weight-loss, exercise-mimetic, longevity, sleep, infusion, dosing or reconstitution protocol is created.

## Next build

Build 0028B will cover bacteriostatic water, acetic-acid water, botulinum toxin, hyaluronic acid, alprostadil and Lemon Bottle.

## Suggested commit

`Add Certiaura Build 0028A biochemical research and ancillary marketplace products`
