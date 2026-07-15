@echo off
setlocal
cd /d "%~dp0"
python "install_project_genesis_branding.py"
if %errorlevel% neq 0 (
 echo Branding installation did not complete.
 pause
 exit /b %errorlevel%
)
echo Branding installation complete. Reopen Project Genesis using run_genesis.bat.
pause
