# Decision Record — CERT-BUILD-0035I

**Decision:** Approve an integrated supplier qualification, onboarding, risk tiering, audit and continuous assurance work package.  
**Status:** GREEN / repository-ready  
**Date:** 2026-07-19

## Context

Builds 0035D–0035H govern product evidence, review, publication, monitoring and remediation. A supplier-level assurance gate was required to control which organisations may participate and to keep that status under continuous review.

## Decision

Adopt one integrated build covering due diligence, onboarding, evidence requirements, risk scoring, human qualification, audit planning, continuous monitoring, restrictions, suspension, Approved Supplier List controls, dashboards and Project Genesis automation.

## Controls retained

- Supplier qualification does not verify a product, batch or claim.
- No automatic positive supplier decision.
- Four-eyes approval for qualification and conditional approval.
- Critical flags override numeric scores.
- Separate Product Passport™ and Marketplace decisions.
- Immutable history and source hashes.

## Consequence

Implementation must extend the existing PPS, EKS, MPS and SYS structures. It must not create a parallel supplier knowledge system or bypass the installed 0035D–0035H controls.
