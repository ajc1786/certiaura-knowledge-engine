# Retatrutide Patient Journey Report Standard

**Build:** CERT-BUILD-0043
**Version:** 1.0.0
**Status:** Baseline — controlled implementation
**Owner:** Certiaura

## Purpose

Define a deterministic, evidence-grounded and safety-gated report-generation process for a pseudonymised retatrutide patient journey. The report is educational and clinician-discussion support. It is not diagnosis, prescribing, dosing, treatment authorisation, emergency triage or a substitute for professional care.

## Dependencies

- Build 0041 retatrutide evidence corpus, citation graph and scientific-review baseline.
- Build 0042 retatrutide safety, monitoring, contraindication and clinical-outcome integration baseline.
- Canonical Master Asset Register and Universal Relationship Engine controls.

## Mandatory report sections

1. Report identity, generation timestamp and input hash.
2. Scope, investigational-status notice and non-medical-advice boundary.
3. Pseudonymised baseline context.
4. Journey phase and evidence-bounded milestone framework.
5. Monitoring schedule resolved from canonical monitoring assets.
6. Contraindication and caution flags resolved from canonical safety assets.
7. Clinical-outcome context resolved from reviewed evidence claims.
8. Red-flag escalation and emergency-routing notice.
9. Uncertainty, missing-data and abstention statements.
10. Source provenance containing repository paths, Universal Asset Identifiers and claim/evidence identifiers.
11. Clinician-discussion prompts.

## Deterministic generation rules

- Equivalent canonical input produces equivalent report content, excluding generated timestamp and output identifier.
- The generator must not invent citations, claims, probabilities, expected weight loss, dose schedules or treatment instructions.
- A source unavailable in the repository is recorded as `SOURCE_NOT_RESOLVED`; it is not replaced by model memory.
- Missing required safety data blocks a `READY_FOR_CLINICIAN_DISCUSSION` status.
- Any emergency symptom flag produces `URGENT_CLINICAL_ROUTING` and suppresses routine journey interpretation.
- Direct identifiers are prohibited. Inputs use a pseudonymous patient reference only.

## Output states

- `READY_FOR_CLINICIAN_DISCUSSION`
- `CONDITIONAL_MISSING_DATA`
- `URGENT_CLINICAL_ROUTING`
- `BLOCKED_UNSAFE_OR_UNSUPPORTED`

## Clinical boundary

The engine may organise reviewed information and generate discussion prompts. It must not decide whether a person should start, stop, continue or alter retatrutide or any other medicine.
