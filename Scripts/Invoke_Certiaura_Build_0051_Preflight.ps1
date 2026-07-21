[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Package,
    [Parameter(Mandatory = $true)][string]$Report
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-Python {
    $Command = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $Command) { $Command = Get-Command py -ErrorAction SilentlyContinue }
    if ($null -eq $Command) { throw "Python was not found on PATH." }
    return $Command.Source
}

$TempRoot = Join-Path $env:TEMP ("Certiaura_0051_Preflight_" + [guid]::NewGuid().ToString("N"))
try {
    Expand-Archive -LiteralPath $Package -DestinationPath $TempRoot -Force
    $Python = Resolve-Python
    $PackageVerifier = Join-Path $TempRoot "13_Project_Genesis\Validators\verify_build_0051_package.py"
    $Validator = Join-Path $TempRoot "13_Project_Genesis\Validators\validate_retatrutide_post_closure_surveillance_reopening.py"
    foreach ($Required in @($PackageVerifier, $Validator)) { if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) { throw "Build 0051 validation component is missing: $Required" } }
    $env:PYTHONDONTWRITEBYTECODE = "1"
    & $Python -B $PackageVerifier $Package
    if ($LASTEXITCODE -ne 0) { throw "Build 0051 package checksum and hygiene verification failed." }
    & $Python -B $Validator $TempRoot --report $Report
    if ($LASTEXITCODE -ne 0) { throw "Build 0051 package validation failed." }

    $PowerShellFiles = @(Get-ChildItem -LiteralPath $TempRoot -Recurse -File | Where-Object { $_.Extension -in @(".ps1", ".cmd") })
    foreach ($File in $PowerShellFiles) {
        $Bytes = [System.IO.File]::ReadAllBytes($File.FullName)
        if (@($Bytes | Where-Object { $_ -gt 127 }).Count -gt 0) { throw "Non-ASCII byte in PowerShell or CMD file: $($File.FullName)" }
    }

    $Runtime = @(Get-ChildItem -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -in @("__pycache__", ".pytest_cache", ".mypy_cache") -or $_.Extension -in @(".pyc", ".pyo")
    })
    if ($Runtime.Count -gt 0) { throw "Runtime artefacts detected in package." }

    Write-Host "Build 0051 preflight passed." -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $TempRoot) { Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
