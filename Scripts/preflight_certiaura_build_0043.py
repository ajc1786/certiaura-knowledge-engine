from __future__ import annotations
import argparse, hashlib, json, re, sys, zipfile
from pathlib import PurePosixPath, Path
ALLOWED={"00_Governance","01_Knowledge_Systems","02_Peptides","03_Biology","04_Conditions","05_Monitoring","06_Evidence","07_Goals","08_Product_Passports","09_Cost_Intelligence","10_Marketplace","11_Academy","12_Reports","13_Project_Genesis","Assets","Database","Documentation","Images","Schemas","Scripts","Standards","Templates"}

def h(b): return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("package"); ap.add_argument("--report",required=True); a=ap.parse_args(); errors=[]
 with zipfile.ZipFile(a.package) as z:
  names=[n for n in z.namelist() if not n.endswith("/")]
  roots={PurePosixPath(n).parts[0] for n in names}
  bad=sorted(roots-ALLOWED)
  if bad: errors.append("Unauthorised root routes: "+", ".join(bad))
  if len(roots)==1 and next(iter(roots)).lower().startswith("certiaura_build_"): errors.append("Build wrapper folder detected")
  lower={}
  for n in names:
   k=n.lower()
   if k in lower and lower[k]!=n: errors.append(f"Case-only collision: {lower[k]} / {n}")
   lower[k]=n
  required=["Documentation/Build_Records/0043/BUILD_MANIFEST.json","Documentation/Build_Records/0043/ASSET_INTENT_MANIFEST.json","Documentation/Build_Records/0043/PACKAGE_CONTENT_SHA256.json"]
  for r in required:
   if r not in names: errors.append("Missing "+r)
  if not errors:
   intent=json.loads(z.read("Documentation/Build_Records/0043/ASSET_INTENT_MANIFEST.json"))
   classified=[x["path"] for x in intent.get("file_classifications",[])]
   missing_classification=sorted(set(names)-set(classified))
   extra_classification=sorted(set(classified)-set(names))
   if missing_classification: errors.append("Unclassified package files: "+", ".join(missing_classification))
   if extra_classification: errors.append("Classified paths absent from package: "+", ".join(extra_classification))
   if len(classified)!=len(set(classified)): errors.append("Duplicate file classifications detected")
   for n in names:
    if n.lower().endswith(".ps1") and any(b>127 for b in z.read(n)):
     errors.append("Non-ASCII byte detected in Windows PowerShell 5.1 script: "+n)
   checks=json.loads(z.read("Documentation/Build_Records/0043/PACKAGE_CONTENT_SHA256.json"))
   for rec in checks["files"]:
    if rec["path"] not in names: errors.append("Checksum path missing: "+rec["path"]); continue
    if h(z.read(rec["path"]))!=rec["sha256"]: errors.append("Checksum mismatch: "+rec["path"])
 result={"valid":not errors,"build_number":"0043","package_file_count":len(names),"roots":sorted(roots),"errors":errors}
 Path(a.report).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8"); print(json.dumps(result,indent=2)); return 0 if result["valid"] else 1
if __name__=="__main__": raise SystemExit(main())
