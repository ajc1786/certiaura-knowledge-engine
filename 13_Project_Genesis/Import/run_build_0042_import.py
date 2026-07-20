#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,io,json,os,re,shutil,subprocess,zipfile
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
BUILD="0042";RECORD="Documentation/Build_Records/0042";REGISTER="Documentation/Master_Asset_Register.csv";CONTINUITY="00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md";REQUIRED_IMPORTER="13_Project_Genesis/Import/transactional_build_import.py";BEGIN="<!-- CERTIAURA_ACTIVE_CHECKPOINT_BEGIN -->";END="<!-- CERTIAURA_ACTIVE_CHECKPOINT_END -->"
def sha(p):
 h=hashlib.sha256();
 with Path(p).open("rb") as f:
  for c in iter(lambda:f.read(1048576),b""):h.update(c)
 return h.hexdigest()
def git(repo,*args):
 cp=subprocess.run(["git","-C",str(repo),*args],text=True,capture_output=True)
 if cp.returncode: raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
 return cp.stdout.strip()
def members(z):
 out=[];seen=set()
 for i in z.infolist():
  if i.is_dir():continue
  p=PurePosixPath(i.filename)
  if p.is_absolute() or ".." in p.parts or "\\" in i.filename:raise RuntimeError(f"Unsafe ZIP member: {i.filename}")
  k=i.filename.casefold()
  if k in seen:raise RuntimeError(f"Duplicate or case collision: {i.filename}")
  seen.add(k);out.append(i.filename)
 return sorted(out)
def read_register(p):
 with p.open(encoding="utf-8-sig",newline="") as f:r=csv.DictReader(f);rows=list(r);fields=r.fieldnames or []
 if "Universal Asset Identifier" not in fields or "Repository Path" not in fields:raise RuntimeError("Master Asset Register structure invalid")
 u=[x.get("Universal Asset Identifier","").strip() for x in rows];paths=[x.get("Repository Path","").strip().replace("\\","/").casefold() for x in rows if x.get("Repository Path","").strip()]
 if any(not x for x in u) or len(u)!=len(set(u)):raise RuntimeError("Blank or duplicate UAI")
 if len(paths)!=len(set(paths)):raise RuntimeError("Duplicate canonical register path")
 return fields,rows
def allocate(rows,system,reserved):
 pat=re.compile(rf"^CERT-{re.escape(system)}-(\d+)$");nums=[]
 for row in rows:
  m=pat.match(row.get("Universal Asset Identifier","").strip())
  if m:nums.append(int(m.group(1)))
 n=max(nums or [0])+1
 while f"CERT-{system}-{n:06d}" in reserved:n+=1
 v=f"CERT-{system}-{n:06d}";reserved.add(v);return v
def checkpoint(title):
 return f"""{BEGIN}\n## Active continuation checkpoint - Build 0042\n\n- Last closed build: **0041** at `eb6ef1ad3f5f3e95accd6f1b01d392548e8e9174` (`ACTIONS_GREEN_CLOSED`).\n- Current build: **0042 - {title}**.\n- Current state after import: `IMPORTED` pending validation, commit, push, GitHub Actions and lessons-learned closure.\n- Immediate next action: complete post-import validation and commit using the locked message.\n- Closure gate: do not set `ACTIONS_GREEN_CLOSED` until actual import evidence and lessons-learned controls are verified.\n- Following planned package: Build 0043 - retatrutide patient journey report generation and AI query integration baseline.\n{END}\n"""
def update_checkpoint(text,title):
 block=checkpoint(title);pat=re.compile(re.escape(BEGIN)+r".*?"+re.escape(END)+r"\n?",re.S)
 return (pat.sub(block,text) if pat.search(text) else text.rstrip()+"\n\n"+block).replace("\r\n","\n").replace("\r","\n")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--package",required=True);ap.add_argument("--repository",required=True);ap.add_argument("--report",required=True);ap.add_argument("--expected-sha256");ap.add_argument("--apply",action="store_true");a=ap.parse_args()
 package=Path(a.package).resolve();repo=Path(a.repository).resolve();report_path=Path(a.report).resolve();report={"build_number":BUILD,"apply_requested":a.apply,"applied":False,"valid":False,"errors":[],"warnings":[],"allocated_identifiers":[],"files":[]}
 try:
  if not package.is_file():raise RuntimeError("Package not found")
  actual=sha(package);report["package_sha256"]=actual
  if a.expected_sha256 and actual.lower()!=a.expected_sha256.lower():raise RuntimeError("Package SHA-256 mismatch")
  if not (repo/".git").is_dir():raise RuntimeError("Repository is not Git")
  if git(repo,"status","--porcelain","--untracked-files=all"):raise RuntimeError("Repository is not clean")
  report["repository_head_before"]=git(repo,"rev-parse","HEAD")
  installed=repo/REQUIRED_IMPORTER
  if not installed.is_file():raise RuntimeError("Installed Project Genesis transactional importer missing")
  txt=installed.read_text(encoding="utf-8",errors="replace")
  if "BUILD_MANIFEST" not in txt or "ASSET_INTENT_MANIFEST" not in txt:raise RuntimeError("Installed importer lacks build-neutral metadata markers")
  reg=repo/REGISTER;cont=repo/CONTINUITY
  if not reg.is_file() or not cont.is_file():raise RuntimeError("Canonical register or continuity file missing")
  fields,rows=read_register(reg)
  with zipfile.ZipFile(package) as z:
   names=members(z);manifest=json.loads(z.read(f"{RECORD}/BUILD_MANIFEST.json"));intent=json.loads(z.read(f"{RECORD}/ASSET_INTENT_MANIFEST.json"));inv={r["path"] for r in csv.DictReader(io.StringIO(z.read(f"{RECORD}/PACKAGE_INVENTORY.csv").decode()))}
   if set(names)!=inv:raise RuntimeError("Inventory does not match package")
   if manifest.get("build_number")!=BUILD:raise RuntimeError("Incorrect build number")
   declared={x["path"] for x in intent.get("files",[])}
   if declared!=set(names):raise RuntimeError("Asset Intent Manifest does not classify every file")
   reserved={r["Universal Asset Identifier"].strip() for r in rows};new=[]
   for asset in intent.get("formal_assets",[]):
    if asset.get("intended_action")!="CREATE":continue
    path=asset["repository_relative_path"]
    if any(r.get("Repository Path","").strip().replace("\\","/").casefold()==path.casefold() for r in rows+new):raise RuntimeError(f"Formal asset path already registered: {path}")
    uai=allocate(rows+new,asset["knowledge_system"],reserved);report["allocated_identifiers"].append({"path":path,"allocated_uai":uai})
    row={f:"" for f in fields};vals={"Universal Asset Identifier":uai,"Asset Name":asset["asset_title"],"Knowledge System":asset["knowledge_system"],"Asset Type":asset["asset_type"],"Status":asset.get("proposed_status","ACTIVE"),"Owner":asset.get("owner","Certiaura"),"Parent Assets":"; ".join(asset.get("parent_assets",[])),"Relationship List":json.dumps(asset.get("relationships",[]),separators=(",",":")),"Evidence Links":"; ".join(asset.get("evidence_links",[])),"Repository Path":path,"Version":asset.get("proposed_version","1.0.0"),"Completion Percentage":str(asset.get("completion_percentage",100)),"Build Provenance":"CERT-BUILD-0042","Source Builds":"0042","Registration Basis":"ASSET_INTENT_MANIFEST","File SHA256":hashlib.sha256(z.read(path)).hexdigest(),"Last Updated":"2026-07-20"}
    for k,v in vals.items():
     if k in row:row[k]=v
    new.append(row)
   report.update({"formal_asset_count":len(intent.get("formal_assets",[])),"expected_register_total":len(rows)+len(new),"package_file_count":len(names),"apply_allowed":True})
   if not a.apply:report.update({"valid":True,"transaction_status":"DRY_RUN_VALIDATED"})
   else:
    root=os.environ.get("CERTIAURA_BACKUP_ROOT")
    if not root:raise RuntimeError("CERTIAURA_BACKUP_ROOT required")
    backup=Path(root).resolve()/f"Build_0042_Pre_Import_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}";backup.mkdir(parents=True,exist_ok=False);created=[];backed=[]
    try:
     for rel in [REGISTER,CONTINUITY]:
      src=repo/rel;dst=backup/"files"/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);backed.append(rel)
     for rel in names:
      dst=repo/rel
      if dst.exists():
       b=backup/"files"/rel;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,b);backed.append(rel)
      else:created.append(rel)
     for rel in names:
      dst=repo/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(z.read(rel))
     out=io.StringIO(newline="");w=csv.DictWriter(out,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows+new);reg.write_text(out.getvalue(),encoding="utf-8",newline="\n")
     cont.write_text(update_checkpoint(cont.read_text(encoding="utf-8"),manifest["build_title"]),encoding="utf-8",newline="\n")
     _,check=read_register(reg)
     if len(check)!=len(rows)+len(new):raise RuntimeError("Register total mismatch after apply")
     report.update({"applied":True,"valid":True,"transaction_status":"APPLIED_VALIDATED","backup_path":str(backup),"backed_up_files":backed,"created_files":created})
    except Exception:
     for rel in created:
      p=repo/rel
      if p.is_file():p.unlink()
     for rel in backed:
      src=backup/"files"/rel;dst=repo/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
     report["transaction_status"]="ROLLED_BACK";raise
  report["repository_head_after"]=git(repo,"rev-parse","HEAD")
 except Exception as exc:report["errors"].append(str(exc));report["valid"]=False
 report_path.parent.mkdir(parents=True,exist_ok=True);report_path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8");print(json.dumps(report,indent=2));return 0 if report["valid"] else 1
if __name__=="__main__":raise SystemExit(main())
