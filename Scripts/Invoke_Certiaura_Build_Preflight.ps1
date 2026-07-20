[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PackagePath,

    [string]$ReportPath = "",

    [string]$RepositoryRoot = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = Split-Path -Parent $PSScriptRoot
}

$Preflight = Join-Path $RepositoryRoot `
    "13_Project_Genesis\Release\build_package_preflight.py"

if (-not (Test-Path -LiteralPath $Preflight -PathType Leaf)) {
    throw "Preflight implementation not found: $Preflight"
}

if (-not (Test-Path -LiteralPath $PackagePath -PathType Leaf)) {
    throw "Package not found: $PackagePath"
}

$PythonCommand = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCommand = "python"
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCommand = "py"
}

if ([string]::IsNullOrWhiteSpace($PythonCommand)) {
    throw "Python was not found."
}

$Arguments = @($Preflight, $PackagePath)
if (-not [string]::IsNullOrWhiteSpace($ReportPath)) {
    $Arguments += @("--report", $ReportPath)
}

& $PythonCommand -B @Arguments
if ($LASTEXITCODE -ne 0) {
    throw "Certiaura build-package preflight failed. Release is blocked."
}

Write-Host "Certiaura build-package preflight: PASS" -ForegroundColor Green
