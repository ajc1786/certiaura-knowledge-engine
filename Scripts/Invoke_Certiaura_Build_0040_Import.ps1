[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Package,

    [Parameter(Mandatory = $true)]
    [string]$Repository,

    [switch]$Apply,

    [string]$Report
)

$ErrorActionPreference = "Stop"

$PackagePath = (Resolve-Path -LiteralPath $Package).Path
$RepositoryPath = (Resolve-Path -LiteralPath $Repository).Path
$TempRoot = Join-Path $env:TEMP ("Certiaura_0040_Import_" + [guid]::NewGuid().ToString("N"))

$Python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $Python) {
    $Python = Get-Command py -ErrorAction SilentlyContinue
}
if ($null -eq $Python) {
    throw "Python was not found."
}

try {
    Expand-Archive -LiteralPath $PackagePath -DestinationPath $TempRoot -Force
    $Runner = Join-Path $TempRoot "13_Project_Genesis\Import\run_build_0040_import.py"
    if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) {
        throw "Build 0040 transactional runner is missing from the package."
    }

    $Arguments = @(
        "-B",
        $Runner,
        $PackagePath,
        $RepositoryPath
    )
    if (-not $Report) {
        $ReportName = if ($Apply) {
            "Build_0040_GUIDED_IMPORT_REPORT.json"
        }
        else {
            "Build_0040_GUIDED_DRY_RUN_REPORT.json"
        }
        $Report = Join-Path (Join-Path $env:USERPROFILE "Downloads") $ReportName
    }

    $ReportDirectory = Split-Path -Parent $Report
    if (-not (Test-Path -LiteralPath $ReportDirectory)) {
        New-Item -ItemType Directory -Path $ReportDirectory -Force | Out-Null
    }

    $Arguments += @("--report", $Report)
    if ($Apply) {
        $Arguments += "--apply"
    }

    Write-Host "Report: $Report"

    & $Python.Source @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Build 0040 transactional import failed."
    }
}
finally {
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force
    }
}
