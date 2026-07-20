from __future__ import annotations
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path

REQUIRED=[
"Standards/RETATRUTIDE_PATIENT_JOURNEY_REPORT_STANDARD.md","Standards/RETATRUTIDE_AI_QUERY_INTEGRATION_STANDARD.md",
"Schemas/retatrutide_patient_profile.schema.json","Schemas/retatrutide_patient_journey_report.schema.json","Schemas/retatrutide_ai_query.schema.json","Schemas/retatrutide_ai_response.schema.json",
"Scripts/generate_retatrutide_patient_journey_report.py","Scripts/query_retatrutide_knowledge.py",
"13_Project_Genesis/AI/retatrutide_ai_query_policy.json","Documentation/Build_Records/0043/ASSET_INTENT_MANIFEST.json"
]

def fail(msg): print("FAIL: "+msg,file=sys.stderr); return 1

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("repository"); ap.add_argument("--report"); a=ap.parse_args(); root=Path(a.repository)
 errors=[]
 for rel in REQUIRED:
  if not (root/rel).is_file(): errors.append("Missing "+rel)
 for p in root.rglob("*.json"):
  if "0043" in str(p) or p.name.startswith("retatrutide_") or "Retatrutide" in str(p):
   try: json.loads(p.read_text(encoding="utf-8"))
   except Exception as e: errors.append(f"Invalid JSON {p}: {e}")
 for p in (root/"Scripts").glob("*.ps1"):
  if any(b>127 for b in p.read_bytes()): errors.append(f"Non-ASCII byte in Windows PowerShell 5.1 script: {p.name}")
 for p in [root/"Standards/RETATRUTIDE_PATIENT_JOURNEY_REPORT_STANDARD.md",root/"Standards/RETATRUTIDE_AI_QUERY_INTEGRATION_STANDARD.md"]:
  if p.exists():
   t=p.read_text(encoding="utf-8").lower()
   for phrase in ["diagnosis","dosing","source","abstention"]:
    if phrase not in t: errors.append(f"Required control phrase '{phrase}' missing from {p.name}")
 if errors:
  result={"valid":False,"errors":errors}
 else:
  result={"valid":True,"errors":[],"checks":{"required_files":"PASS","json_parse":"PASS","safety_boundaries":"PASS"}}
 if a.report: Path(a.report).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,indent=2)); return 0 if result["valid"] else 1
if __name__=="__main__": raise SystemExit(main())
