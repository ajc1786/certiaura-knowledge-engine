from __future__ import annotations
import json, subprocess, sys
from pathlib import Path, PurePosixPath

def run_importer(zip_path, repository_path, apply=False):
    importer=Path(__file__).parents[1]/"Import"/"transactional_build_import.py"
    report=Path(repository_path)/"Documentation"/"Build_Records"/"0039"/("GUIDED_IMPORT_REPORT.json" if apply else "GUIDED_DRY_RUN_REPORT.json")
    cmd=[sys.executable,str(importer),str(zip_path),str(repository_path),"--asset-register","Documentation/Master_Asset_Register.csv","--report",str(report)]
    if apply: cmd.append("--apply")
    completed=subprocess.run(cmd,text=True,capture_output=True)
    payload=json.loads(report.read_text(encoding="utf-8")) if report.exists() else {"valid":False,"errors":[{"code":"REPORT_MISSING"}]}
    return completed.returncode,payload,completed.stdout,completed.stderr
