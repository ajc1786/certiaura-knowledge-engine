from __future__ import annotations
import argparse, csv, json
from pathlib import Path
REGISTERS={
"changes":"Retatrutide_Knowledge_Change_Register.csv","impacts":"Retatrutide_Cross_Asset_Impact_Register.csv","implementations":"Retatrutide_Change_Implementation_Register.csv","publications":"Retatrutide_Publication_Release_Register.csv","effectiveness":"Retatrutide_Post_Change_Effectiveness_Register.csv","reopenings":"Retatrutide_Change_Reopening_Register.csv"}
def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("repository"); p.add_argument("--output",required=True); a=p.parse_args(); root=Path(a.repository)/"Database/Registers"; summary={"build_number":"0053","counts":{},"attention":[]}
 for key,name in REGISTERS.items():
  path=root/name; rows=list(csv.DictReader(path.open("r",encoding="utf-8-sig",newline=""))) if path.exists() else []; summary["counts"][key]=len(rows)
  for row in rows:
   state=" ".join(str(v) for v in row.values()).upper()
   if any(token in state for token in ["QUARANTINED","INCOMPLETE","INEFFECTIVE","REOPEN","FAILED"]): summary["attention"].append({"register":name,"record":row})
 Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8",newline="\n"); print(json.dumps(summary,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
