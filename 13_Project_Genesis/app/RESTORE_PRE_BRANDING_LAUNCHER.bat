@echo off
setlocal
cd /d "%~dp0"
if not exist "run_genesis.pre_branding_backup.bat" (
 echo No pre-branding launcher backup was found.
 pause
 exit /b 1
)
copy /Y "run_genesis.pre_branding_backup.bat" "run_genesis.bat" >nul
echo Original launcher restored.
pause
