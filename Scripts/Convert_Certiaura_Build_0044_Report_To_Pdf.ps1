[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$InputHtml,
 [Parameter(Mandatory=$true)][string]$OutputPdf,
 [int]$TimeoutSeconds = 60
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-BrowserCandidates {
 $Candidates = New-Object System.Collections.Generic.List[string]
 if ($env:ProgramFiles) {
  $Candidates.Add((Join-Path $env:ProgramFiles "Microsoft\Edge\Application\msedge.exe"))
  $Candidates.Add((Join-Path $env:ProgramFiles "Google\Chrome\Application\chrome.exe"))
 }
 $ProgramFilesX86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
 if ($ProgramFilesX86) {
  $Candidates.Add((Join-Path $ProgramFilesX86 "Microsoft\Edge\Application\msedge.exe"))
  $Candidates.Add((Join-Path $ProgramFilesX86 "Google\Chrome\Application\chrome.exe"))
 }
 if ($env:LOCALAPPDATA) {
  $Candidates.Add((Join-Path $env:LOCALAPPDATA "Microsoft\Edge\Application\msedge.exe"))
  $Candidates.Add((Join-Path $env:LOCALAPPDATA "Google\Chrome\Application\chrome.exe"))
 }
 return @(
  $Candidates |
   Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } |
   Select-Object -Unique
 )
}

if (-not (Test-Path -LiteralPath $InputHtml -PathType Leaf)) {
 throw "Input HTML not found: $InputHtml"
}
$InputHtml = (Resolve-Path -LiteralPath $InputHtml).Path
$OutputPdf = [System.IO.Path]::GetFullPath($OutputPdf)
$OutputDirectory = Split-Path $OutputPdf -Parent
if (-not $OutputDirectory) {
 throw "Output PDF must include a parent directory."
}
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
if (Test-Path -LiteralPath $OutputPdf) {
 Remove-Item -LiteralPath $OutputPdf -Force
}

$Browsers = @(Get-BrowserCandidates)
if ($Browsers.Count -eq 0) {
 throw "Microsoft Edge or Google Chrome could not be resolved."
}
$Browser = $Browsers[0]
$FileUri = ([System.Uri]$InputHtml).AbsoluteUri
$Arguments = @(
 "--headless",
 "--disable-gpu",
 "--no-pdf-header-footer",
 "--run-all-compositor-stages-before-draw",
 "--virtual-time-budget=5000",
 "--print-to-pdf=$OutputPdf",
 $FileUri
)

$Process = Start-Process -FilePath $Browser -ArgumentList $Arguments -PassThru -WindowStyle Hidden
if (-not $Process.WaitForExit($TimeoutSeconds * 1000)) {
 try { $Process.Kill() } catch {}
 throw "Browser PDF rendering exceeded $TimeoutSeconds seconds."
}
if ($Process.ExitCode -ne 0) {
 throw "Browser PDF rendering failed with exit code $($Process.ExitCode)."
}
if (-not (Test-Path -LiteralPath $OutputPdf -PathType Leaf)) {
 throw "PDF output was not created: $OutputPdf"
}
$Bytes = [System.IO.File]::ReadAllBytes($OutputPdf)
if ($Bytes.Length -lt 1024) {
 throw "PDF output is unexpectedly small."
}
$Header = [System.Text.Encoding]::ASCII.GetString($Bytes, 0, [Math]::Min(5, $Bytes.Length))
if ($Header -ne "%PDF-") {
 throw "PDF output does not contain a valid PDF header."
}
$TailStart = [Math]::Max(0, $Bytes.Length - 2048)
$Tail = [System.Text.Encoding]::ASCII.GetString($Bytes, $TailStart, $Bytes.Length - $TailStart)
if (-not $Tail.Contains("%%EOF")) {
 throw "PDF output does not contain a PDF end marker."
}

$Result = [ordered]@{
 valid = $true
 browser = $Browser
 input_html = $InputHtml
 output_pdf = $OutputPdf
 output_bytes = $Bytes.Length
 sha256 = (Get-FileHash -LiteralPath $OutputPdf -Algorithm SHA256).Hash
}
$Result | ConvertTo-Json -Depth 5
Write-Host "BUILD 0044 BRANDED PDF RENDER: PASS" -ForegroundColor Green
