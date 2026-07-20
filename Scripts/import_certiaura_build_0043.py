from __future__ import annotations
import argparse, csv, hashlib, json, os, re, shutil, tempfile, zipfile
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
ALLOWED={"00_Governance","01_Knowledge_Systems","02_Peptides","03_Biology","04_Conditions","05_Monitoring","06_Evidence","07_Goals","08_Product_Passports","09_Cost_Intelligence","10_Marketplace","11_Academy","12_Reports","13_Project_Genesis","Assets","Database","Documentation","Images","Schemas","Scripts","Standards","Templates"}
REQ_COLS=["Universal Asset Identifier","Asset Name","Knowledge System","Asset Type","Status","Owner","Parent Assets","Last Review","Notes","Repository Path","Supporting Files","Version","Completion Percentage","Child Assets","Relationship List","Evidence Links","Report Links","Marketplace Links","Next Review","Change History","Build Provenance","Source Builds","Registration Basis","File SHA256","Last Updated"]

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def sha_file(p):
 h=hashlib.sha256();
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
 return h.hexdigest()
def read_rows(p):
 with p.open("r",encoding="utf-8-sig",newline="") as f:
  r=csv.DictReader(f); fields=r.fieldnames or []
  missing=[c for c in REQ_COLS if c not in fields]
  if missing: raise RuntimeError("Master Asset Register missing columns: "+", ".join(missing))
  return fields,list(r)
def next_uai(rows,system):
 nums=[]
 pat=re.compile(rf"^CERT-{re.escape(system)}-(\d{{6}})$")
 for row in rows:
  m=pat.match((row.get("Universal Asset Identifier") or "").strip())
  if m: nums.append(int(m.group(1)))
 return f"CERT-{system}-{(max(nums) if nums else 0)+1:06d}"
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--package",required=True); ap.add_argument("--repository",required=True); ap.add_argument("--report",required=True); ap.add_argument("--backup-root"); ap.add_argument("--apply",action="store_true"); a=ap.parse_args()
 repo=Path(a.repository).resolve(); package=Path(a.package).resolve(); errors=[]; conflicts=[]; allocations=[]; planned=[]; applied=False; backup_path=None
 reg=repo/"Documentation/Master_Asset_Register.csv"
 if not reg.is_file(): errors.append("Canonical Master Asset Register missing: Documentation/Master_Asset_Register.csv")
 if (repo/"Documentation/Master_Asset_Register.csv").resolve()!=reg: errors.append("Ambiguous register path")
 try:
  fields,rows=read_rows(reg) if reg.is_file() else (REQ_COLS,[])
 except Exception as e: errors.append(str(e)); fields,rows=REQ_COLS,[]
 with zipfile.ZipFile(package) as z:
  names=[n for n in z.namelist() if not n.endswith("/")]
  roots={PurePosixPath(n).parts[0] for n in names}
  if roots-ALLOWED: errors.append("Unauthorised root route")
  manifest=json.loads(z.read("Documentation/Build_Records/0043/ASSET_INTENT_MANIFEST.json"))
  incoming_data={n:z.read(n) for n in names}
  path_map={}
  reserved={(r.get("Universal Asset Identifier") or "").strip() for r in rows}
  for asset in manifest["assets"]:
   source=asset["repository_path"]
   target=source
   uai=asset.get("existing_uai")
   if asset["classification"]=="FORMAL_ASSET" and not uai:
    uai=next_uai(rows+[{"Universal Asset Identifier":x} for x in reserved],asset["knowledge_system"])
    while uai in reserved:
     n=int(uai[-6:])+1; uai=f"CERT-{asset['knowledge_system']}-{n:06d}"
    reserved.add(uai); allocations.append({"source_path":source,"uai":uai})
    target=source.replace("__UAI__",uai)
   path_map[source]={"target":target,"uai":uai,"asset":asset}
  for n in names:
   target=path_map.get(n,{}).get("target",n)
   dest=repo/Path(target)
   incoming=incoming_data[n]
   if dest.exists():
    same=hashlib.sha256(dest.read_bytes()).hexdigest()==hashlib.sha256(incoming).hexdigest()
    action=path_map.get(n,{}).get("asset",{}).get("intended_action")
    allow=path_map.get(n,{}).get("asset",{}).get("allow_replace",False)
    if not same and not (action=="UPDATE" and allow): conflicts.append({"path":target,"reason":"NON_IDENTICAL_EXISTING_FILE"})
   planned.append({"source":n,"target":target})
 expected=len(rows)+sum(1 for x in manifest["assets"] if x["classification"]=="FORMAL_ASSET" and not x.get("existing_uai"))
 if a.apply and not errors and not conflicts:
  if not a.backup_root: errors.append("Backup root is required for apply")
  else:
   stamp=datetime.now().strftime("%Y%m%d_%H%M%S"); backup_path=Path(a.backup_root)/f"Build_0043_Pre_Import_{stamp}"; backup_path.mkdir(parents=True,exist_ok=False)
   journal=[]
   try:
    shutil.copy2(reg,backup_path/"Master_Asset_Register.csv")
    for item in planned:
     src=item["source"]; target=item["target"]; dest=repo/Path(target); dest.parent.mkdir(parents=True,exist_ok=True)
     if dest.exists():
      b=backup_path/"files"/Path(target); b.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(dest,b); journal.append(("restore",dest,b))
     else: journal.append(("delete",dest,None))
     data=incoming_data[src]
     info=path_map.get(src)
     if info and info.get("uai"):
      try: data=data.decode("utf-8").replace("UAI_ALLOCATION_REQUIRED",info["uai"]).encode("utf-8")
      except UnicodeDecodeError: pass
     dest.write_bytes(data)
    for src,info in path_map.items():
     asset=info["asset"]
     if asset["classification"]!="FORMAL_ASSET": continue
     uai=info["uai"]
     existing=next((r for r in rows if (r.get("Universal Asset Identifier") or "").strip()==uai),None)
     dest=repo/Path(info["target"])
     row=existing or {c:"" for c in fields}
     row.update({"Universal Asset Identifier":uai,"Asset Name":asset["asset_title"],"Knowledge System":asset["knowledge_system"],"Asset Type":asset["asset_type"],"Status":asset["proposed_status"],"Owner":asset["owner"],"Parent Assets":"; ".join(asset.get("parent_assets",[])),"Repository Path":info["target"],"Supporting Files":"; ".join(asset.get("supporting_files",[])),"Version":asset["proposed_version"],"Completion Percentage":str(asset.get("completion_percentage",100)),"Child Assets":"; ".join(asset.get("child_assets",[])),"Relationship List":json.dumps(asset.get("relationships",[]),separators=(",",":")),"Evidence Links":"; ".join(asset.get("evidence_links",[])),"Report Links":"; ".join(asset.get("report_links",[])),"Marketplace Links":"; ".join(asset.get("marketplace_links",[])),"Change History":f"{now()} Build 0043 import","Build Provenance":"CERT-BUILD-0043","Source Builds":"0041; 0042; 0043","Registration Basis":"BUILD_ASSET_INTENT_MANIFEST","File SHA256":sha_file(dest),"Last Updated":now()})
     if not existing: rows.append(row)
    tmp=reg.with_suffix(".csv.tmp")
    with tmp.open("w",encoding="utf-8-sig",newline="") as f:
     wr=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n"); wr.writeheader(); wr.writerows(rows)
    os.replace(tmp,reg); applied=True
   except Exception as e:
    errors.append("Apply failed: "+str(e))
    for action,dest,b in reversed(journal):
     try:
      if action=="restore": dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(b,dest)
      elif action=="delete" and dest.exists(): dest.unlink()
     except Exception as re_: errors.append("Rollback failure: "+str(re_))
    if (backup_path/"Master_Asset_Register.csv").exists(): shutil.copy2(backup_path/"Master_Asset_Register.csv",reg)
 result={"valid":not errors and not conflicts,"build_number":"0043","apply_requested":a.apply,"applied":applied,"transaction_status":"APPLIED_VALIDATED" if applied and not errors else ("DRY_RUN_VALIDATED" if not a.apply and not errors and not conflicts else "BLOCKED"),"package_file_count":len(names),"formal_asset_count":sum(1 for x in manifest["assets"] if x["classification"]=="FORMAL_ASSET"),"assets_to_create":[x for x in allocations],"allocated_identifiers":[x["uai"] for x in allocations],"expected_register_total":expected,"conflicts":conflicts,"errors":errors,"backup_path":str(backup_path) if backup_path else None,"planned_paths":planned}
 Path(a.report).parent.mkdir(parents=True,exist_ok=True); Path(a.report).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8"); print(json.dumps(result,indent=2)); return 0 if result["valid"] else 1
if __name__=="__main__": raise SystemExit(main())
