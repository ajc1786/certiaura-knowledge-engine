# Retatrutide Patient-Facing Interface Standard

## Mandatory controls

1. Serve only on a loopback interface unless a later approved security architecture supersedes this baseline.
2. Do not persist patient profiles, conversation bodies or generated reports automatically.
3. Do not load remote JavaScript, analytics, fonts, stylesheets or images.
4. Render untrusted text through safe text APIs or HTML escaping; never inject patient-controlled content through `innerHTML`.
5. Display report state, scope boundary, uncertainty, source provenance and urgent-routing content prominently.
6. Do not expose a control that generates personalised dosing, titration, diagnosis, procurement or treatment-selection instructions.
7. Clear in-memory session data when the user resets the interface or closes the page.
8. Apply no-store cache headers and restrictive browser security headers.
9. Treat this baseline as educational discussion support, not a medical device or clinical decision system.
