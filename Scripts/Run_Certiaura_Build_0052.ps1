[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackagePath,
    [Parameter(Mandatory = $true)][string]$ExpectedPackageSha256,
    [string]$RepositoryPath = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
    [string]$ReportRootPath = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0052",
    [string]$BackupRootPath = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Backups"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$RegressionPath = Join-Path $PSScriptRoot "Invoke_Certiaura_Build_0052_Windows_PS51_Regression.ps1"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $RegressionPath -PackagePath $PackagePath -ExpectedPackageSha256 $ExpectedPackageSha256 -RepositoryPath $RepositoryPath -ReportRootPath $ReportRootPath -BackupRootPath $BackupRootPath
if ($LASTEXITCODE -ne 0) { throw "Build 0052 RC6 Windows regression failed with exit code $LASTEXITCODE." }
