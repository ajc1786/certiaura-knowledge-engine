# Decision Record — CERT-BUILD-0035H

**Decision:** Approve an integrated Product Passport™ remediation, evidence refresh, reinstatement and supplier performance work package.  
**Status:** GREEN / repository-ready  
**Date:** 2026-07-18

## Context

Builds 0035D–0035G establish submission, evidence review, lifecycle publication and monitoring alerts. A controlled route was required to resolve alerts without allowing automatic positive assurance.

## Decision

Adopt a single integrated build covering case creation, corrective action, refreshed evidence, re-review, alert closure, passport reinstatement, separate marketplace restoration, supplier escalation, repeat-failure tracking, performance scoring and dashboarding.

## Controls retained

- No automatic evidence verification.
- No automatic alert closure.
- No automatic passport or marketplace reinstatement.
- Four-eyes approval for positive restoration.
- Separate marketplace decision and transaction.
- Immutable history and source hashes.

## Consequence

Future implementation should consume this package through Project Genesis and the existing registers. It must not create a parallel supplier-governance architecture.
