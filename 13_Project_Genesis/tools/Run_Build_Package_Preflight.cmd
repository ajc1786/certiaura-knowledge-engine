@echo off
setlocal
set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..\..
python -B "%REPO_ROOT%\13_Project_Genesis\Release\build_package_preflight.py" %*
exit /b %ERRORLEVEL%
