@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Run_Certiaura_Build_0048.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if not "%EXIT_CODE%"=="0" echo Build 0048 launcher stopped with exit code %EXIT_CODE%.
pause
exit /b %EXIT_CODE%
