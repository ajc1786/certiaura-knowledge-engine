from __future__ import annotations
import argparse,csv,hashlib,json,re
from pathlib import Path
BUILD="0046";PROV="CERT-BUILD-0046";REGISTER="Documentation/Master_Asset_Register.csv";INTENT="Documentation/Build_Records/0046/ASSET_INTENT_MANIFEST.json"
DEPS=["Scripts/build_retatrutide_longitudinal_journey.py","Scripts/generate_retatrutide_review_schedule.py","Scripts/generate_retatrutide_clinician_handoff.py","05_Monitoring/Retatrutide/Longitudinal_Journey/CERT-MKS-000196_Retatrutide_Longitudinal_Journey_Tracking_Baseline.md","05_Monitoring/Retatrutide/Review_Scheduling/CERT-MKS-000197_Retatrutide_Review_Scheduling_Baseline.md","12_Reports/Retatrutide/Clinician_Handoff/CERT-RKS-000005_Retatrutide_Clinician_Handoff_Baseline.md"]
TEXT={".md",".json",".csv",".py",".ps1",".cmd",".bat",".txt",".html",".css",".js",".svg",".yml",".yaml"}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(repo):
 p=repo/REGISTER
 if not p.is_file():return []
 with p.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def owned(repo,rr):
 p=repo/INTENT
 if not p.is_file():return []
 intent=json.loads(p.read_text(encoding="utf-8"));result=set()
 for item in intent.get("file_classifications",[]):
  rel=str(item.get("path") or "").replace("\\","/")
  if item.get("classification")!="FORMAL_ASSET" and Path(rel).suffix.lower() in TEXT:result.add(rel)
 for row in rr:
  if (row.get("Build Provenance") or "").strip()==PROV:
   rel=(row.get("Repository Path") or "").strip().replace("\\","/")
   if Path(rel).suffix.lower() in TEXT:result.add(rel)
 return sorted(result)
def hygiene(repo,rel):
 p=repo/Path(rel);errors=[]
 if not p.is_file():return ["Build 0046-owned file missing: "+rel]
 data=p.read_bytes()
 if data.startswith(b"\xef\xbb\xbf"):errors.append("UTF-8 BOM: "+rel)
 if b"\r" in data:errors.append("Non-LF: "+rel)
 if not data.endswith(b"\n"):errors.append("Final newline missing: "+rel)
 for i,line in enumerate(data.splitlines(),1):
  if line.endswith((b" ",b"\t")):errors.append(f"Trailing whitespace: {rel}:{i}")
 if p.suffix.lower()==".ps1" and any(x>127 for x in data):errors.append("Non-ASCII PowerShell: "+rel)
 return errors
def main():
 p=argparse.ArgumentParser();p.add_argument("repository");p.add_argument("--report",required=True);a=p.parse_args();repo=Path(a.repository).resolve();errors=[]
 canonical=repo/REGISTER;candidates=[x for x in repo.rglob("Master_Asset_Register.csv") if ".git" not in x.parts and ".certiaura_backups" not in x.parts]
 if not canonical.is_file() or candidates!=[canonical]:errors.append("Canonical Master Asset Register missing or ambiguous")
 if (repo/".certiaura_backups").exists() and any((repo/".certiaura_backups").rglob("*")):errors.append("Internal repository backup directory prohibited")
 for rel in DEPS:
  if not (repo/rel).is_file():errors.append("Missing dependency: "+rel)
 rr=rows(repo);owned_paths=owned(repo,rr)
 for rel in owned_paths:errors.extend(hygiene(repo,rel))
 ids={};paths={};build_rows=[]
 for row in rr:
  u=(row.get("Universal Asset Identifier") or "").strip();rel=(row.get("Repository Path") or "").strip().replace("\\","/")
  if u:ids[u]=ids.get(u,0)+1
  if rel:paths[rel.lower()]=paths.get(rel.lower(),0)+1
  if (row.get("Build Provenance") or "").strip()==PROV:build_rows.append(row)
 for u,c in ids.items():
  if c>1:errors.append("Duplicate UAI: "+u)
 for rel,c in paths.items():
  if c>1:errors.append("Duplicate path: "+rel)
 if len(build_rows)!=3:errors.append(f"Expected 3 Build 0046 formal assets; found {len(build_rows)}")
 for row in build_rows:
  rel=(row.get("Repository Path") or "").replace("\\","/");path=repo/Path(rel)
  if not path.is_file():errors.append("Registered asset missing: "+rel);continue
  if (row.get("File SHA256") or "").lower()!=sha(path):errors.append("Asset hash mismatch: "+rel)
  match=re.search(r"CERT-[A-Z]{3}-\d{6}",path.name)
  if not match or match.group(0)!=row.get("Universal Asset Identifier"):errors.append("Filename/UAI mismatch: "+rel)
 for path in repo.rglob("*"):
  if not path.is_file():continue
  relative=path.relative_to(repo).as_posix()
  if "__UAI__" in path.name:errors.append("Unresolved UAI filename placeholder: "+relative)
 ui=repo/"13_Project_Genesis/UI/Retatrutide_Outcome_Analytics";ui_text="\n".join(x.read_text(encoding="utf-8") for x in ui.glob("*") if x.suffix.lower() in {".html",".css",".js"}) if ui.is_dir() else ""
 for forbidden in ("innerHTML","outerHTML","document.write","localStorage","sessionStorage","indexedDB","http://","https://"):
  if forbidden in ui_text:errors.append("Forbidden UI construct: "+forbidden)
 result={"valid":not errors,"build_number":BUILD,"dependency_count":len(DEPS),"formal_asset_rows":len(build_rows),"owned_text_file_count":len(owned_paths),"validator_scope":"EXACT_ASSET_INTENT_AND_BUILD_PROVENANCE","external_backup_only":True,"ui_security_baseline":not any("UI" in e for e in errors),"errors":errors}
 out=Path(a.report);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n");print(json.dumps(result,indent=2));return 0 if result["valid"] else 1
if __name__=="__main__":raise SystemExit(main())
