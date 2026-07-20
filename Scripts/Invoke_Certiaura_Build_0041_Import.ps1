[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Repository,

    [Parameter(Mandatory = $true)]
    [string]$Package,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[A-Fa-f0-9]{64}$")]
    [string]$PackageSha256,

    [Parameter(Mandatory = $true)]
    [string]$Report,

    [switch]$Apply,

    [string]$BackupRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Backups"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Package -PathType Leaf)) {
    throw "Build package is missing: $Package"
}
$ActualSha256 = (Get-FileHash -LiteralPath $Package -Algorithm SHA256).Hash.ToUpperInvariant()
$ExpectedSha256 = $PackageSha256.ToUpperInvariant()
if ($ActualSha256 -ne $ExpectedSha256) {
    throw "Build package SHA-256 mismatch. Expected $ExpectedSha256 but found $ActualSha256."
}

$TempRoot = Join-Path $env:TEMP ("Certiaura_0041_" + [guid]::NewGuid().ToString("N"))
$PreviousBackupRoot = $env:CERTIAURA_BACKUP_ROOT

try {
    Expand-Archive -LiteralPath $Package -DestinationPath $TempRoot -Force
    $Runner = Join-Path $TempRoot "13_Project_Genesis\Import\run_build_0041_import.py"
    if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) {
        throw "Build 0041 import runner is missing."
    }

    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue }
    if ($null -eq $Python) { throw "Python was not found." }

    $Arguments = @(
        "-B", $Runner,
        "--package", $Package,
        "--repository", $Repository,
        "--report", $Report,
        "--expected-sha256", $ExpectedSha256
    )

    if ($Apply) {
        $env:CERTIAURA_BACKUP_ROOT = $BackupRoot
        $Arguments += "--apply"
    }

    & $Python.Source @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Build 0041 import runner failed." }
}
finally {
    if ($null -eq $PreviousBackupRoot) {
        Remove-Item Env:CERTIAURA_BACKUP_ROOT -ErrorAction SilentlyContinue
    } else {
        $env:CERTIAURA_BACKUP_ROOT = $PreviousBackupRoot
    }
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force
    }
}
