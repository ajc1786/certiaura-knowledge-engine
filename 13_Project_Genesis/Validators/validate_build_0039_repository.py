from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path, PurePosixPath
REQUIRED=["Documentation/Build_Records/0039/ASSET_INTENT_MANIFEST.json","Documentation/Build_Records/0039/BUILD_MANIFEST.json","13_Project_Genesis/Import/transactional_build_import.py","13_Project_Genesis/Import/recover_failed_build_import.py"]
def main():
    p=argparse.ArgumentParser(); p.add_argument("repository"); a=p.parse_args(); repo=Path(a.repository); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).is_file(): errors.append(f"Missing {rel}")
    reg=repo/"Documentation/Master_Asset_Register.csv"
    if reg.exists():
        with reg.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
        u=[r.get("Universal Asset Identifier","") for r in rows if r.get("Universal Asset Identifier","")]
        if len(u)!=len(set(u)): errors.append("Duplicate UAI in Master Asset Register")
    else: errors.append("Master Asset Register missing")
    result={"valid":not errors,"errors":errors}; print(json.dumps(result,indent=2)); raise SystemExit(0 if not errors else 1)
if __name__=="__main__": main()
