# CERTIAURA BUILD 0030A — ELAMIPRETIDE / SS-31 & GENERIC GLP-1 COVERAGE CORRECTION

**Build:** 0030A  
**Date:** 2026-07-16  
**Filename mode:** SHORT-PATH COMPATIBLE

## Purpose

This build closes the two product-family gaps identified by Build 0029.

## New permanent assets

- `CERT-PKS-000089` — Elamipretide / SS-31
- `CERT-PKS-000090` — Generic GLP-1 Supplier Product Family

## Catalogue rows closed

- `2S10` — SS-31 — 10 mg x 10 vials — USD 85
- `2S50` — SS-31 — 50 mg x 10 vials — USD 360
- `GP` — GLP-1, 5 mg/vial — 5 mg x 10 vials — USD 103

## Elamipretide control

- Elamipretide is the defined tetrapeptide `D-Arg-2,6-dimethyl-Tyr-Lys-Phe-NH2`.
- The United States authorised product is Forzinity, an elamipretide hydrochloride sterile solution.
- Forzinity received accelerated approval in September 2025 for a defined Barth-syndrome indication.
- Supplier powder does not inherit Forzinity formulation, strength, preservative, manufacturing, approval, label or clinical equivalence.
- European Union orphan designation and a United Kingdom paediatric investigation plan are not marketing authorisations.

## Generic GLP-1 control

The catalogue wording does not distinguish among:

- GLP-1(7-36) amide;
- GLP-1(7-37);
- longer proglucagon-derived forms;
- metabolites;
- modified or stabilised analogues;
- salt, counter-ion or formulation.

A permanent UAI is therefore allocated only to a deliberately identity-blocked supplier product family.

## Coverage milestone

After this build:

- source SKU coverage: 196 / 196;
- preliminary family coverage: 104 / 104;
- page 1-5 catalogue coverage gaps: 0.

## Clinical boundary

No Barth-syndrome, mitochondrial, glucose-control, weight-loss, infusion, dosing, injection or reconstitution protocol is created.

## Suggested commit

`Add Certiaura Build 0030A Elamipretide and generic GLP-1 coverage correction`
