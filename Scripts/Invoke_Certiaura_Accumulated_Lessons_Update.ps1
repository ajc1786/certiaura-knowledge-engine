[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepositoryPath,

    [Parameter(Mandatory = $true)]
    [string]$CurrentBuild,

    [Parameter(Mandatory = $true)]
    [string]$ReportPath,

    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-PythonCommand {
    $PythonCommands = @(Get-Command python -ErrorAction SilentlyContinue)
    if ($PythonCommands.Count -gt 0) {
        return [pscustomobject]@{ Path = [string]$PythonCommands[0].Source; Prefix = @() }
    }
    $LauncherCommands = @(Get-Command py -ErrorAction SilentlyContinue)
    if ($LauncherCommands.Count -gt 0) {
        return [pscustomobject]@{ Path = [string]$LauncherCommands[0].Source; Prefix = @("-3") }
    }
    throw "Python was not found on PATH."
}

if (-not (Test-Path -LiteralPath (Join-Path $RepositoryPath ".git") -PathType Container)) {
    throw "RepositoryPath is not a Git repository: $RepositoryPath"
}

$UpdaterPath = Join-Path $RepositoryPath "Scripts\update_certiaura_accumulated_lessons.py"
if (-not (Test-Path -LiteralPath $UpdaterPath -PathType Leaf)) {
    throw "Accumulated lessons updater is missing: $UpdaterPath"
}

$PythonCommand = Resolve-PythonCommand
$Arguments = @()
$Arguments += @($PythonCommand.Prefix)
$Arguments += @("-B", $UpdaterPath, "--repository", $RepositoryPath, "--current-build", $CurrentBuild, "--report", $ReportPath)
if ($Apply.IsPresent) {
    $Arguments += "--apply"
}

& $PythonCommand.Path @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Accumulated lessons update failed with exit code $LASTEXITCODE."
}

$RuntimeArtefacts = @(Get-ChildItem -LiteralPath $RepositoryPath -Recurse -Force -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -eq "__pycache__" -or $_.Extension -in @(".pyc", ".pyo")
})
if ($RuntimeArtefacts.Count -gt 0) {
    throw "Python runtime artefacts were created during accumulated lessons update."
}

Write-Host "ACCUMULATED_LESSONS_UPDATE_VALIDATED" -ForegroundColor Green
