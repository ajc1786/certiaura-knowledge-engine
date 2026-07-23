from __future__ import annotations
import argparse,json
from pathlib import Path
START="<!-- CERTIAURA_BUILD_0059_CHECKPOINT_START -->"; END="<!-- CERTIAURA_BUILD_0059_CHECKPOINT_END -->"
LSTART="<!-- CERTIAURA_BUILD_0059_LESSONS_START -->"; LEND="<!-- CERTIAURA_BUILD_0059_LESSONS_END -->"
def append(path,start,end,block):
 p=Path(path); text=p.read_text(encoding="utf-8") if p.exists() else ""; count=text.count(start)
 if count==0: text=text.rstrip()+"\n\n"+start+"\n"+block.rstrip()+"\n"+end+"\n"
 elif count!=1 or text.count(end)!=1: raise RuntimeError("marker count invalid: "+str(path))
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding="utf-8",newline="\n")
def update(repository):
 repo=Path(repository)
 append(repo/"00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",START,END,"Build 0059 establishes governed Tesamorelin review-board approvals, immutable evidence-pack versions, independent challenge and appeal resolution, suspension recovery, periodic reassessment, reusable peptide-review operating-model transition and copy-ready PowerShell closure evidence. Canonical closure requires exact GitHub Actions evidence and founder GREEN.")
 append(repo/"00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md",LSTART,LEND,"Build 0059 lessons: review approvals require role separation, quorum, conflict disclosure and a version-locked evidence pack; appeals require an independent panel; recovery is fail-closed until every criterion is met; reassessment cannot ignore open challenges or suspension; reusable operating models transfer governance mechanics but never peptide-specific clinical assumptions; every close script must print and persist a complete copy-ready evidence block; the Build 0058 single-backslash report-path correction and non-interactive Git guard remain mandatory.")
 c=repo/"00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json"; data=json.loads(c.read_text(encoding="utf-8")) if c.exists() else {}; data["latest_build"]="0059"; data["build_0059_controls"]=["role-based review board","immutable evidence pack versions","independent challenge and appeal","suspension recovery fail-closed","periodic reassessment","reusable operating model boundary","copy-ready closure evidence output","recoverable closure evidence JSON","non-interactive Git guard","Windows single-backslash normalisation"]; c.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8",newline="\n")
def main():
 p=argparse.ArgumentParser(); p.add_argument("repository"); a=p.parse_args(); update(a.repository); print("BUILD_0059_CONTROLS_UPDATED"); return 0
if __name__=="__main__": raise SystemExit(main())
