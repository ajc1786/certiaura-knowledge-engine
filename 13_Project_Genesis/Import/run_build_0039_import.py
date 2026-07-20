from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path, PurePosixPath

def main():
    p=argparse.ArgumentParser(); p.add_argument("zip_path"); p.add_argument("repository_path"); p.add_argument("--apply",action="store_true")
    a=p.parse_args(); importer=Path(__file__).with_name("transactional_build_import.py")
    cmd=[sys.executable,str(importer),a.zip_path,a.repository_path,"--asset-register","Documentation/Master_Asset_Register.csv","--report",f"Documentation/Build_Records/0039/{'GUIDED_IMPORT_REPORT.json' if a.apply else 'GUIDED_DRY_RUN_REPORT.json'}"]
    if a.apply: cmd.append("--apply")
    raise SystemExit(subprocess.call(cmd))
if __name__=="__main__": main()
