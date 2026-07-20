# Retatrutide Longitudinal Journey Tracking Standard

**Build:** 0045
**Status:** Baseline

A longitudinal journey is a pseudonymised append-only JSON object. Events are ordered by observation time and contain a deterministic event identifier, prior-chain hash, event hash, source references and safety routing state.

Direct identifiers, free-text names, email addresses, telephone numbers and postal addresses are prohibited. Inputs containing direct identifiers must fail closed.

The engine may record measurements, symptoms, monitoring observations, review outcomes and patient questions. It must not generate diagnoses, prescriptions, personalised dosing, treatment selection or procurement advice.
