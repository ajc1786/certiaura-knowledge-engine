[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Package,
 [Parameter(Mandatory=$true)][string]$ExpectedPackageSha256,
 [string]$Repository = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
 [string]$BackupRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Backups",
 [string]$ReportRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0044"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$CommitMessage = "Add Certiaura Build 0044 retatrutide patient-facing interface, branded report rendering and controlled conversation workflow baseline"
$RequiredImplementationCommit = "08793de672383c51df31d83015a9e768a09e16fd"
$RequiredCorrectionPrefix = "cc6e92e"
$ExtractRoot = $null
$OneDriveState = [pscustomobject]@{ WasRunning = $false; Executable = $null }
$Failure = $null
$CommitPushed = $false
$StoppedBeforeCommit = $false

function Assert-Exit {
 param([Parameter(Mandatory=$true)][string]$Operation)
 if ($LASTEXITCODE -ne 0) {
  throw "$Operation failed with exit code $LASTEXITCODE."
 }
}

function Get-Python {
 $Python = Get-Command python -ErrorAction SilentlyContinue
 if ($null -eq $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue }
 if ($null -eq $Python) { throw "Python was not found on PATH." }
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
  if ($Remaining.Count -gt 0) { throw "OneDrive could not be stopped." }
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
 Start-Process -FilePath $ResolvedCandidates[0] | Out-Null
 Start-Sleep -Seconds 5
 $Restarted = @(Get-Process -Name OneDrive -ErrorAction SilentlyContinue)
 if ($Restarted.Count -eq 0) {
  throw "OneDrive did not restart."
 }
 return "PASS"
}

function Assert-NoRuntimeArtifacts {
 param([Parameter(Mandatory=$true)][string]$RepositoryPath)
 $Artifacts = @(
  Get-ChildItem -LiteralPath $RepositoryPath -Recurse -Force -ErrorAction SilentlyContinue |
   Where-Object {
    $_.Name -eq "__pycache__" -or
    $_.Extension -eq ".pyc" -or
    $_.Extension -eq ".pyo" -or
    $_.Name -match "^(GUIDED_DRY_RUN_REPORT|GUIDED_DRY_RUN_EXECUTIVE_SUMMARY).*\.json$"
   }
 )
 if ($Artifacts.Count -gt 0) {
  $Artifacts | ForEach-Object { Write-Host $_.FullName -ForegroundColor Red }
  throw "Runtime artefacts were detected."
 }
}

try {
 if ($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -lt 1) {
  throw "Run the canonical workflow in Windows PowerShell 5.1."
 }
 if (-not (Test-Path -LiteralPath $Package -PathType Leaf)) {
  throw "Package not found: $Package"
 }
 $ActualPackageSha256 = (Get-FileHash -LiteralPath $Package -Algorithm SHA256).Hash
 if ($ActualPackageSha256 -ne $ExpectedPackageSha256.ToUpperInvariant()) {
  throw "Package SHA-256 mismatch. Expected $ExpectedPackageSha256 but found $ActualPackageSha256."
 }
 if (-not (Test-Path -LiteralPath (Join-Path $Repository ".git") -PathType Container)) {
  throw "Canonical repository is not a Git repository: $Repository"
 }

 $Dirty = @(git -C $Repository status --porcelain --untracked-files=all)
 Assert-Exit "Initial repository status"
 if ($Dirty.Count -gt 0) {
  $Dirty | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
  throw "Canonical repository is not clean."
 }

 git -C $Repository fetch origin
 Assert-Exit "Git fetch"
 git -C $Repository pull --ff-only
 Assert-Exit "Git pull --ff-only"
 git -C $Repository merge-base --is-ancestor $RequiredImplementationCommit HEAD
 if ($LASTEXITCODE -ne 0) {
  throw "Required Build 0043 implementation commit is not an ancestor of HEAD."
 }
 $CorrectionMatches = @(
  git -C $Repository rev-list --all |
   Where-Object { $_ -like ($RequiredCorrectionPrefix + "*") }
 )
 Assert-Exit "Build 0043 correction search"
 if ($CorrectionMatches.Count -ne 1) {
  throw "Expected one Build 0043 correction commit matching $RequiredCorrectionPrefix; found $($CorrectionMatches.Count)."
 }

 New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
 $ExtractRoot = Join-Path $env:TEMP ("Certiaura_0044_Run_" + [guid]::NewGuid().ToString("N"))
 Expand-Archive -LiteralPath $Package -DestinationPath $ExtractRoot -Force

 & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0044_Windows_PS51_Regression.ps1") `
  -Package $Package `
  -ExpectedPackageSha256 $ExpectedPackageSha256 `
  -ReportRoot (Join-Path $ReportRoot "Windows_PS51_Regression") `
  -SourceRepository $Repository
 if ($LASTEXITCODE -ne 0) {
  throw "Build 0044 Windows PowerShell 5.1 release regression failed."
 }

 $PreflightReport = Join-Path $ReportRoot "BUILD_0044_PREFLIGHT.json"
 $DryRunReport = Join-Path $ReportRoot "BUILD_0044_DRY_RUN.json"
 $ApplyReport = Join-Path $ReportRoot "BUILD_0044_APPLY.json"

 & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0044_Preflight.ps1") `
  -Package $Package -Report $PreflightReport
 & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0044_Import.ps1") `
  -Package $Package -Repository $Repository -Report $DryRunReport

 $DryRun = Get-Content -LiteralPath $DryRunReport -Raw | ConvertFrom-Json
 if ($DryRun.valid -ne $true -or $DryRun.transaction_status -ne "DRY_RUN_VALIDATED") {
  throw "Build 0044 dry-run did not validate."
 }
 if (@($DryRun.conflicts).Count -gt 0 -or @($DryRun.errors).Count -gt 0) {
  throw "Build 0044 dry-run contains conflicts or errors."
 }

 $ApplyApproval = Read-Host "Review the dry-run report. Type APPLY to continue"
 if ($ApplyApproval -cne "APPLY") {
  $StoppedBeforeCommit = $true
 }
 else {
  $OneDriveState = Stop-OneDriveSafely
  & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0044_Import.ps1") `
   -Package $Package -Repository $Repository -Report $ApplyReport `
   -BackupRoot $BackupRoot -Apply
  $Apply = Get-Content -LiteralPath $ApplyReport -Raw | ConvertFrom-Json
  if ($Apply.valid -ne $true -or $Apply.transaction_status -ne "APPLIED_VALIDATED") {
   throw "Build 0044 apply did not validate."
  }
  if (-not (Test-Path -LiteralPath $Apply.backup_path -PathType Container)) {
   throw "Build 0044 external transactional backup was not created."
  }

  $Python = Get-Python
  & $Python.Source -B `
   (Join-Path $Repository "13_Project_Genesis\Validators\validate_build_0044_retatrutide_interface_report_workflow.py") `
   $Repository --report (Join-Path $ReportRoot "BUILD_0044_VALIDATOR.json")
  Assert-Exit "Build 0044 validator"

  & $Python.Source -B -m unittest discover `
   -s (Join-Path $Repository "13_Project_Genesis\Tests") `
   -p "test_build_0044_retatrutide_interface_report_workflow.py"
  Assert-Exit "Build 0044 tests"

  $OutputRoot = Join-Path $ReportRoot "Runtime_Outputs"
  New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
  $Profile = Join-Path $Repository "12_Reports\Retatrutide\Examples\valid_patient_profile.example.json"
  $ReportJson = Join-Path $OutputRoot "patient_report.json"
  $ReportMarkdown = Join-Path $OutputRoot "patient_report.md"
  $ReportHtml = Join-Path $OutputRoot "patient_report.html"
  $RenderManifest = Join-Path $OutputRoot "render_manifest.json"
  $ReportPdf = Join-Path $OutputRoot "patient_report.pdf"

  & $Python.Source -B (Join-Path $Repository "Scripts\generate_retatrutide_patient_journey_report.py") `
   $Profile --repository $Repository --output-json $ReportJson --output-md $ReportMarkdown
  Assert-Exit "Build 0043 report generation"
  & $Python.Source -B (Join-Path $Repository "Scripts\render_retatrutide_branded_report.py") `
   $ReportJson --brand-tokens (Join-Path $Repository "Templates\retatrutide_report_brand_tokens.json") `
   --output-html $ReportHtml --manifest $RenderManifest
  Assert-Exit "Build 0044 HTML rendering"
  & (Join-Path $Repository "Scripts\Convert_Certiaura_Build_0044_Report_To_Pdf.ps1") `
   -InputHtml $ReportHtml -OutputPdf $ReportPdf
  if (-not (Test-Path -LiteralPath $ReportPdf -PathType Leaf)) {
   throw "Build 0044 PDF output was not created."
  }

  foreach ($Example in @(
   "controlled_conversation_valid.example.json",
   "controlled_conversation_personal_dosing.example.json",
   "controlled_conversation_urgent.example.json",
   "controlled_conversation_identifiable_input.example.json"
  )) {
   $ConversationOutput = Join-Path $OutputRoot ($Example -replace "\.example\.json$", ".output.json")
   & $Python.Source -B (Join-Path $Repository "Scripts\run_retatrutide_controlled_conversation.py") `
    (Join-Path $Repository "13_Project_Genesis\AI\Examples\$Example") `
    --repository $Repository --output $ConversationOutput
   Assert-Exit "Controlled conversation example $Example"
  }

  Assert-NoRuntimeArtifacts -RepositoryPath $Repository
  $Deleted = @(
   git -C $Repository status --short --untracked-files=all |
    Where-Object { $_ -match "^\s*D|^D" }
  )
  Assert-Exit "Unexpected deletion check"
  if ($Deleted.Count -gt 0) {
   $Deleted | ForEach-Object { Write-Host $_ -ForegroundColor Red }
   throw "Unexpected deletions were detected."
  }

  git -C $Repository diff --check
  Assert-Exit "git diff --check"
  git -C $Repository add -A
  Assert-Exit "Git stage"
  git -C $Repository diff --cached --check
  Assert-Exit "git diff --cached --check"

  $Unstaged = @(git -C $Repository diff --name-only)
  Assert-Exit "Unstaged change check"
  if ($Unstaged.Count -gt 0) {
   throw "Unstaged changes remain after staging."
  }
  $Staged = @(git -C $Repository diff --cached --name-only)
  Assert-Exit "Staged change check"
  if ($Staged.Count -eq 0) {
   throw "No Build 0044 changes are staged."
  }

  git -C $Repository status --short --untracked-files=all
  $CommitApproval = Read-Host "Review staged changes. Type COMMIT to commit and push"
  if ($CommitApproval -cne "COMMIT") {
   $StoppedBeforeCommit = $true
  }
  else {
   git -C $Repository commit -m $CommitMessage
   Assert-Exit "Git commit"
   git -C $Repository push origin main
   Assert-Exit "Git push"
   $CommitPushed = $true
  }
 }
}
catch {
 $Failure = $_
}
finally {
 try {
  if ($ExtractRoot -and (Test-Path -LiteralPath $ExtractRoot)) {
   Remove-Item -LiteralPath $ExtractRoot -Recurse -Force -ErrorAction Stop
  }
  $RestartResult = Start-OneDriveRobustly -State $OneDriveState
  if ($RestartResult -eq "PASS") {
   Write-Host "ONEDRIVE RESTARTED: PASS" -ForegroundColor Green
  }
  else {
   Write-Host "ONEDRIVE RESTART: NOT REQUIRED" -ForegroundColor Green
  }
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
 Write-Host "BUILD 0044 STOPPED - FAIL-CLOSED" -ForegroundColor Red
 Write-Host $Failure.Exception.Message -ForegroundColor Red
 throw $Failure
}
if ($CommitPushed) {
 Write-Host "BUILD 0044 COMMITTED AND PUSHED" -ForegroundColor Green
 Write-Host "Next gate: confirm GitHub Actions green, complete lessons learned, and record ACTIONS_GREEN_CLOSED."
}
elseif ($StoppedBeforeCommit) {
 Write-Host "BUILD 0044 STOPPED BY OPERATOR BEFORE COMMIT" -ForegroundColor Yellow
 Write-Host "No Build 0044 commit or push was performed."
}
