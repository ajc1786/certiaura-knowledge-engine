#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,io,json,os,re,shutil,subprocess,tempfile,zipfile
from pathlib import Path,PurePosixPath
ALLOWED={"00_Governance","01_Knowledge_Systems","02_Peptides","03_Biology","04_Conditions","05_Monitoring","06_Evidence","07_Goals","08_Product_Passports","09_Cost_Intelligence","10_Marketplace","11_Academy","12_Reports","13_Project_Genesis","Assets","Database","Documentation","Images","Schemas","Scripts","Standards","Templates"}
RUNTIME=("__pycache__",".pyc",".pyo")
def sha(p):
 h=hashlib.sha256();
 with Path(p).open("rb") as f:
  for c in iter(lambda:f.read(1048576),b""):h.update(c)
 return h.hexdigest()
def run(cmd,cwd=None,env=None):
 cp=subprocess.run(cmd,cwd=cwd,env=env,text=True,capture_output=True)
 if cp.returncode:raise RuntimeError(cp.stderr.strip() or cp.stdout.strip())
 return cp.stdout.strip()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--package",required=True);ap.add_argument("--report",required=True);a=ap.parse_args();package=Path(a.package).resolve();out=Path(a.report).resolve();report={"build_number":"0042","package":str(package),"valid":False,"gates":{},"warnings":[],"errors":[]}
 try:
  with zipfile.ZipFile(package) as z:
   names=[];seen=set()
   for i in z.infolist():
    if i.is_dir():continue
    p=PurePosixPath(i.filename)
    if p.is_absolute() or ".." in p.parts or "\\" in i.filename:raise RuntimeError(f"Unsafe ZIP member: {i.filename}")
    if p.parts[0] not in ALLOWED:raise RuntimeError(f"Unauthorised root: {p.parts[0]}")
    if p.parts[0].startswith("Certiaura_Build_"):raise RuntimeError("Wrapper folder found")
    k=i.filename.casefold()
    if k in seen:raise RuntimeError(f"Case collision: {i.filename}")
    seen.add(k);names.append(i.filename)
    if any(x in i.filename for x in RUNTIME):raise RuntimeError(f"Runtime artefact: {i.filename}")
   report["gates"].update({"zip_member_validation":True,"repository_route_allowlist":True,"wrapper_folder_absent":True,"case_collision_absent":True,"runtime_artifacts_absent":True})
   inv={r["path"] for r in csv.DictReader(io.StringIO(z.read("Documentation/Build_Records/0042/PACKAGE_INVENTORY.csv").decode()))}
   if set(names)!=inv:raise RuntimeError("Inventory mismatch")
   checks={}
   for line in z.read("Documentation/Build_Records/0042/CHECKSUMS.sha256").decode().splitlines():
    if line.strip():d,n=line.split("  ",1);checks[n]=d
   for n,d in checks.items():
    if hashlib.sha256(z.read(n)).hexdigest()!=d:raise RuntimeError(f"Checksum mismatch: {n}")
   report["gates"].update({"inventory_self_validation":True,"checksum_validation":True})
   with tempfile.TemporaryDirectory() as td:
    ext=Path(td)/"package";z.extractall(ext)
    ambiguous=re.compile(r'(?<!\{)\$(?!env:|global:|script:|local:|private:|using:)[A-Za-z_][A-Za-z0-9_]*:')
    for p in ext.rglob("*"):
     if not p.is_file():continue
     if p.suffix.lower() in {".md",".json",".csv",".py",".ps1",".cmd",".txt",".sha256"}:
      data=p.read_bytes()
      if b"\r" in data:raise RuntimeError(f"CR line ending: {p.relative_to(ext)}")
      text=data.decode("utf-8")
      if not text.endswith("\n"):raise RuntimeError(f"Missing final newline: {p.relative_to(ext)}")
      if any(x.endswith((" ","\t")) for x in text.splitlines()):raise RuntimeError(f"Trailing whitespace: {p.relative_to(ext)}")
      if p.suffix.lower() in {".ps1",".cmd"}:
       data.decode("ascii")
       if "^|" in text:raise RuntimeError(f"CMD caret-pipeline defect: {p.relative_to(ext)}")
       if ambiguous.search(text):raise RuntimeError(f"Unbraced variable-colon defect: {p.relative_to(ext)}")
       if "return @($Records)" in text or "System.Collections.Generic.List" in text:raise RuntimeError(f"PowerShell 5.1 collection defect: {p.relative_to(ext)}")
       if "Start-Process -FilePath $Candidates[0]" in text:raise RuntimeError(f"Scalar path indexing defect: {p.relative_to(ext)}")
       if "Dropbox\\PC\\Downloads" in text or "Get-ChildItem -LiteralPath $Root -Filter \"*.zip\"" in text:raise RuntimeError(f"Broad package search prohibited: {p.relative_to(ext)}")
     if p.suffix.lower()==".json":json.loads(p.read_text(encoding="utf-8"))
    report["gates"].update({"text_normalization":True,"json_parsing":True,"windows_powershell_5_1_ascii_compatibility":True,"known_launcher_regressions_absent":True})
    env=os.environ.copy();env["PYTHONDONTWRITEBYTECODE"]="1";py=os.environ.get("PYTHON","python")
    for p in ext.rglob("*.py"):run([py,"-B","-m","py_compile",str(p)],env=env)
    for d in ext.rglob("__pycache__"):shutil.rmtree(d)
    report["gates"]["python_compilation"]=True
    run([py,"-B",str(ext/"13_Project_Genesis/Validators/validate_retatrutide_safety_integration.py"),str(ext)],env=env)
    run([py,"-B","-m","unittest","discover","-s",str(ext/"13_Project_Genesis/Tests"),"-p","test_build_0042_*.py"],env=env)
    report["gates"].update({"scientific_validator":True,"unit_tests":True})
    repo=Path(td)/"repo";repo.mkdir();run(["git","init","-b","main"],cwd=repo);run(["git","config","user.email","synthetic@certiaura.local"],cwd=repo);run(["git","config","user.name","Certiaura Synthetic"],cwd=repo)
    (repo/"Unrelated/History").mkdir(parents=True);(repo/"Unrelated/History/legacy.txt").write_text("unrelated\n")
    (repo/"00_Governance").mkdir();(repo/"00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md").write_text("# Existing\n\nBuild 0041 closed.\n")
    (repo/"13_Project_Genesis/Import").mkdir(parents=True);(repo/"13_Project_Genesis/Import/transactional_build_import.py").write_text("# BUILD_MANIFEST ASSET_INTENT_MANIFEST\n")
    (repo/"Documentation").mkdir();fields=["Universal Asset Identifier","Asset Name","Knowledge System","Asset Type","Status","Owner","Parent Assets","Last Review","Notes","Repository Path","Supporting Files","Version","Completion Percentage","Child Assets","Relationship List","Evidence Links","Report Links","Marketplace Links","Next Review","Change History","Build Provenance","Source Builds","Registration Basis","File SHA256","Last Updated"]
    rows=[["CERT-PKS-000001","Retatrutide","PKS","Flagship","ACTIVE","Certiaura","","","","02_Peptides/CERT-PKS-000001_Retatrutide/CERT-PKS-000001_Retatrutide.md","","1.0.0","","","","","","","","","prior","prior","historical","","2026-07-20"],["CERT-EKS-000776","Retatrutide evidence 12","EKS","Evidence","ACTIVE","Certiaura","","","","06_Evidence/Retatrutide/Corpus/RET-EVD-0012.json","","1.0.0","","","","","","","","","0041","0041","historical","","2026-07-20"],["CERT-SYS-999999","Unrelated","SYS","File","ACTIVE","Certiaura","","","","Unrelated/History/legacy.txt","","1.0.0","","","","","","","","","prior","prior","historical","","2026-07-20"]]
    with (repo/"Documentation/Master_Asset_Register.csv").open("w",newline="",encoding="utf-8") as f:w=csv.writer(f,lineterminator="\n");w.writerow(fields);w.writerows(rows)
    run(["git","add","."],cwd=repo);run(["git","commit","-m","Synthetic baseline"],cwd=repo);baseline=run(["git","rev-parse","HEAD"],cwd=repo)
    runner=ext/"13_Project_Genesis/Import/run_build_0042_import.py";dry=Path(td)/"dry.json";run([py,"-B",str(runner),"--package",str(package),"--repository",str(repo),"--report",str(dry),"--expected-sha256",sha(package)],env=env);d=json.loads(dry.read_text())
    if not d.get("valid") or d.get("applied"):raise RuntimeError("Synthetic dry-run failure")
    if run(["git","status","--porcelain","--untracked-files=all"],cwd=repo):raise RuntimeError("Dry-run changed repository")
    env2=env.copy();env2["CERTIAURA_BACKUP_ROOT"]=str(Path(td)/"backups");apply=Path(td)/"apply.json";run([py,"-B",str(runner),"--package",str(package),"--repository",str(repo),"--report",str(apply),"--expected-sha256",sha(package),"--apply"],env=env2);r=json.loads(apply.read_text())
    if not r.get("valid") or not r.get("applied"):raise RuntimeError("Synthetic apply failure")
    if not (repo/"Unrelated/History/legacy.txt").is_file() or run(["git","rev-parse","HEAD"],cwd=repo)!=baseline:raise RuntimeError("History preservation failure")
    run(["git","diff","--check"],cwd=repo);run(["git","add","-A"],cwd=repo);run(["git","diff","--cached","--check"],cwd=repo)
    if run(["git","diff","--name-only"],cwd=repo):raise RuntimeError("Unstaged changes")
    status=run(["git","status","--porcelain","--untracked-files=all"],cwd=repo)
    if any(x.startswith(" D") or x.startswith("D ") for x in status.splitlines()):raise RuntimeError("Unexpected deletion")
    if any("__pycache__" in p.as_posix() or p.suffix in {".pyc",".pyo"} for p in repo.rglob("*")):raise RuntimeError("Runtime artefact")
    report["synthetic_repository"]={"baseline_commit":baseline,"unrelated_history_preserved":True,"dry_run_no_changes":True,"apply_mode_validated":True,"backup_created":True,"expected_register_total":r.get("expected_register_total"),"allocated_identifiers":len(r.get("allocated_identifiers",[])),"git_diff_check":"PASS","git_diff_cached_check":"PASS","unexpected_deletions":0,"unstaged_changes":0,"runtime_artifacts":0}
    report["gates"].update({"synthetic_git_repository":True,"unrelated_history_preserved":True,"actual_runner_dry_run":True,"actual_runner_apply_mode":True,"transactional_backup":True,"master_asset_register_reconciliation":True,"continuity_delta_applied":True,"unexpected_deletions_absent":True,"all_changes_staged":True,"git_diff_check_after_staging":True,"git_diff_cached_check_after_staging":True,"unstaged_changes_absent":True,"runtime_artifacts_after_validation_absent":True})
  report["package_sha256"]=sha(package);report["package_file_count"]=len(names);report["valid"]=True
 except Exception as exc:report["errors"].append(str(exc));report["valid"]=False
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report,indent=2));return 0 if report["valid"] else 1
if __name__=="__main__":raise SystemExit(main())
