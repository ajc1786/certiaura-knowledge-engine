from __future__ import annotations
import argparse, hashlib, json, os, py_compile, subprocess, sys, tempfile, zipfile
from pathlib import Path

def run(cmd,cwd=None,expect=0):
 r=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if r.returncode!=expect: raise RuntimeError(f"command failed ({r.returncode}, expected {expect}): {' '.join(map(str,cmd))}\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")
 return r

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("package"); p.add_argument("--report",required=True); a=p.parse_args(); package=Path(a.package).resolve(); report=Path(a.report).resolve(); errors=[]; checks={}
 try:
  digest=hashlib.sha256(package.read_bytes()).hexdigest(); checks["zip_sha256"]=digest
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/"payload"
   with zipfile.ZipFile(package) as zf: zf.extractall(root)
   manifest=json.loads((root/"Documentation/Build_Records/0055/ASSET_INTENT_MANIFEST.json").read_text(encoding="utf-8")); names=sorted(str(p.relative_to(root)).replace("\\","/") for p in root.rglob("*") if p.is_file()); declared=sorted(str(x["repository_path"]).replace("\\","/") for x in manifest["files"])
   if names!=declared: errors.append("extracted package paths do not equal Asset Intent Manifest files")
   checks["package_path_count"]=len(names)
   for path in root.rglob("*.json"): json.loads(path.read_text(encoding="utf-8"))
   checks["json_parse"]="PASS"
   for path in root.rglob("*.py"): py_compile.compile(str(path),doraise=True)
   for cache in root.rglob("__pycache__"):
    import shutil; shutil.rmtree(cache)
   checks["python_compile"]="PASS"
   valid=sorted((root/"05_Monitoring/Examples/Retatrutide").glob("valid_*.example.json"))+sorted((root/"05_Monitoring/Examples/Retatrutide").glob("conditional_*.example.json"))
   invalid=sorted((root/"05_Monitoring/Examples/Retatrutide").glob("invalid_*.example.json"))
   validator=root/"13_Project_Genesis/Validators/validate_retatrutide_baseline_closure.py"
   for f in valid: run([sys.executable,"-B",str(validator),str(f)])
   for f in invalid: run([sys.executable,"-B",str(validator),str(f)],expect=1)
   checks["example_contracts"]="PASS"
   tests=run([sys.executable,"-B","-m","unittest","discover","-s","13_Project_Genesis/Tests","-p","test_build_0055_*.py","-v"],cwd=root)
   checks["automated_tests"]="PASS"; checks["test_output"]=tests.stdout[-8000:]
 except Exception as exc: errors.append(str(exc))
 result={"build_number":"0055","candidate":"RC2","valid":not errors,"checks":checks,"errors":errors,"result":"CANDIDATE_RELEASE_VALIDATED" if not errors else "FAIL"}
 report.parent.mkdir(parents=True,exist_ok=True); report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n"); print(json.dumps(result,indent=2)); return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
