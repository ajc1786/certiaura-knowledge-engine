# Retatrutide Review Scheduling Standard

**Build:** 0045
**Status:** Baseline

Review scheduling is administrative decision support. Due dates are generated only from explicit policy intervals and source-event dates. Each item must identify the rule, source event, due date and state.

Urgent indicators create `LOCKED_URGENT_ROUTING` and suppress routine automated scheduling until clinician review is recorded. Missing data generates a `CLINICIAN_DISCUSSION_REQUIRED` prompt rather than a clinical conclusion.
