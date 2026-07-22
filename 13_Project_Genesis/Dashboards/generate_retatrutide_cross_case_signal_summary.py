from __future__ import annotations
import argparse, csv, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("register"); p.add_argument("output")
    a=p.parse_args(); rows=list(csv.DictReader(Path(a.register).open(encoding="utf-8")))
    counts={}
    for row in rows: counts[row.get("Classification","")]=counts.get(row.get("Classification",""),0)+1
    Path(a.output).write_text(json.dumps({"signal_count":len(rows),"classification_counts":counts},indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
