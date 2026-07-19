@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO=%%~fI"
echo Certiaura Master Asset Register repair
echo Repository: %REPO%
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 "%SCRIPT_DIR%repair_master_asset_register.py" "%REPO%" --apply --open --report "Documentation\Build_Records\0038\MANUAL_REPAIR_RUN_REPORT.json"
) else (
  python "%SCRIPT_DIR%repair_master_asset_register.py" "%REPO%" --apply --open --report "Documentation\Build_Records\0038\MANUAL_REPAIR_RUN_REPORT.json"
)
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo Repair failed or was rolled back. Review the report in Documentation\Build_Records\0038.
  pause
  exit /b 1
)
echo.
echo Repair completed. The canonical Master Asset Register has been opened.
pause
