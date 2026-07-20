from __future__ import annotations
import argparse, json
from project_genesis_dry_run_core import run_importer

def main():
    p=argparse.ArgumentParser(description="Project Genesis guided Build 0039 dry run assistant"); p.add_argument("zip_path"); p.add_argument("repository_path"); p.add_argument("--apply",action="store_true")
    a=p.parse_args(); code,payload,out,err=run_importer(a.zip_path,a.repository_path,a.apply)
    print(json.dumps({"exit_code":code,"report":payload,"stdout":out,"stderr":err},indent=2)); raise SystemExit(code)
if __name__=="__main__": main()
