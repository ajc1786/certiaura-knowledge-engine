[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Package,
 [Parameter(Mandatory=$true)][string]$ExpectedPackageSha256,
 [Parameter(Mandatory=$true)][string]$ReportRoot,
 [string]$SourceRepository = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RequiredImplementationCommit = "08793de672383c51df31d83015a9e768a09e16fd"
$RequiredCorrectionPrefix = "cc6e92e"
$Root = Join-Path $env:TEMP ("Certiaura_0044_PS51_" + [guid]::NewGuid().ToString("N"))
$PackageRoot = Join-Path $Root "package"
$SyntheticRepository = Join-Path $Root "repository"
$BackupRoot = Join-Path $Root "backups"
$OutputRoot = Join-Path $Root "outputs"
$Failure = $null
$OneDriveState = [pscustomobject]@{ WasRunning = $false; Executable = $null }
$Result = [ordered]@{}

function Assert-Exit {
 param([Parameter(Mandatory=$true)][string]$Operation)
 if ($LASTEXITCODE -ne 0) {
  throw "$Operation failed with exit code $LASTEXITCODE."
 }
}

function Get-Python {
 $Python = Get-Command python -ErrorAction SilentlyContinue
 if ($null -eq $Python) {
  $Python = Get-Command py -ErrorAction SilentlyContinue
 }
 if ($null -eq $Python) {
  throw "Python was not found on PATH."
 }
 return $Python
}

function Stop-OneDriveSafely {
 $Processes = @(Get-Process -Name OneDrive -ErrorAction SilentlyContinue)
 $State = [ordered]@{ WasRunning = $false; Executable = $null }
 if ($Processes.Count -gt 0) {
  $State.WasRunning = $true
  try { $State.Executable = $Processes[0].Path } catch {}
  $Processes | Stop-Process -Force
  Start-Sleep -Seconds 2
  $Remaining = @(Get-Process -Name OneDrive -ErrorAction SilentlyContinue)
  if ($Remaining.Count -gt 0) {
   throw "OneDrive could not be stopped."
  }
 }
 return [pscustomobject]$State
}

function Start-OneDriveRobustly {
 param([Parameter(Mandatory=$true)]$State)
 if (-not $State.WasRunning) {
  return "NOT_REQUIRED"
 }
 $CandidatePaths = New-Object System.Collections.Generic.List[string]
 if ($State.Executable) { $CandidatePaths.Add([string]$State.Executable) }
 if ($env:LOCALAPPDATA) {
  $CandidatePaths.Add((Join-Path $env:LOCALAPPDATA "Microsoft\OneDrive\OneDrive.exe"))
 }
 if ($env:ProgramFiles) {
  $CandidatePaths.Add((Join-Path $env:ProgramFiles "Microsoft OneDrive\OneDrive.exe"))
 }
 $ProgramFilesX86 = [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
 if ($ProgramFilesX86) {
  $CandidatePaths.Add((Join-Path $ProgramFilesX86 "Microsoft OneDrive\OneDrive.exe"))
 }
 $ResolvedCandidates = @(
  $CandidatePaths |
   Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } |
   Select-Object -Unique
 )
 if ($ResolvedCandidates.Count -eq 0) {
  throw "OneDrive restart executable could not be resolved."
 }
 $SingleCandidateRegression = @($ResolvedCandidates | Select-Object -First 1)
 if ($SingleCandidateRegression.Count -ne 1) {
  throw "StrictMode single-candidate array regression failed."
 }
 Start-Process -FilePath $ResolvedCandidates[0] | Out-Null
 Start-Sleep -Seconds 5
 $Restarted = @(Get-Process -Name OneDrive -ErrorAction SilentlyContinue)
 if ($Restarted.Count -eq 0) {
  throw "OneDrive did not restart."
 }
 return "PASS"
}

function Assert-PowerShellSources {
 param([Parameter(Mandatory=$true)][string]$RootPath)
 $Failures = New-Object System.Collections.Generic.List[string]
 $Scripts = @(Get-ChildItem -LiteralPath $RootPath -Recurse -Filter "*.ps1" -File)
 foreach ($Script in $Scripts) {
  $Bytes = [System.IO.File]::ReadAllBytes($Script.FullName)
  $NonAscii = @($Bytes | Where-Object { $_ -gt 127 })
  if ($NonAscii.Count -gt 0) {
   $Failures.Add("$($Script.FullName): non-ASCII byte detected")
  }
  $Tokens = $null
  $ParseErrors = $null
  [System.Management.Automation.Language.Parser]::ParseFile(
   $Script.FullName, [ref]$Tokens, [ref]$ParseErrors
  ) | Out-Null
  foreach ($ParseError in @($ParseErrors)) {
   $Failures.Add("$($Script.FullName): $($ParseError.Message)")
  }
 }
 if ($Failures.Count -gt 0) {
  $Failures | ForEach-Object { Write-Host $_ -ForegroundColor Red }
  throw "Windows PowerShell 5.1 parser or ASCII precheck failed."
 }
}

function Assert-NoRuntimeArtifacts {
 param([Parameter(Mandatory=$true)][string]$Repository)
 $Artifacts = @(
  Get-ChildItem -LiteralPath $Repository -Recurse -Force -ErrorAction SilentlyContinue |
   Where-Object {
    $_.Name -eq "__pycache__" -or
    $_.Extension -eq ".pyc" -or
    $_.Extension -eq ".pyo" -or
    $_.Name -match "^(GUIDED_DRY_RUN_REPORT|GUIDED_DRY_RUN_EXECUTIVE_SUMMARY).*\.json$"
   }
 )
 if ($Artifacts.Count -gt 0) {
  throw "Runtime artefacts were detected in the synthetic repository."
 }
}

try {
 if ($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -lt 1) {
  throw "Run the regression in Windows PowerShell 5.1."
 }
 if (-not (Test-Path -LiteralPath $Package -PathType Leaf)) {
  throw "Build 0044 package not found: $Package"
 }
 $ActualPackageSha256 = (Get-FileHash -LiteralPath $Package -Algorithm SHA256).Hash
 if ($ActualPackageSha256 -ne $ExpectedPackageSha256.ToUpperInvariant()) {
  throw "Package SHA-256 mismatch. Expected $ExpectedPackageSha256 but found $ActualPackageSha256."
 }
 if (-not (Test-Path -LiteralPath (Join-Path $SourceRepository ".git") -PathType Container)) {
  throw "Canonical source repository was not found: $SourceRepository"
 }
 $Dirty = @(git -C $SourceRepository status --porcelain --untracked-files=all)
 Assert-Exit "Source repository status"
 if ($Dirty.Count -gt 0) {
  throw "Canonical source repository is not clean."
 }
 git -C $SourceRepository merge-base --is-ancestor $RequiredImplementationCommit HEAD
 if ($LASTEXITCODE -ne 0) {
  throw "Required Build 0043 implementation commit is not an ancestor of HEAD."
 }
 $CorrectionMatches = @(
  git -C $SourceRepository rev-list --all |
   Where-Object { $_ -like ($RequiredCorrectionPrefix + "*") }
 )
 Assert-Exit "Build 0043 correction commit search"
 if ($CorrectionMatches.Count -ne 1) {
  throw "Expected one Build 0043 correction commit matching $RequiredCorrectionPrefix; found $($CorrectionMatches.Count)."
 }

 New-Item -ItemType Directory -Path $Root, $PackageRoot, $BackupRoot, $OutputRoot, $ReportRoot -Force | Out-Null
 Expand-Archive -LiteralPath $Package -DestinationPath $PackageRoot -Force

 $ParserHarness = Join-Path $Root "CMD_PS51_Parser_Precheck.ps1"
 $ParserHarnessContent = @'
param([string]$RootPath)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Scripts = @(Get-ChildItem -LiteralPath $RootPath -Recurse -Filter "*.ps1" -File)
foreach ($Script in $Scripts) {
 $Tokens = $null
 $Errors = $null
 [System.Management.Automation.Language.Parser]::ParseFile($Script.FullName,[ref]$Tokens,[ref]$Errors)|Out-Null
 if (@($Errors).Count -gt 0) { exit 3 }
}
exit 0
'@
 [System.IO.File]::WriteAllText(
  $ParserHarness,
  ($ParserHarnessContent -replace "`r`n", "`n"),
  [System.Text.Encoding]::ASCII
 )
 & cmd.exe /d /c powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ParserHarness -RootPath $PackageRoot
 Assert-Exit "CMD Windows PowerShell 5.1 parser precheck"
 Assert-PowerShellSources -RootPath $PackageRoot

 git clone --quiet --no-hardlinks $SourceRepository $SyntheticRepository
 Assert-Exit "Synthetic repository clone"
 git -C $SyntheticRepository config user.email "synthetic-regression@certiaura.local"
 git -C $SyntheticRepository config user.name "Certiaura Synthetic Regression"
 [System.IO.File]::WriteAllText(
  (Join-Path $SyntheticRepository "HISTORICAL_UNRELATED.txt"),
  "Unrelated historical file preserved by Build 0044 regression.`n",
  (New-Object System.Text.UTF8Encoding($false))
 )
 $HistoricalNoiseDirectory = Join-Path $SyntheticRepository "03_Biology"
 New-Item -ItemType Directory -Path $HistoricalNoiseDirectory -Force | Out-Null
 $HistoricalNoisePath = Join-Path $HistoricalNoiseDirectory "CERT-BKS-000044_Synthetic_Historical_Text.md"
 $HistoricalNoiseBytes = [System.Text.Encoding]::UTF8.GetBytes(
  "# Unrelated historical UAI 000044 fixture`r`nLegacy trailing whitespace. `r`n"
 )
 [System.IO.File]::WriteAllBytes($HistoricalNoisePath, $HistoricalNoiseBytes)
 git -C $SyntheticRepository add HISTORICAL_UNRELATED.txt 03_Biology/CERT-BKS-000044_Synthetic_Historical_Text.md
 git -C $SyntheticRepository commit --quiet -m "Add unrelated synthetic history"
 Assert-Exit "Synthetic history commit"

 $Python = Get-Python
 $PreflightReport = Join-Path $ReportRoot "BUILD_0044_PS51_PREFLIGHT.json"
 & $Python.Source -B (Join-Path $PackageRoot "Scripts\preflight_certiaura_build_0044.py") $Package --report $PreflightReport
 Assert-Exit "Build 0044 package preflight"

 $DryRunReport = Join-Path $ReportRoot "BUILD_0044_PS51_DRY_RUN.json"
 $ApplyReport = Join-Path $ReportRoot "BUILD_0044_PS51_APPLY.json"
 & $Python.Source -B (Join-Path $PackageRoot "Scripts\import_certiaura_build_0044.py") `
  --package $Package --repository $SyntheticRepository --report $DryRunReport
 Assert-Exit "Build 0044 synthetic dry-run"
 $DryRun = Get-Content -LiteralPath $DryRunReport -Raw | ConvertFrom-Json
 if ($DryRun.valid -ne $true -or $DryRun.transaction_status -ne "DRY_RUN_VALIDATED") {
  throw "Synthetic dry-run did not validate."
 }

 $OneDriveState = Stop-OneDriveSafely
 & $Python.Source -B (Join-Path $PackageRoot "Scripts\import_certiaura_build_0044.py") `
  --package $Package --repository $SyntheticRepository --report $ApplyReport `
  --backup-root $BackupRoot --apply
 Assert-Exit "Build 0044 synthetic apply"
 $Apply = Get-Content -LiteralPath $ApplyReport -Raw | ConvertFrom-Json
 if ($Apply.valid -ne $true -or $Apply.transaction_status -ne "APPLIED_VALIDATED") {
  throw "Synthetic apply did not validate."
 }

 & $Python.Source -B `
  (Join-Path $SyntheticRepository "13_Project_Genesis\Validators\validate_build_0044_retatrutide_interface_report_workflow.py") `
  $SyntheticRepository --report (Join-Path $ReportRoot "BUILD_0044_PS51_VALIDATOR.json")
 Assert-Exit "Build 0044 validator"
 & $Python.Source -B -m unittest discover `
  -s (Join-Path $SyntheticRepository "13_Project_Genesis\Tests") `
  -p "test_build_0044_retatrutide_interface_report_workflow.py"
 Assert-Exit "Build 0044 tests"

 $Profile = Join-Path $SyntheticRepository "12_Reports\Retatrutide\Examples\valid_patient_profile.example.json"
 $ReportJson = Join-Path $OutputRoot "patient_report.json"
 $ReportMarkdown = Join-Path $OutputRoot "patient_report.md"
 $ReportHtml = Join-Path $OutputRoot "patient_report.html"
 $RenderManifest = Join-Path $OutputRoot "render_manifest.json"
 $ReportPdf = Join-Path $OutputRoot "patient_report.pdf"
 & $Python.Source -B (Join-Path $SyntheticRepository "Scripts\generate_retatrutide_patient_journey_report.py") `
  $Profile --repository $SyntheticRepository --output-json $ReportJson --output-md $ReportMarkdown
 Assert-Exit "Build 0043 patient report generation"
 & $Python.Source -B (Join-Path $SyntheticRepository "Scripts\render_retatrutide_branded_report.py") `
  $ReportJson --brand-tokens (Join-Path $SyntheticRepository "Templates\retatrutide_report_brand_tokens.json") `
  --output-html $ReportHtml --manifest $RenderManifest
 Assert-Exit "Build 0044 HTML rendering"
 & (Join-Path $SyntheticRepository "Scripts\Convert_Certiaura_Build_0044_Report_To_Pdf.ps1") `
  -InputHtml $ReportHtml -OutputPdf $ReportPdf
 if (-not (Test-Path -LiteralPath $ReportPdf -PathType Leaf)) {
  throw "Build 0044 PDF rendering did not produce an output."
 }

 $ConversationStates = [ordered]@{}
 $ConversationExamples = @(
  "controlled_conversation_valid.example.json",
  "controlled_conversation_personal_dosing.example.json",
  "controlled_conversation_urgent.example.json",
  "controlled_conversation_identifiable_input.example.json"
 )
 foreach ($Example in $ConversationExamples) {
  $Output = Join-Path $OutputRoot ($Example -replace "\.example\.json$", ".output.json")
  & $Python.Source -B (Join-Path $SyntheticRepository "Scripts\run_retatrutide_controlled_conversation.py") `
   (Join-Path $SyntheticRepository "13_Project_Genesis\AI\Examples\$Example") `
   --repository $SyntheticRepository --output $Output
  Assert-Exit "Controlled conversation example $Example"
  $ConversationResult = Get-Content -LiteralPath $Output -Raw | ConvertFrom-Json
  $ConversationStates[$Example] = $ConversationResult.session_state
 }

 Assert-NoRuntimeArtifacts -Repository $SyntheticRepository
 $Deleted = @(
  git -C $SyntheticRepository status --short --untracked-files=all |
   Where-Object { $_ -match "^\s*D|^D" }
 )
 Assert-Exit "Synthetic deletion check"
 if ($Deleted.Count -gt 0) {
  throw "Unexpected deletions were detected."
 }
 git -C $SyntheticRepository diff --check
 Assert-Exit "git diff --check"
 git -C $SyntheticRepository add -A
 Assert-Exit "Synthetic stage"
 git -C $SyntheticRepository diff --cached --check
 Assert-Exit "git diff --cached --check"
 $Unstaged = @(git -C $SyntheticRepository diff --name-only)
 Assert-Exit "Synthetic unstaged check"
 if ($Unstaged.Count -gt 0) {
  throw "Unstaged changes remain in the synthetic repository."
 }
 if (-not (Test-Path -LiteralPath (Join-Path $SyntheticRepository "HISTORICAL_UNRELATED.txt") -PathType Leaf)) {
  throw "Unrelated historical file was not preserved."
 }
 if (-not (Test-Path -LiteralPath $HistoricalNoisePath -PathType Leaf)) {
  throw "Unrelated historical UAI 000044 fixture was not preserved."
 }
 if (-not (Test-Path -LiteralPath $Apply.backup_path -PathType Container)) {
  throw "Transactional backup was not created."
 }

 $Result = [ordered]@{
  valid = $true
  powershell_version = $PSVersionTable.PSVersion.ToString()
  package_sha256 = $ActualPackageSha256
  cmd_parser_precheck = "PASS"
  ascii_powershell = "PASS"
  build_0043_dependency = "PASS"
  dry_run = "PASS"
  apply = "PASS"
  validator = "PASS"
  tests = "PASS"
  branded_html = "PASS"
  branded_pdf = "PASS"
  controlled_conversation_states = $ConversationStates
  git_diff_check = "PASS"
  git_cached_diff_check = "PASS"
  unrelated_history_preserved = $true
  historical_uai_000044_noise_ignored = $true
  transactional_backup_created = $true
  cleanup_and_onedrive_restart = "PENDING_FINALLY"
 }
}
catch {
 $Failure = $_
}
finally {
 try {
  if (Test-Path -LiteralPath $Root) {
   Remove-Item -LiteralPath $Root -Recurse -Force -ErrorAction Stop
  }
  $RestartResult = Start-OneDriveRobustly -State $OneDriveState
  $Result["cleanup_and_onedrive_restart"] = $RestartResult
 }
 catch {
  if ($null -eq $Failure) {
   $Failure = $_
  }
  else {
   $Failure = New-Object System.Exception(
    ($Failure.Exception.Message + " Cleanup failure: " + $_.Exception.Message),
    $Failure.Exception
   )
  }
 }
}

if ($null -ne $Failure) {
 Write-Host "BUILD 0044 WINDOWS POWERSHELL 5.1 REGRESSION: FAIL" -ForegroundColor Red
 Write-Host $Failure.Exception.Message -ForegroundColor Red
 throw $Failure
}

$ResultPath = Join-Path $ReportRoot "BUILD_0044_WINDOWS_PS51_REGRESSION.json"
$Result | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $ResultPath -Encoding UTF8
Write-Host "BUILD 0044 WINDOWS POWERSHELL 5.1 REGRESSION: PASS" -ForegroundColor Green
