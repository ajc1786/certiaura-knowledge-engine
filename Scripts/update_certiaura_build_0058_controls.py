from __future__ import annotations
import argparse,json
from pathlib import Path
START="<!-- CERTIAURA_BUILD_0058_CHECKPOINT_START -->"; END="<!-- CERTIAURA_BUILD_0058_CHECKPOINT_END -->"
LSTART="<!-- CERTIAURA_BUILD_0058_LESSONS_START -->"; LEND="<!-- CERTIAURA_BUILD_0058_LESSONS_END -->"
def append(path,start,end,block):
 p=Path(path); text=p.read_text(encoding="utf-8") if p.exists() else ""; count=text.count(start)
 if count==0: text=text.rstrip()+"\n\n"+start+"\n"+block.rstrip()+"\n"+end+"\n"
 elif count!=1 or text.count(end)!=1: raise RuntimeError("marker count invalid: "+str(path))
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding="utf-8",newline="\n")
def update(repository):
 repo=Path(repository); append(repo/"00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",START,END,"Build 0058 establishes governed Tesamorelin multi-source quality assessment, conflicting-evidence adjudication, longitudinal recurrence review, controlled amendment and pilot continuation or suspension governance. Canonical closure still requires exact GitHub Actions evidence and founder GREEN.")
 append(repo/"00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md",LSTART,LEND,"Build 0058 lessons: aggregate scores must not hide rejected provenance; conflicting evidence must be explicitly adjudicated or held; recurrent signals must route by severity; amendments require validation and rollback; pilot continuation is fail-closed; the non-interactive Git guard remains mandatory; Windows generated-report self-exclusion must normalise each single backslash before owned-path comparison.")
 c=repo/"00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json"; data=json.loads(c.read_text(encoding="utf-8")) if c.exists() else {}; data["latest_build"]="0058"; data["build_0058_controls"]=["source quality scoring","conflict adjudication","signal recurrence routing","controlled amendment","pilot continuation fail-closed","non-interactive Git guard","Windows single-backslash report-path normalisation"]; c.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8",newline="\n")
def main():
 p=argparse.ArgumentParser(); p.add_argument("repository"); a=p.parse_args(); update(a.repository); print("BUILD_0058_CONTROLS_UPDATED"); return 0
if __name__=="__main__": raise SystemExit(main())
