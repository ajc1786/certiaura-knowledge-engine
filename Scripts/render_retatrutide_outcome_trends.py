from __future__ import annotations
import argparse, hashlib, html, json
from pathlib import Path

def canonical(value): return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)

def render(analytics):
    metrics=analytics.get("metrics",[]); width=960; panel_h=150; height=120+panel_h*max(1,len(metrics))
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
           '<title id="title">Retatrutide longitudinal outcome trends</title>',
           '<desc id="desc">Deterministic descriptive trend visualisation for clinician discussion.</desc>',
           '<rect width="100%" height="100%" fill="white"/>',
           '<text x="40" y="44" font-family="Arial" font-size="24">Retatrutide outcome trends</text>',
           f'<text x="40" y="72" font-family="Arial" font-size="13">State: {html.escape(str(analytics.get("analytics_state")))}</text>']
    if not metrics:
        parts.append('<text x="40" y="130" font-family="Arial" font-size="16">Insufficient data for trend rendering.</text>')
    for i,m in enumerate(metrics):
        y=100+i*panel_h; x0=70; x1=890; ymid=y+78
        first=float(m.get("first_value",0)); latest=float(m.get("latest_value",first)); low=min(first,latest); high=max(first,latest); span=max(high-low,1.0)
        y_first=ymid+35-((first-low)/span)*70; y_latest=ymid+35-((latest-low)/span)*70
        label=html.escape(str(m.get("label",m.get("metric")))); unit=html.escape(str(m.get("unit","")))
        parts.extend([
          f'<rect x="40" y="{y}" width="880" height="125" fill="none" stroke="#555"/>',
          f'<text x="55" y="{y+24}" font-family="Arial" font-size="16">{label}</text>',
          f'<line x1="{x0}" y1="{y_first:.2f}" x2="{x1}" y2="{y_latest:.2f}" stroke="#222" stroke-width="3"/>',
          f'<circle cx="{x0}" cy="{y_first:.2f}" r="5" fill="#222"/><circle cx="{x1}" cy="{y_latest:.2f}" r="5" fill="#222"/>',
          f'<text x="{x0}" y="{y+112}" font-family="Arial" font-size="12">{first:g} {unit}</text>',
          f'<text x="{x1-80}" y="{y+112}" font-family="Arial" font-size="12">{latest:g} {unit}</text>',
          f'<text x="410" y="{y+112}" font-family="Arial" font-size="12">{html.escape(str(m.get("direction")))} | {m.get("observation_count",0)} observations</text>'
        ])
    parts.append('</svg>')
    svg='\n'.join(parts)+'\n'
    core={"analytics_id":analytics.get("analytics_id"),"trend_state":analytics.get("analytics_state"),"metric_count":len(metrics),"svg_sha256":hashlib.sha256(svg.encode()).hexdigest(),"safety_boundary":"Descriptive visualisation only; not diagnosis or treatment advice."}
    return {"trend_id":"RTV-"+hashlib.sha256(canonical(core).encode()).hexdigest()[:16].upper(),**core},svg

def main():
    p=argparse.ArgumentParser();p.add_argument("analytics");p.add_argument("--output-json",required=True);p.add_argument("--output-svg",required=True);a=p.parse_args()
    analytics=json.loads(Path(a.analytics).read_text(encoding="utf-8"));manifest,svg=render(analytics)
    Path(a.output_json).parent.mkdir(parents=True,exist_ok=True);Path(a.output_json).write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8",newline="\n");Path(a.output_svg).write_text(svg,encoding="utf-8",newline="\n")
    print(json.dumps({"valid":True,"trend_id":manifest["trend_id"],"trend_state":manifest["trend_state"],"svg_sha256":manifest["svg_sha256"]},indent=2));return 0
if __name__=="__main__": raise SystemExit(main())
