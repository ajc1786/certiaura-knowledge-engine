# Retatrutide patient-facing interface baseline

This local interface exposes the installed Build 0043 patient-journey report generator and evidence-grounded query engine through a controlled Build 0044 workflow.

## Boundaries

- Loopback binding only.
- No database, analytics, telemetry or browser storage.
- No direct identifiers.
- No personalised diagnosis, suitability decision, prescribing, dose selection or titration.
- Urgent symptom routing locks the current session.
- Source provenance is shown for grounded responses.
- Outputs remain educational discussion support requiring qualified clinical review.

## Launch

From the canonical repository:

```powershell
python -B Scripts\serve_retatrutide_patient_interface.py `
  --repository . `
  --host 127.0.0.1 `
  --port 8765
```

Open `127.0.0.1:8765` in a local browser. Press `Ctrl+C` in the terminal to stop.
