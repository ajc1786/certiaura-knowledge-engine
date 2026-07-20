[CmdletBinding()]
param(
 [string]$Repository = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
 [string]$HostAddress = "127.0.0.1",
 [int]$Port = 8765
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $Python) {
 $Python = Get-Command py -ErrorAction SilentlyContinue
}
if ($null -eq $Python) {
 throw "Python was not found on PATH."
}
$Server = Join-Path $Repository "Scripts\serve_retatrutide_patient_interface.py"
if (-not (Test-Path -LiteralPath $Server -PathType Leaf)) {
 throw "Build 0044 interface server is not installed: $Server"
}
& $Python.Source -B $Server --repository $Repository --host $HostAddress --port $Port
if ($LASTEXITCODE -ne 0) {
 throw "Build 0044 interface server exited with code $LASTEXITCODE."
}
