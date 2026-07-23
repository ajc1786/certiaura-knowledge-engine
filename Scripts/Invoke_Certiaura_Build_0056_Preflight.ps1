[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$PackagePath,[Parameter(Mandatory = $true)][string]$ReportPath)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Python = Get-Command python -ErrorAction SilentlyContinue; $Prefix=@()
if ($null -eq $Python) { $Python=Get-Command py -ErrorAction SilentlyContinue; if ($null -eq $Python) { throw "Python was not found on PATH." }; $Prefix=@("-3") }
$Script=Join-Path $PSScriptRoot "..\13_Project_Genesis\Release\run_build_0056_preflight.py"
& $Python.Source @Prefix -B $Script $PackagePath --report $ReportPath
if ($LASTEXITCODE -ne 0) { throw "Build 0056 preflight failed." }
