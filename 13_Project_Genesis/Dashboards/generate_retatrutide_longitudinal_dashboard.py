from __future__ import annotations

import argparse
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path

BUILD_PROVENANCE = "CERT-BUILD-0047"
DISCLAIMER = "For authorised clinician or investigator review. Not a diagnosis, prescription or autonomous treatment instruction."


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def trend(observations: list[dict], field: str) -> dict:
    usable = [(o["observed_date"], o[field]) for o in observations if isinstance(o.get(field), (int, float))]
    if len(usable) < 2:
        return {"available": False, "reason": "fewer than two usable observations"}
    first_date, first_value = usable[0]
    last_date, last_value = usable[-1]
    absolute = round(last_value - first_value, 3)
    percent = round((absolute / first_value) * 100, 3) if first_value else None
    return {
        "available": True,
        "first_date": first_date,
        "first_value": first_value,
        "last_date": last_date,
        "last_value": last_value,
        "absolute_change": absolute,
        "percent_change": percent,
        "formula": "(last - first) / first * 100",
    }


def build_export(journey: dict, alerts: list[dict], input_hash: str) -> dict:
    observations = journey["observations"]
    active = [a for a in alerts if a.get("state") not in {"CLOSED", "CLINICIAN_REVIEWED"}]
    resolved = [a for a in alerts if a.get("state") in {"CLOSED", "CLINICIAN_REVIEWED"}]
    uncertainties = []
    if len(observations) < 2:
        uncertainties.append("Insufficient observations for longitudinal trend calculation.")
    if any(not o.get("laboratory") for o in observations):
        uncertainties.append("Laboratory data are incomplete or not supplied for all observations.")
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "1.0.0",
        "build_provenance": BUILD_PROVENANCE,
        "export_id": f"RET-EXPORT-{journey['journey_id'].removeprefix('RET-JOURNEY-')}",
        "journey_id": journey["journey_id"],
        "subject_reference": journey["subject_reference"],
        "status": "DRAFT_FOR_CLINICIAN_REVIEW",
        "generated_at": generated,
        "compound": "retatrutide",
        "investigational_status": {
            "statement": "Investigational status must be verified for the applicable jurisdiction at review time.",
            "source_id": journey["governance"]["investigational_status_source_id"],
            "checked_date": journey["governance"]["status_checked_date"],
        },
        "summary": {
            "date_range": {"first": observations[0]["observed_date"], "last": observations[-1]["observed_date"]},
            "observation_count": len(observations),
            "weight_trend_kg": trend(observations, "weight_kg"),
            "waist_trend_cm": trend(observations, "waist_cm"),
            "latest_observation": observations[-1],
            "resolved_alert_count": len(resolved),
        },
        "active_alerts": active,
        "resolved_alerts": resolved,
        "uncertainties": uncertainties,
        "provenance": {
            "input_sha256": input_hash,
            "generator": "13_Project_Genesis/Dashboards/generate_retatrutide_longitudinal_dashboard.py",
            "generator_version": "1.0.0",
            "build_provenance": BUILD_PROVENANCE,
        },
        "disclaimer": DISCLAIMER,
    }


def render_markdown(export: dict) -> str:
    wt = export["summary"]["weight_trend_kg"]
    lines = [
        "# Retatrutide Clinician Review Export",
        "",
        f"- Export state: `{export['status']}`",
        f"- Journey: `{export['journey_id']}`",
        f"- Subject reference: `{export['subject_reference']}`",
        f"- Generated: `{export['generated_at']}`",
        "",
        "## Investigational status",
        "",
        export["investigational_status"]["statement"],
        f"Source: `{export['investigational_status']['source_id']}`; checked `{export['investigational_status']['checked_date']}`.",
        "",
        "## Longitudinal summary",
        "",
        f"Observations: {export['summary']['observation_count']}",
    ]
    if wt.get("available"):
        lines += [f"Weight: {wt['first_value']} kg on {wt['first_date']} to {wt['last_value']} kg on {wt['last_date']} ({wt['absolute_change']} kg; {wt['percent_change']}%)."]
    else:
        lines += [f"Weight trend unavailable: {wt.get('reason')}."]
    lines += ["", "## Active alerts", ""]
    if export["active_alerts"]:
        for alert in export["active_alerts"]:
            lines.append(f"- `{alert['alert_id']}`: {alert['severity']} / {alert['state']} - {alert['trigger']['summary']}")
    else:
        lines.append("No active alerts were supplied to this export. This does not establish clinical safety.")
    lines += ["", "## Uncertainty", ""]
    if export["uncertainties"]:
        lines.extend(f"- {item}" for item in export["uncertainties"])
    else:
        lines.append("No structural uncertainty was generated; clinical uncertainty still requires human review.")
    lines += ["", "## Disclaimer", "", export["disclaimer"], ""]
    return "\n".join(lines)


def render_html(export: dict) -> str:
    wt = export["summary"]["weight_trend_kg"]
    weight_text = html.escape(str(wt))
    alert_rows = "".join(
        f"<tr><td>{html.escape(a['alert_id'])}</td><td>{html.escape(a['severity'])}</td><td>{html.escape(a['state'])}</td><td>{html.escape(a['trigger']['summary'])}</td></tr>"
        for a in export["active_alerts"]
    ) or "<tr><td colspan='4'>No active alerts supplied. This does not establish clinical safety.</td></tr>"
    return f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><title>Retatrutide longitudinal dashboard</title>
<style>body{{font-family:Arial,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem}}.banner{{border:2px solid #333;padding:1rem}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #bbb;padding:.5rem;text-align:left}}code{{word-break:break-all}}</style></head>
<body><h1>Retatrutide Controlled Longitudinal Dashboard</h1>
<div class='banner'><strong>{html.escape(export['status'])}</strong><br>{html.escape(export['disclaimer'])}</div>
<h2>Journey</h2><p><code>{html.escape(export['journey_id'])}</code> / <code>{html.escape(export['subject_reference'])}</code></p>
<h2>Investigational status</h2><p>{html.escape(export['investigational_status']['statement'])}</p>
<h2>Weight trend</h2><pre>{weight_text}</pre>
<h2>Active alerts</h2><table><thead><tr><th>ID</th><th>Severity</th><th>State</th><th>Trigger</th></tr></thead><tbody>{alert_rows}</tbody></table>
<h2>Uncertainty</h2><ul>{''.join(f'<li>{html.escape(u)}</li>' for u in export['uncertainties']) or '<li>Clinical interpretation remains a human responsibility.</li>'}</ul>
<h2>Provenance</h2><p>Input SHA-256: <code>{html.escape(export['provenance']['input_sha256'])}</code></p>
</body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("journey", type=Path)
    parser.add_argument("--alert", action="append", default=[], type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    journey = json.loads(args.journey.read_text(encoding="utf-8"))
    alerts = [json.loads(path.read_text(encoding="utf-8")) for path in args.alert]
    export = build_export(journey, alerts, sha256(args.journey))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "retatrutide_clinician_export.json").write_text(json.dumps(export, indent=2) + "\n", encoding="utf-8", newline="\n")
    (args.output_dir / "retatrutide_clinician_export.md").write_text(render_markdown(export), encoding="utf-8", newline="\n")
    (args.output_dir / "retatrutide_dashboard.html").write_text(render_html(export), encoding="utf-8", newline="\n")
    print(json.dumps({"valid": True, "output_dir": str(args.output_dir), "export_id": export["export_id"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
