# Build 0055 Lessons-Learned Review

1. An operational baseline must close through an explicit, evidenced decision rather than by build-number progression alone.
2. Controlled knowledge release is not clinical or regulatory authorisation.
3. Reusable architecture must exclude peptide-specific science by default.
4. A next-peptide pilot requires target-specific evidence and safety-boundary work before implementation.
5. Closed baselines need an exception and reopening route for material new evidence or control failure.
6. The exact successful GitHub Actions run ID remains mandatory closure evidence.
7. Current-build tests must resolve their records from the exact Asset Intent Manifest rather than globbing shared repository directories.
8. Historical build closure claims require a repository-wide Actions-evidence audit rather than inference from recent builds.
9. Retrospectively recovered run IDs must be labelled as backfilled unless Git history proves contemporaneous capture before the next build.
10. Build 0055 must remain fail-closed until Builds 0001 through 0054 each have either a verified run ID or an explicit controlled exception, with zero unresolved records.
