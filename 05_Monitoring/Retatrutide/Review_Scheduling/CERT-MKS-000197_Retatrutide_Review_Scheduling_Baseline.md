---
universal_asset_identifier: CERT-MKS-000197
version: 1.0.0
status: BASELINE
knowledge_system: MKS
owner: Certiaura
build_provenance: CERT-BUILD-0045
---

# Retatrutide Review Scheduling Baseline

## Purpose

Defines deterministic administrative review scheduling from pseudonymised longitudinal events without making clinical treatment decisions.

## Baseline controls

- Scheduling uses explicit policy intervals and recorded event dates.
- Urgent indicators override routine scheduling and create an immediate clinician-routing state.
- Overdue and missing-monitoring states are surfaced as discussion prompts, not diagnoses.
- No medication initiation, dose selection, titration or cessation instruction is produced.
- Every schedule item records its source event and policy rule.

## Relationships

- Parent: CERT-PKS-000001
- Requires: Retatrutide Longitudinal Journey Tracking Baseline
- Generates: Review schedule and clinician handoff prompts
