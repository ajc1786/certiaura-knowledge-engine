[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Repository,[Parameter(Mandatory=$true)][string]$Package,[Parameter(Mandatory=$true)][ValidatePattern("^[A-Fa-f0-9]{64}$")][string]$PackageSha256,[Parameter(Mandatory=$true)][string]$Report,[string]$BackupRoot,[switch]$Apply)
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $PSScriptRoot
$Python=Get-Command python -ErrorAction SilentlyContinue
if($null -eq $Python){$Python=Get-Command py -ErrorAction SilentlyContinue}
if($null -eq $Python){throw "Python was not found on PATH."}
if($Apply){
 if(-not $BackupRoot){throw "BackupRoot is required for apply mode."}
 $env:CERTIAURA_BACKUP_ROOT=$BackupRoot
 & $Python.Source -B (Join-Path $Root "13_Project_Genesis\Import\run_build_0042_import.py") --package $Package --repository $Repository --report $Report --expected-sha256 $PackageSha256 --apply
}else{
 & $Python.Source -B (Join-Path $Root "13_Project_Genesis\Import\run_build_0042_import.py") --package $Package --repository $Repository --report $Report --expected-sha256 $PackageSha256
}
exit $LASTEXITCODE
