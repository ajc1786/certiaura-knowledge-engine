from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

RENDERER_VERSION = "1.0.0"
REQUIRED_REPORT_FIELDS = {
    "schema_version", "report_id", "generated_at_utc", "input_sha256",
    "patient_reference", "report_state", "scope_notice", "journey_phase",
    "baseline_summary", "monitoring", "safety", "clinical_outcomes",
    "uncertainty", "clinician_discussion_prompts", "sources"
}

def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def escape(value) -> str:
    return html.escape(str(value), quote=True)

def list_items(values) -> str:
    return "<ul>" + "".join(f"<li>{escape(v)}</li>" for v in values) + "</ul>"

def validate_report(report: dict) -> None:
    missing = sorted(REQUIRED_REPORT_FIELDS - set(report))
    if missing:
        raise ValueError("Report is missing required fields: " + ", ".join(missing))
    if report.get("schema_version") != "1.0.0":
        raise ValueError("Unsupported Build 0043 report schema version")
    if not isinstance(report.get("sources"), list):
        raise ValueError("Report sources must be an array")

def validate_tokens(tokens: dict) -> None:
    required = {"brand_token_version", "wordmark", "strapline", "primary", "secondary", "accent", "surface", "text", "muted", "danger", "font_stack"}
    missing = sorted(required - set(tokens))
    if missing:
        raise ValueError("Brand token file is missing: " + ", ".join(missing))
    for key in ["primary", "secondary", "accent", "surface", "text", "muted", "danger"]:
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(tokens[key])):
            raise ValueError(f"Invalid colour token: {key}")

def render(report: dict, tokens: dict) -> tuple[str, dict]:
    validate_report(report)
    validate_tokens(tokens)
    report_hash = sha256_bytes(canonical_bytes(report))
    token_hash = sha256_bytes(canonical_bytes(tokens))
    render_hash = sha256_bytes((report_hash + token_hash + RENDERER_VERSION).encode("ascii"))
    render_id = "RBR-" + render_hash[:16].upper()
    urgent = report["report_state"] == "URGENT_CLINICAL_ROUTING"
    state_class = "urgent" if urgent else "standard"
    baseline = report.get("baseline_summary", {})
    monitoring = report.get("monitoring", {})
    safety = report.get("safety", {})
    outcomes = report.get("clinical_outcomes", {})
    sources = report.get("sources", [])
    source_rows = []
    for source in sources:
        source_rows.append(
            "<tr>"
            f"<td>{escape(source.get('repository_path', ''))}</td>"
            f"<td>{escape(source.get('uai') or 'Not recorded')}</td>"
            f"<td>{escape(source.get('review_status') or 'Not recorded')}</td>"
            f"<td>{escape(source.get('source_status', ''))}</td>"
            "</tr>"
        )
    monitoring_items = [item.get("repository_path", "Unresolved monitoring source") for item in monitoring.get("items", [])]
    outcome_items = [item.get("repository_path", "Unresolved outcome source") for item in outcomes.get("claims", [])]
    goals = baseline.get("goals", [])
    flags = safety.get("flags", [])
    cautions = safety.get("cautions", [])
    css = f"""
:root{{--primary:{tokens['primary']};--secondary:{tokens['secondary']};--accent:{tokens['accent']};--surface:{tokens['surface']};--text:{tokens['text']};--muted:{tokens['muted']};--danger:{tokens['danger']};}}
*{{box-sizing:border-box}}
html{{background:#dfe5e9}}
body{{margin:0;color:var(--text);font-family:{tokens['font_stack']};font-size:10.2pt;line-height:1.45;background:white}}
.page{{width:210mm;min-height:297mm;margin:0 auto;background:#fff;padding:17mm 17mm 15mm 17mm}}
.brand{{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid var(--primary);padding-bottom:9mm;margin-bottom:9mm}}
.wordmark{{font-size:23pt;font-weight:800;letter-spacing:0.12em;color:var(--primary)}}
.strapline{{font-size:9pt;color:var(--secondary);margin-top:2mm}}
.control{{text-align:right;font-size:8.5pt;color:var(--muted)}}
h1{{font-size:21pt;line-height:1.12;margin:0 0 4mm;color:var(--primary)}}
h2{{font-size:13pt;margin:8mm 0 3mm;color:var(--primary);border-bottom:1px solid #ccd5db;padding-bottom:1.5mm;page-break-after:avoid}}
h3{{font-size:10.5pt;margin:4mm 0 2mm;color:var(--secondary)}}
p{{margin:0 0 2.5mm}} ul{{margin:1.5mm 0 3mm 5mm;padding-left:5mm}} li{{margin-bottom:1.2mm}}
.state{{display:inline-block;padding:2mm 3mm;border-radius:2mm;background:var(--surface);border:1px solid #c7d1d8;font-weight:700;color:var(--primary)}}
.state.urgent{{background:#fff1f1;border-color:var(--danger);color:var(--danger)}}
.notice{{margin:5mm 0;padding:4mm;border-left:4px solid var(--accent);background:#fffaf0}}
.notice.urgent{{border-left-color:var(--danger);background:#fff1f1}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:4mm}}
.card{{border:1px solid #d4dce1;border-radius:2mm;padding:4mm;background:#fff;break-inside:avoid}}
.label{{font-size:8pt;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-bottom:1mm}}
.value{{font-weight:700}}
table{{width:100%;border-collapse:collapse;font-size:8.5pt;table-layout:fixed}}
th,td{{border:1px solid #d4dce1;padding:2mm;vertical-align:top;overflow-wrap:anywhere}}
th{{background:var(--surface);color:var(--primary);text-align:left}}
.footer{{margin-top:10mm;border-top:1px solid #ccd5db;padding-top:3mm;font-size:8pt;color:var(--muted)}}
.hash{{font-family:Consolas,monospace;font-size:7.5pt;overflow-wrap:anywhere}}
@page{{size:A4;margin:0}}
@media print{{html{{background:#fff}}.page{{margin:0;box-shadow:none}}h2{{break-after:avoid}}.card,table{{break-inside:avoid}}}}
"""
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{escape(tokens['wordmark'])} Retatrutide Patient Journey Report</title>
<style>{css}</style>
</head>
<body class="{state_class}">
<main class="page">
<header class="brand">
<div><div class="wordmark">{escape(tokens['wordmark'])}</div><div class="strapline">{escape(tokens['strapline'])}</div></div>
<div class="control"><div>Report ID: {escape(report['report_id'])}</div><div>Render ID: {escape(render_id)}</div><div>Generated: {escape(report['generated_at_utc'])}</div></div>
</header>
<section>
<h1>Retatrutide Patient Journey Report</h1>
<p><span class="state {state_class}">{escape(report['report_state'])}</span></p>
<div class="notice {state_class}">{list_items(report['scope_notice'])}</div>
</section>
<section>
<h2>Report context</h2>
<div class="grid">
<div class="card"><div class="label">Patient reference</div><div class="value">{escape(report['patient_reference'])}</div></div>
<div class="card"><div class="label">Journey phase</div><div class="value">{escape(report['journey_phase'])}</div></div>
<div class="card"><div class="label">Age band</div><div class="value">{escape(baseline.get('age_band','Not recorded'))}</div></div>
<div class="card"><div class="label">Clinical supervision recorded</div><div class="value">{escape(baseline.get('clinical_supervision','Not recorded'))}</div></div>
</div>
<h3>Goals recorded for discussion</h3>{list_items(goals)}
</section>
<section>
<h2>Monitoring and safety</h2>
<div class="card"><div class="label">Monitoring status</div><div class="value">{escape(monitoring.get('status','Not recorded'))}</div>{list_items(monitoring_items)}</div>
<div class="card"><div class="label">Routing</div><div class="value">{escape(safety.get('routing','Not recorded'))}</div><h3>Flags</h3>{list_items(flags or ['None recorded'])}<h3>Cautions</h3>{list_items(cautions or ['No additional caution text recorded'])}</div>
</section>
<section>
<h2>Clinical-outcome evidence context</h2>
<p>Status: <strong>{escape(outcomes.get('status','Not recorded'))}</strong></p>{list_items(outcome_items or ['No source resolved'])}
</section>
<section>
<h2>Uncertainty</h2>{list_items(report['uncertainty'])}
</section>
<section>
<h2>Questions to discuss with a clinician</h2>{list_items(report['clinician_discussion_prompts'])}
</section>
<section>
<h2>Source provenance</h2>
<table><thead><tr><th style="width:46%">Repository path</th><th style="width:18%">UAI</th><th style="width:18%">Review</th><th style="width:18%">Resolution</th></tr></thead><tbody>{''.join(source_rows)}</tbody></table>
</section>
<footer class="footer">
<p>Educational discussion support only. This report does not determine individual suitability, diagnose a condition or provide prescribing or dosing instructions.</p>
<p class="hash">Input SHA-256: {escape(report['input_sha256'])}</p>
<p class="hash">Rendered report SHA-256 basis: {escape(report_hash)}</p>
</footer>
</main>
</body>
</html>
"""
    html_bytes = html_doc.encode("utf-8")
    manifest = {
        "schema_version":"1.0.0","render_id":render_id,"renderer_version":RENDERER_VERSION,
        "brand_token_version":tokens["brand_token_version"],"input_sha256":report_hash,
        "html_sha256":sha256_bytes(html_bytes),"report_id":report["report_id"],
        "report_state":report["report_state"],"source_count":len(sources),
        "remote_dependencies":False,"output_html":""
    }
    return html_doc, manifest

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    parser.add_argument("--brand-tokens", required=True)
    parser.add_argument("--output-html", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    tokens = json.loads(Path(args.brand_tokens).read_text(encoding="utf-8"))
    html_doc, manifest = render(report, tokens)
    output = Path(args.output_html)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_doc, encoding="utf-8", newline="\n")
    manifest["output_html"] = str(output)
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"valid":True,"render_id":manifest["render_id"],"html_sha256":manifest["html_sha256"],"report_state":manifest["report_state"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
