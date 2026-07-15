from __future__ import annotations
import json, os, runpy, sys, tkinter as tk
from pathlib import Path
APP_DIR=Path(__file__).resolve().parent
cfg=json.loads((APP_DIR/'brand_runtime_config.json').read_text(encoding='utf-8'))
entry=APP_DIR/cfg['entrypoint']
if not entry.exists():raise SystemExit(f'Project Genesis entry point not found: {entry}')
OriginalTk=tk.Tk
class CertiAuraTk(OriginalTk):
    def __init__(self,*a,**k):
        super().__init__(*a,**k)
        try:
            from certiaura_branding import schedule
            schedule(self)
        except Exception as exc:print(f'CertiAura branding warning: {exc}',file=sys.stderr)
tk.Tk=CertiAuraTk
os.environ['CERTIAURA_BRANDING_ACTIVE']='1'
sys.path.insert(0,str(APP_DIR))
runpy.run_path(str(entry),run_name='__main__')
