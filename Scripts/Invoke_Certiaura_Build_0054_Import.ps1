[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackagePath,
    [Parameter(Mandatory = $true)][string]$Repository,
    [Parameter(Mandatory = $true)][string]$BackupRoot,
    [Parameter(Mandatory = $true)][string]$ReportPath,
    [switch]$Apply,
    [switch]$ForceFailureAfterApply,
    [string]$RollbackBackup
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Python = Get-Command python -ErrorAction SilentlyContinue
$Prefix = @()
if ($null -eq $Python) {
    $Python = Get-Command py -ErrorAction SilentlyContinue
    if ($null -eq $Python) { throw "Python was not found on PATH." }
    $Prefix = @("-3")
}
$Script = Join-Path $PSScriptRoot "..\13_Project_Genesis\Import\run_build_0054_import.py"
$Arguments = @($Prefix) + @("-B", $Script, "--package", $PackagePath, "--repository", $Repository, "--backup-root", $BackupRoot, "--report", $ReportPath)
if ($Apply) { $Arguments += "--apply" }
if ($ForceFailureAfterApply) { $Arguments += "--force-failure-after-apply" }
if (-not [string]::IsNullOrWhiteSpace($RollbackBackup)) { $Arguments += @("--rollback-backup", $RollbackBackup) }
& $Python.Source @Arguments
if ($LASTEXITCODE -ne 0) { throw "Build 0054 import failed with exit code $LASTEXITCODE." }
