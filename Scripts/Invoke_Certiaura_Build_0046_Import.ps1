[CmdletBinding()]param([string]$Package,[Parameter(Mandatory=$true)][string]$Repository,[Parameter(Mandatory=$true)][string]$Report,[string]$BackupRoot,[switch]$Apply,[string]$Rollback)
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
$Python=Get-Command python -ErrorAction SilentlyContinue
if($null -eq $Python){$Python=Get-Command py -ErrorAction SilentlyContinue}
if($null -eq $Python){throw "Python was not found on PATH."}
$Args=@((Join-Path $PSScriptRoot "import_certiaura_build_0046.py"),"--repository",$Repository,"--report",$Report)
if($Rollback){$Args+=@("--rollback",$Rollback)}else{$Args+=@("--package",$Package);if($BackupRoot){$Args+=@("--backup-root",$BackupRoot)};if($Apply){$Args+="--apply"}}
& $Python.Source -B @Args
if($LASTEXITCODE -ne 0){throw "Build 0046 import control failed."}
