[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Package,[Parameter(Mandatory=$true)][string]$Report)
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot
$Python=Get-Command python -ErrorAction SilentlyContinue
if($null -eq $Python){$Python=Get-Command py -ErrorAction SilentlyContinue}
if($null -eq $Python){throw "Python was not found on PATH."}
& $Python.Source -B (Join-Path $Root "13_Project_Genesis\Release\run_build_0042_preflight.py") --package $Package --report $Report
exit $LASTEXITCODE
