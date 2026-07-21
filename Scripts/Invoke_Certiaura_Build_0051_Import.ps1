[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Repository,
    [Parameter(Mandatory = $true)][string]$Package,
    [Parameter(Mandatory = $true)][string]$Report,
    [string]$BackupRoot,
    [switch]$Apply
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-Python {
    $Command = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $Command) { $Command = Get-Command py -ErrorAction SilentlyContinue }
    if ($null -eq $Command) { throw "Python was not found on PATH." }
    return $Command.Source
}

$TempRoot = Join-Path $env:TEMP ("Certiaura_0051_Import_" + [guid]::NewGuid().ToString("N"))
try {
    Expand-Archive -LiteralPath $Package -DestinationPath $TempRoot -Force
    $Importer = Join-Path $TempRoot "13_Project_Genesis\Import\build_0051_transactional_import.py"
    if (-not (Test-Path -LiteralPath $Importer -PathType Leaf)) { throw "Build 0051 importer is missing." }
    $Python = Resolve-Python
    $Arguments = @("-B", $Importer, "--repository", $Repository, "--package", $Package, "--report", $Report)
    if ($Apply) {
        if (-not $BackupRoot) { throw "BackupRoot is mandatory in apply mode." }
        $Arguments += @("--backup-root", $BackupRoot, "--apply")
    }
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Build 0051 transactional importer failed." }
}
finally {
    if (Test-Path -LiteralPath $TempRoot) { Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue }
}
