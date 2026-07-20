from __future__ import annotations
import argparse,hashlib,json,py_compile,tempfile,zipfile
from pathlib import Path,PurePosixPath
BUILD="0046";RECORD="Documentation/Build_Records/0046";MANIFEST=RECORD+"/ASSET_INTENT_MANIFEST.json";CHECKSUM=RECORD+"/PACKAGE_CONTENT_SHA256.json"
ALLOWED={"00_Governance","01_Knowledge_Systems","02_Peptides","03_Biology","04_Conditions","05_Monitoring","06_Evidence","07_Goals","08_Product_Passports","09_Cost_Intelligence","10_Marketplace","11_Academy","12_Reports","13_Project_Genesis","Assets","Database","Documentation","Images","Schemas","Scripts","Standards","Templates"}
TEXT={".md",".json",".csv",".py",".ps1",".cmd",".bat",".txt",".html",".css",".js",".svg",".yml",".yaml"}
def h(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--package",required=True);p.add_argument("--report",required=True);a=p.parse_args();package=Path(a.package);errors=[]
 if not package.is_file():errors.append("Package not found");names=[];data={}
 else:
  with zipfile.ZipFile(package) as z:names=[n for n in z.namelist() if not n.endswith("/")];data={n:z.read(n) for n in names}
 roots=sorted({PurePosixPath(n).parts[0] for n in names})
 if set(roots)-ALLOWED:errors.append("Unauthorised root")
 if any(PurePosixPath(n).parts[0].startswith("Certiaura_Build_") for n in names):errors.append("Build wrapper folder detected")
 if any(".certiaura_backups" in PurePosixPath(n).parts for n in names):errors.append("Internal backup path packaged")
 if any("__pycache__" in PurePosixPath(n).parts or Path(n).suffix.lower() in {".pyc",".pyo"} for n in names):errors.append("Python runtime artifact packaged")
 try:intent=json.loads(data[MANIFEST].decode("utf-8"))
 except Exception as exc:intent={};errors.append("Asset Intent Manifest invalid: "+str(exc))
 classified=[x.get("path") for x in intent.get("file_classifications",[])]
 if len(classified)!=len(set(classified)):errors.append("Duplicate Asset Intent Manifest classification")
 if set(classified)!=set(names):errors.append("Every package file must be classified exactly once")
 try:checks=json.loads(data[CHECKSUM].decode("utf-8")).get("files",{})
 except Exception as exc:checks={};errors.append("Checksum record invalid: "+str(exc))
 expected=set(names)-{CHECKSUM}
 if set(checks)!=expected:errors.append("Checksum record inventory mismatch")
 for name,digest in checks.items():
  if name in data and h(data[name])!=str(digest).lower():errors.append("Checksum mismatch: "+name)
 for name,blob in data.items():
  suffix=Path(name).suffix.lower()
  if suffix in TEXT:
   if blob.startswith(b"\xef\xbb\xbf"):errors.append("UTF-8 BOM: "+name)
   if b"\r" in blob:errors.append("Non-LF text: "+name)
   if not blob.endswith(b"\n"):errors.append("Final newline missing: "+name)
   for i,line in enumerate(blob.splitlines(),1):
    if line.endswith((b" ",b"\t")):errors.append(f"Trailing whitespace: {name}:{i}")
  if suffix==".ps1" and any(x>127 for x in blob):errors.append("Non-ASCII PowerShell: "+name)
  if suffix==".json":
   try:json.loads(blob.decode("utf-8"))
   except Exception as exc:errors.append(f"Invalid JSON {name}: {exc}")
 with tempfile.TemporaryDirectory() as td:
  root=Path(td)
  for name,blob in data.items():
   if Path(name).suffix.lower()==".py":
    target=root/Path(name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
    try:py_compile.compile(str(target),doraise=True)
    except Exception as exc:errors.append(f"Python compile failed {name}: {exc}")
 result={"valid":not errors,"build_number":BUILD,"package_file_count":len(names),"roots":roots,"ascii_only_powershell":not any("PowerShell" in e for e in errors),"repository_text_hygiene":not any(x in e for e in errors for x in ("BOM","Non-LF","whitespace","newline")),"package_checksums":not any("Checksum" in e for e in errors),"external_backup_only":True,"errors":errors}
 out=Path(a.report);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n");print(json.dumps(result,indent=2));return 0 if result["valid"] else 1
if __name__=="__main__":raise SystemExit(main())
