[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Package,
 [Parameter(Mandatory=$true)][string]$Repository,
 [Parameter(Mandatory=$true)][string]$Report,
 [string]$BackupRoot,
 [switch]$Apply
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue }
if ($null -eq $Python) { throw "Python was not found on PATH." }
$Script = Join-Path $PSScriptRoot "import_certiaura_build_0043.py"
$Arguments = @("-B",$Script,"--package",$Package,"--repository",$Repository,"--report",$Report)
if ($Apply.IsPresent) {
 if ([string]::IsNullOrWhiteSpace($BackupRoot)) { throw "BackupRoot is required in apply mode." }
 $Arguments += @("--backup-root",$BackupRoot,"--apply")
}
& $Python.Source @Arguments
if ($LASTEXITCODE -ne 0) { throw "Build 0043 import operation failed." }
