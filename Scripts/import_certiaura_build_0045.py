from __future__ import annotations
import argparse, csv, hashlib, json, os, re, shutil, zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

BUILD="0045"; PROVENANCE="CERT-BUILD-0045"; MANIFEST="Documentation/Build_Records/0045/ASSET_INTENT_MANIFEST.json"
ALLOWED_ROOTS={"00_Governance","01_Knowledge_Systems","02_Peptides","03_Biology","04_Conditions","05_Monitoring","06_Evidence","07_Goals","08_Product_Passports","09_Cost_Intelligence","10_Marketplace","11_Academy","12_Reports","13_Project_Genesis","Assets","Database","Documentation","Images","Schemas","Scripts","Standards","Templates"}
REQUIRED_COLUMNS=["Universal Asset Identifier","Asset Name","Knowledge System","Asset Type","Status","Owner","Parent Assets","Last Review","Notes","Repository Path","Supporting Files","Version","Completion Percentage","Child Assets","Relationship List","Evidence Links","Report Links","Marketplace Links","Next Review","Change History","Build Provenance","Source Builds","Registration Basis","File SHA256","Last Updated"]

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def hbytes(data): return hashlib.sha256(data).hexdigest()
def hfile(path): return hbytes(path.read_bytes())
def inside(child,parent):
 try: child.resolve().relative_to(parent.resolve()); return True
 except ValueError: return False

def read_register(path):
 with path.open("r",encoding="utf-8-sig",newline="") as f:
  reader=csv.DictReader(f); fields=reader.fieldnames or []; missing=[x for x in REQUIRED_COLUMNS if x not in fields]
  if missing: raise RuntimeError("Master Asset Register missing columns: "+", ".join(missing))
  return fields,list(reader)
def write_register(path,fields,rows):
 temp=path.with_suffix(".csv.tmp")
 with temp.open("w",encoding="utf-8-sig",newline="") as f:
  writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
 os.replace(temp,path)
def next_uai(rows,system,reserved):
 pat=re.compile(rf"^CERT-{re.escape(system)}-(\d{{6}})$"); nums=[]
 for row in rows:
  m=pat.fullmatch((row.get("Universal Asset Identifier") or "").strip())
  if m: nums.append(int(m.group(1)))
 n=max(nums,default=0)+1; candidate=f"CERT-{system}-{n:06d}"
 while candidate in reserved: n+=1; candidate=f"CERT-{system}-{n:06d}"
 return candidate
def validate_register(rows,repository):
 errors=[]; ids={}; paths={}
 for idx,row in enumerate(rows,2):
  u=(row.get("Universal Asset Identifier") or "").strip(); p=(row.get("Repository Path") or "").strip().replace("\\","/")
  if not u: errors.append(f"Blank UAI at row {idx}")
  else: ids[u]=ids.get(u,0)+1
  if p:
   paths[p.lower()]=paths.get(p.lower(),0)+1; status=(row.get("Status") or "").upper()
   if not any(x in status for x in ("RETIRED","SUPERSEDED","ARCHIVED")) and not (repository/Path(p)).is_file(): errors.append("Register path does not resolve: "+p)
 for u,c in ids.items():
  if c>1: errors.append("Duplicate UAI: "+u)
 for p,c in paths.items():
  if c>1: errors.append("Duplicate repository path: "+p)
 return errors

def register_candidates(repository):
 return [p for p in repository.rglob("Master_Asset_Register.csv") if ".git" not in p.parts]

def rollback(repository,backup):
 meta=json.loads((backup/"TRANSACTION_METADATA.json").read_text(encoding="utf-8"))
 for item in reversed(meta["journal"]):
  dest=repository/Path(item["path"])
  if item["action"]=="restore":
   source=backup/"files"/Path(item["path"]); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,dest)
  elif item["action"]=="delete" and dest.exists(): dest.unlink()
 reg=repository/"Documentation/Master_Asset_Register.csv"; shutil.copy2(backup/"Master_Asset_Register.csv",reg)
 return {"valid":True,"build_number":BUILD,"transaction_status":"ROLLED_BACK","backup_path":str(backup)}

def main():
 p=argparse.ArgumentParser(); p.add_argument("--package"); p.add_argument("--repository",required=True); p.add_argument("--report",required=True); p.add_argument("--backup-root"); p.add_argument("--apply",action="store_true"); p.add_argument("--rollback")
 a=p.parse_args(); repo=Path(a.repository).resolve(); report=Path(a.report).resolve()
 if a.rollback:
  result=rollback(repo,Path(a.rollback).resolve()); report.parent.mkdir(parents=True,exist_ok=True); report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n"); print(json.dumps(result,indent=2)); return 0
 package=Path(a.package).resolve() if a.package else Path(); register=repo/"Documentation/Master_Asset_Register.csv"; errors=[]; conflicts=[]; allocations=[]; routing=[]; backup=None; applied=False
 if not package.is_file(): errors.append("Package not found")
 if not repo.is_dir(): errors.append("Repository not found")
 if (repo/".certiaura_backups").exists() and any((repo/".certiaura_backups").rglob("*")): errors.append("Internal repository backup directory is prohibited; move backups outside the repository")
 candidates=register_candidates(repo) if repo.is_dir() else []
 if not register.is_file() or candidates != [register]: errors.append("Canonical Master Asset Register is missing or ambiguous")
 try: fields,rows=read_register(register) if register.is_file() else (REQUIRED_COLUMNS,[])
 except Exception as exc: errors.append(str(exc)); fields,rows=REQUIRED_COLUMNS,[]
 incoming={}; intent={"assets":[],"file_classifications":[]}; names=[]; path_map={}
 if not errors:
  with zipfile.ZipFile(package) as z:
   names=[n for n in z.namelist() if not n.endswith("/")]; roots={PurePosixPath(n).parts[0] for n in names}
   if roots-ALLOWED_ROOTS: errors.append("Unauthorised package root route")
   incoming={n:z.read(n) for n in names}; intent=json.loads(incoming[MANIFEST].decode("utf-8"))
  classified={x["path"] for x in intent.get("file_classifications",[])}
  if classified != set(names): errors.append("Asset Intent Manifest file classifications do not match package inventory")
  reserved={(r.get("Universal Asset Identifier") or "").strip() for r in rows if (r.get("Universal Asset Identifier") or "").strip()}
  for asset in intent.get("assets",[]):
   source=asset["repository_path"]; target=source; uai=asset.get("existing_uai")
   if asset["classification"]=="FORMAL_ASSET" and not uai:
    uai=next_uai(rows,asset["knowledge_system"],reserved); reserved.add(uai); target=source.replace("__UAI__",uai); allocations.append({"source_path":source,"target_path":target,"uai":uai})
   path_map[source]={"target":target,"uai":uai,"asset":asset}
  for name in names:
   target=path_map.get(name,{}).get("target",name); dest=repo/Path(target); ih=hbytes(incoming[name]); eh=hfile(dest) if dest.is_file() else None; asset=path_map.get(name,{}).get("asset",{})
   routing.append({"source":name,"target":target,"destination_state":"ABSENT" if eh is None else ("IDENTICAL" if eh==ih else "NON_IDENTICAL")})
   if eh is not None and eh!=ih and not (asset.get("intended_action")=="UPDATE" and asset.get("allow_replace") is True): conflicts.append({"path":target,"reason":"NON_IDENTICAL_EXISTING_FILE","resolution":"BLOCKED"})
 expected=len(rows)+len(allocations)
 if a.apply and not errors and not conflicts:
  if not a.backup_root: errors.append("External backup root is required")
  else:
   br=Path(a.backup_root).resolve()
   if inside(br,repo): errors.append("Backup root must be outside canonical repository")
   else:
    backup=br/("Build_0045_Pre_Import_"+datetime.now().strftime("%Y%m%d_%H%M%S")); journal=[]; original=register.read_bytes()
    try:
     backup.mkdir(parents=True,exist_ok=False); shutil.copy2(register,backup/"Master_Asset_Register.csv")
     for item in routing:
      source=item["source"]; target=item["target"]; dest=repo/Path(target); dest.parent.mkdir(parents=True,exist_ok=True)
      if dest.exists():
       bf=backup/"files"/Path(target); bf.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(dest,bf); journal.append({"action":"restore","path":target})
      else: journal.append({"action":"delete","path":target})
      data=incoming[source]; alloc=next((x for x in allocations if x["source_path"]==source),None)
      if alloc and dest.suffix.lower() in {".md",".json",".txt",".csv",".py",".ps1",".html",".css",".js"}:
       text=data.decode("utf-8").replace("UAI_ALLOCATION_REQUIRED",alloc["uai"]); data=text.encode("utf-8")
      dest.write_bytes(data)
     for alloc in allocations:
      asset=path_map[alloc["source_path"]]["asset"]; target=alloc["target_path"]; dest=repo/Path(target)
      row={c:"" for c in fields}; row.update({"Universal Asset Identifier":alloc["uai"],"Asset Name":asset["asset_title"],"Knowledge System":asset["knowledge_system"],"Asset Type":asset["asset_type"],"Status":asset["proposed_status"],"Owner":asset["owner"],"Parent Assets":"; ".join(asset.get("parent_assets",[])),"Notes":"Created by Certiaura Build 0045.","Repository Path":target,"Supporting Files":"; ".join(asset.get("supporting_files",[])),"Version":asset["proposed_version"],"Completion Percentage":str(asset.get("completion_percentage",0)),"Child Assets":"; ".join(asset.get("child_assets",[])),"Relationship List":json.dumps(asset.get("relationships",[]),separators=(",",":")),"Evidence Links":"; ".join(asset.get("evidence_links",[])),"Report Links":"; ".join(asset.get("report_links",[])),"Marketplace Links":"; ".join(asset.get("marketplace_links",[])),"Change History":"Created by Build 0045","Build Provenance":PROVENANCE,"Source Builds":"0045","Registration Basis":"Asset Intent Manifest transactional import","File SHA256":hfile(dest),"Last Updated":now()}); rows.append(row)
     write_register(register,fields,rows); reg_errors=validate_register(rows,repo)
     if reg_errors: raise RuntimeError("; ".join(reg_errors))
     meta={"build_number":BUILD,"created_utc":now(),"package":str(package),"repository":str(repo),"register_rows_before":len(rows)-len(allocations),"register_rows_after":len(rows),"journal":journal}; (backup/"TRANSACTION_METADATA.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8",newline="\n"); applied=True
    except Exception as exc:
     errors.append("Apply failed and rolled back: "+str(exc)); register.write_bytes(original)
     for item in reversed(journal):
      dest=repo/Path(item["path"])
      if item["action"]=="restore": shutil.copy2(backup/"files"/Path(item["path"]),dest)
      elif dest.exists(): dest.unlink()
 status="APPLIED_VALIDATED" if applied and not errors else ("DRY_RUN_VALIDATED" if not a.apply and not errors and not conflicts else ("APPLY_ROLLED_BACK" if a.apply else "DRY_RUN_BLOCKED"))
 result={"valid":not errors and not conflicts,"build_number":BUILD,"mode":"APPLY" if a.apply else "DRY_RUN","transaction_status":status,"applied":applied,"canonical_register":"Documentation/Master_Asset_Register.csv","register_rows_before":len(rows)-len(allocations) if applied else len(rows),"expected_register_rows_after":expected,"allocations":allocations,"routing":routing,"conflicts":conflicts,"errors":errors,"backup_path":str(backup) if backup else None}
 report.parent.mkdir(parents=True,exist_ok=True); report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n"); print(json.dumps(result,indent=2)); return 0 if result["valid"] else 1
if __name__=="__main__": raise SystemExit(main())
