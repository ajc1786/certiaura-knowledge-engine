[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Package,

    [Parameter(Mandatory = $true)]
    [string]$Report
)

$ErrorActionPreference = "Stop"
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue }
if ($null -eq $Python) { throw "Python was not found." }

$TempRoot = Join-Path $env:TEMP ("Certiaura_0041_Preflight_" + [guid]::NewGuid().ToString("N"))
try {
    Expand-Archive -LiteralPath $Package -DestinationPath $TempRoot -Force
    $Preflight = Join-Path $TempRoot "13_Project_Genesis\Release\run_build_0041_preflight.py"
    if (-not (Test-Path -LiteralPath $Preflight -PathType Leaf)) { throw "Build 0041 preflight is missing." }
    & $Python.Source -B $Preflight --package $Package --report $Report
    if ($LASTEXITCODE -ne 0) { throw "Build 0041 preflight failed." }
}
finally {
    if (Test-Path -LiteralPath $TempRoot) { Remove-Item -LiteralPath $TempRoot -Recurse -Force }
}
