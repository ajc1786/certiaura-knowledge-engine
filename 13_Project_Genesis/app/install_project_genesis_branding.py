from __future__ import annotations
import json,re,shutil
from pathlib import Path
APP=Path(__file__).resolve().parent
RUN=APP/'run_genesis.bat'; BACKUP=APP/'run_genesis.pre_branding_backup.bat'; CFG=APP/'brand_runtime_config.json'
BATCH='''@echo off
setlocal
cd /d "%~dp0"
where pythonw >nul 2>nul
if %errorlevel%==0 (
 start "" pythonw "branded_launcher.py"
 exit /b 0
)
python "branded_launcher.py"
exit /b %errorlevel%
'''
def detect(text):
    pats=[re.compile(r'(?i)(?:pythonw?|py)(?:\.exe)?\s+(?:"([^"]+\.py)"|([^\s\r\n]+\.py))')]
    for pat in pats:
        for m in pat.finditer(text):
            cand=(m.group(1) or m.group(2)).replace('%~dp0','').replace('\\','/').strip(); name=Path(cand).name
            if name.lower() not in {'branded_launcher.py','install_project_genesis_branding.py','certiaura_branding.py'} and (APP/name).exists():return name
    for name in ['project_genesis.py','genesis.py','app.py','main.py','project_genesis_app.py']:
        if (APP/name).exists():return name
    candidates=[p for p in APP.glob('*.py') if p.name.lower() not in {'branded_launcher.py','install_project_genesis_branding.py','certiaura_branding.py'}]
    if len(candidates)==1:return candidates[0].name
    raise RuntimeError('Could not identify the Project Genesis Python entry point automatically.')
def main():
    if not RUN.exists():raise FileNotFoundError(RUN)
    text=RUN.read_text(encoding='utf-8',errors='replace')
    if 'branded_launcher.py' in text and CFG.exists():print('Branding already installed.'); return
    entry=detect(text)
    if not BACKUP.exists():shutil.copy2(RUN,BACKUP)
    CFG.write_text(json.dumps({'entrypoint':entry,'installed_by':'Certiaura Build 0014','original_launcher_backup':BACKUP.name},indent=2)+'\n',encoding='utf-8')
    RUN.write_text(BATCH,encoding='utf-8')
    print(f'CertiAura branding installed. Entry point: {entry}')
if __name__=='__main__':main()
