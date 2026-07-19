# Decision Record — Build 0035K

**Decision ID:** CERT-DEC-0035K-001  
**Date:** 2026-07-19  
**Status:** Proposed for canonical registration upon import  

## Decision

Implement an integrated marketplace transaction-control chain covering contracting, order assurance, fulfilment, goods receipt, incident response, withdrawal/recall, payment holds and settlement.

## Existing decisions retained

- Supplier evidence is submitted, not verified, until controlled review.
- Supplier qualification does not verify products or batches.
- Product Passport™, Marketplace and supplier statuses remain independent.
- Automated systems may restrict and recommend but may not create approval.
- Existing UARS, registers, dashboards, decision log and repository architecture are extended rather than duplicated.
- The final legal/regulatory route for direct peptide sales remains unlocked and is not decided by this build.

## Critical control

An open critical incident or active recall blocks affected order release and creates protective payment, listing and passport restrictions until authorised human decisions change the relevant independent statuses.
