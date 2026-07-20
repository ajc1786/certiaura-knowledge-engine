[CmdletBinding()]param([Parameter(Mandatory=$true)][string]$Package,[Parameter(Mandatory=$true)][string]$Report)
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
$Python=Get-Command python -ErrorAction SilentlyContinue
if($null -eq $Python){$Python=Get-Command py -ErrorAction SilentlyContinue}
if($null -eq $Python){throw "Python was not found on PATH."}
& $Python.Source -B (Join-Path $PSScriptRoot "preflight_certiaura_build_0045.py") --package $Package --report $Report
if($LASTEXITCODE -ne 0){throw "Build 0045 preflight failed."}
