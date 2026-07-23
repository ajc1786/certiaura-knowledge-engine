[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Repository,
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [string]$Owner = "ajc1786",
    [string]$RepositoryName = "certiaura-knowledge-engine",
    [int]$StartBuild = 1,
    [int]$EndBuild = 54
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-PythonCommand {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $Python) {
        return [pscustomobject]@{ Path = $Python.Source; Prefix = @() }
    }
    $Launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $Launcher) {
        return [pscustomobject]@{ Path = $Launcher.Source; Prefix = @("-3") }
    }
    throw "Python was not found on PATH."
}

if (-not (Test-Path -LiteralPath $Repository -PathType Container)) {
    throw "Repository not found: $Repository"
}
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$Python = Resolve-PythonCommand
$Script = Join-Path $PSScriptRoot "..\13_Project_Genesis\Release\audit_historical_github_actions_evidence.py"
$Arguments = @($Python.Prefix) + @(
    "-B",
    $Script,
    $Repository,
    "--owner",
    $Owner,
    "--repository-name",
    $RepositoryName,
    "--output-directory",
    $OutputDirectory,
    "--start-build",
    [string]$StartBuild,
    "--end-build",
    [string]$EndBuild
)
& $Python.Path @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Historical GitHub Actions audit failed with exit code $LASTEXITCODE."
}
$SummaryPath = Join-Path $OutputDirectory "HISTORICAL_GITHUB_ACTIONS_AUDIT_SUMMARY.json"
$Summary = Get-Content -LiteralPath $SummaryPath -Raw | ConvertFrom-Json
if ([string]$Summary.result -ne "HISTORICAL_ACTIONS_AUDIT_COMPLETE") {
    throw "Historical GitHub Actions audit did not complete."
}
if (-not [bool]$Summary.all_builds_accounted) {
    throw "Historical GitHub Actions audit left unaccounted builds."
}
Write-Host ""
Write-Host "BUILD_0055_HISTORICAL_ACTIONS_AUDIT_COMPLETE" -ForegroundColor Green
Write-Host "Accounted builds:"
Write-Host $Summary.accounted_count
Write-Host "Verified run IDs:"
Write-Host $Summary.verified_run_id_count
Write-Host "Exceptions:"
Write-Host $Summary.exception_count
Write-Host "All exact run IDs captured:"
Write-Host $Summary.all_exact_run_ids_captured
Write-Host "Audit directory:"
Write-Host $OutputDirectory
