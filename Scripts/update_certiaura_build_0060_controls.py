from __future__ import annotations
import argparse,json
from pathlib import Path
START="<!-- CERTIAURA_BUILD_0060_CHECKPOINT_START -->"; END="<!-- CERTIAURA_BUILD_0060_CHECKPOINT_END -->"
LSTART="<!-- CERTIAURA_BUILD_0060_LESSONS_START -->"; LEND="<!-- CERTIAURA_BUILD_0060_LESSONS_END -->"
def append(path,start,end,block):
 p=Path(path); text=p.read_text(encoding="utf-8") if p.exists() else ""; count=text.count(start)
 if count==0: text=text.rstrip()+"\n\n"+start+"\n"+block.rstrip()+"\n"+end+"\n"
 elif count!=1 or text.count(end)!=1: raise RuntimeError("marker count invalid: "+str(path))
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding="utf-8",newline="\n")
def update(repository):
 repo=Path(repository)
 append(repo/"00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",START,END,"Build 0060 executes the reusable peptide-review operating model against BPC-157 as the governed second-peptide candidate. It establishes target-specific evidence reconstruction, regulatory and sport boundaries, human-evidence gap control, safety-quality uncertainty, review-board transition, independent appeal and repeatable multi-peptide onboarding readiness. Canonical closure requires exact GitHub Actions evidence and founder GREEN.")
 append(repo/"00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md",LSTART,LEND,"Build 0060 lessons: repeatability is demonstrated by rebuilding target-specific evidence and producing a justified hold when evidence is insufficient; no Tesamorelin biological or clinical assumption may transfer; regulatory proposals must remain labelled as proposals; sport prohibition and human-evidence gaps require explicit fail-closed routing; second-peptide onboarding requires exact predecessor UAI lineage, role-separated board review, independent appeal, transactional rollback, non-interactive Git closure and persisted copy-ready Actions evidence.")
 c=repo/"00_Governance/CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json"; data=json.loads(c.read_text(encoding="utf-8")) if c.exists() else {}; data["latest_build"]="0060"; data["build_0060_controls"]=["BPC-157 target-specific evidence reconstruction","FDA proposal labelling","2026 WADA S0 boundary","human-evidence gap hold","safety-quality uncertainty hold","role-separated transition board","independent appeal","no Tesamorelin assumption transfer","repeatable multi-peptide onboarding","copy-ready closure evidence","non-interactive Git guard"]; c.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8",newline="\n")
def main():
 p=argparse.ArgumentParser(); p.add_argument("repository"); a=p.parse_args(); update(a.repository); print("BUILD_0060_CONTROLS_UPDATED"); return 0
if __name__=="__main__": raise SystemExit(main())
