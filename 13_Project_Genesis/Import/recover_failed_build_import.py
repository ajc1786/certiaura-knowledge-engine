from __future__ import annotations
import argparse, json, sys
from pathlib import Path, PurePosixPath
from transactional_build_import import recover_transaction

def main(argv=None):
    p=argparse.ArgumentParser(description="Recover a Certiaura transactional import without recursive directory deletion")
    p.add_argument("journal"); p.add_argument("repository"); p.add_argument("--apply",action="store_true"); p.add_argument("--report")
    a=p.parse_args(argv); journal=json.loads(Path(a.journal).read_text(encoding="utf-8")); result=recover_transaction(Path(a.repository).resolve(),journal,apply=a.apply)
    result.update({"journal":str(Path(a.journal).resolve()),"repository":str(Path(a.repository).resolve()),"safety":{"recursive_directory_deletion_used":False,"remove_only_if_empty":True,"transaction_owned_directories_only":True}})
    if a.report: Path(a.report).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
