# Retatrutide Patient-Facing Interface Baseline

**Universal Asset Identifier:** CERT-RKS-000004
**Build:** CERT-BUILD-0044
**Version:** 1.0.0
**Status:** BASELINE
**Knowledge System:** RKS

## Purpose

This asset defines the first controlled patient-facing presentation layer for the canonical Retatrutide patient journey and evidence-query contracts introduced by Build 0043.

## Baseline capability

- local-only patient interface served on the loopback address;
- pseudonymised patient journey report generation;
- deterministic branded HTML report rendering;
- controlled conversion to PDF through an installed Chromium-family browser;
- explicit report-state, uncertainty, source provenance and clinician-discussion sections;
- no analytics, external scripts, remote fonts or persistent patient storage;
- no diagnosis, prescribing, dosing, titration, procurement or treatment selection.

## Safety boundary

The interface is an educational discussion-support layer. It consumes canonical repository outputs without weakening Build 0043 evidence grounding, abstention, refusal or urgent-routing controls.

## Dependencies

- Build 0043 Retatrutide patient journey report contract;
- Build 0043 Retatrutide AI query integration contract;
- Build 0042 safety and monitoring controls;
- Build 0041 evidence and citation controls.

## Completion status

This baseline is suitable for controlled local validation. It is not a production clinical system, authenticated patient portal, medical device or substitute for professional assessment.
