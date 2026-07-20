[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Package,
 [Parameter(Mandatory=$true)][string]$ExpectedPackageSha256,
 [string]$Repository="$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
 [string]$BackupRoot="$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Backups",
 [string]$ReportRoot="$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0045"
)
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
$CommitMessage="Add Certiaura Build 0045 retatrutide longitudinal journey tracking, review scheduling and clinician handoff baseline"
$RequiredClosurePrefix="46d92c2"
$ExtractRoot=$null;$OneDriveState=[pscustomobject]@{WasRunning=$false;Executable=$null};$Failure=$null;$AppliedBackup=$null;$CommitPushed=$false;$Stopped=$false
function Assert-Exit{param([string]$Operation);if($LASTEXITCODE -ne 0){throw "$Operation failed with exit code $LASTEXITCODE."}}
function Get-Python{$P=Get-Command python -ErrorAction SilentlyContinue;if($null -eq $P){$P=Get-Command py -ErrorAction SilentlyContinue};if($null -eq $P){throw "Python was not found on PATH."};return $P}
function Stop-OneDriveSafely{$P=@(Get-Process OneDrive -ErrorAction SilentlyContinue);$S=[ordered]@{WasRunning=$false;Executable=$null};if($P.Count -gt 0){$S.WasRunning=$true;try{$S.Executable=$P[0].Path}catch{};$P|Stop-Process -Force;Start-Sleep 2;if(@(Get-Process OneDrive -ErrorAction SilentlyContinue).Count -gt 0){throw "OneDrive could not be stopped."}};return [pscustomobject]$S}
function Start-OneDriveRobustly{param($State);if(-not $State.WasRunning){return "NOT_REQUIRED"};$C=New-Object System.Collections.Generic.List[string];if($State.Executable){$C.Add([string]$State.Executable)};if($env:LOCALAPPDATA){$C.Add((Join-Path $env:LOCALAPPDATA "Microsoft\OneDrive\OneDrive.exe"))};if($env:ProgramFiles){$C.Add((Join-Path $env:ProgramFiles "Microsoft OneDrive\OneDrive.exe"))};$X=[Environment]::GetEnvironmentVariable("ProgramFiles(x86)");if($X){$C.Add((Join-Path $X "Microsoft OneDrive\OneDrive.exe"))};$R=@($C|Where-Object{$_ -and (Test-Path -LiteralPath $_ -PathType Leaf)}|Select-Object -Unique);if($R.Count -eq 0){throw "OneDrive restart executable could not be resolved."};Start-Process -FilePath $R[0]|Out-Null;Start-Sleep 5;if(@(Get-Process OneDrive -ErrorAction SilentlyContinue).Count -eq 0){throw "OneDrive did not restart."};return "PASS"}
try{
 if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -lt 1){throw "Run in Windows PowerShell 5.1."}
 if(-not(Test-Path $Package -PathType Leaf)){throw "Package not found."};$Actual=(Get-FileHash $Package -Algorithm SHA256).Hash;if($Actual -ne $ExpectedPackageSha256.ToUpperInvariant()){throw "Package SHA-256 mismatch."}
 if(-not(Test-Path (Join-Path $Repository ".git") -PathType Container)){throw "Canonical repository not found."}
 $Dirty=@(git -C $Repository status --porcelain --untracked-files=all);Assert-Exit "Initial Git status";if($Dirty.Count -gt 0){$Dirty|ForEach-Object{Write-Host $_ -ForegroundColor Yellow};throw "Repository is not clean."}
 if((Test-Path (Join-Path $Repository ".certiaura_backups")) -and @(Get-ChildItem (Join-Path $Repository ".certiaura_backups") -Recurse -Force -ErrorAction SilentlyContinue).Count -gt 0){throw "Internal repository backup content is prohibited."}
 $Registers=@(Get-ChildItem $Repository -Recurse -File -Filter "Master_Asset_Register.csv"|Where-Object{$_.FullName -notmatch "[\\/]\.git[\\/]"});$Canonical=Join-Path $Repository "Documentation\Master_Asset_Register.csv";if($Registers.Count -ne 1 -or $Registers[0].FullName -ne $Canonical){throw "Canonical Master Asset Register is missing or ambiguous."}
 git -C $Repository fetch origin;Assert-Exit "Git fetch";git -C $Repository pull --ff-only;Assert-Exit "Git pull"
 $Matches=@(git -C $Repository rev-list --all|Where-Object{$_ -like ($RequiredClosurePrefix+"*")});Assert-Exit "Build 0044 closure search";if($Matches.Count -ne 1){throw "Expected one Build 0044 closure commit matching $RequiredClosurePrefix."};git -C $Repository merge-base --is-ancestor $Matches[0] HEAD;if($LASTEXITCODE -ne 0){throw "Build 0044 closure commit is not an ancestor of HEAD."}
 New-Item -ItemType Directory -Path $ReportRoot -Force|Out-Null;$ExtractRoot=Join-Path $env:TEMP ("Certiaura_0045_Run_"+[guid]::NewGuid().ToString("N"));Expand-Archive $Package $ExtractRoot -Force
 & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0045_Windows_PS51_Regression.ps1") -Package $Package -ExpectedPackageSha256 $ExpectedPackageSha256 -ReportRoot (Join-Path $ReportRoot "Windows_PS51_Regression") -SourceRepository $Repository
 if($LASTEXITCODE -ne 0){throw "Build 0045 release regression failed."}
 $Pre=Join-Path $ReportRoot "BUILD_0045_PREFLIGHT.json";$DryPath=Join-Path $ReportRoot "BUILD_0045_DRY_RUN.json";$ApplyPath=Join-Path $ReportRoot "BUILD_0045_APPLY.json"
 & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0045_Preflight.ps1") -Package $Package -Report $Pre
 & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0045_Import.ps1") -Package $Package -Repository $Repository -Report $DryPath
 $Dry=Get-Content $DryPath -Raw|ConvertFrom-Json;if($Dry.valid -ne $true -or $Dry.transaction_status -ne "DRY_RUN_VALIDATED" -or @($Dry.conflicts).Count -gt 0 -or @($Dry.errors).Count -gt 0){throw "Build 0045 dry-run did not validate."}
 if((Read-Host "Review the dry-run report. Type APPLY to continue") -cne "APPLY"){$Stopped=$true}else{
  $OneDriveState=Stop-OneDriveSafely
  & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0045_Import.ps1") -Package $Package -Repository $Repository -Report $ApplyPath -BackupRoot $BackupRoot -Apply
  $Apply=Get-Content $ApplyPath -Raw|ConvertFrom-Json;if($Apply.valid -ne $true -or $Apply.transaction_status -ne "APPLIED_VALIDATED"){throw "Build 0045 apply did not validate."};$AppliedBackup=$Apply.backup_path;if(-not(Test-Path $AppliedBackup -PathType Container)){throw "External backup missing."}
  $Python=Get-Python;& $Python.Source -B (Join-Path $Repository "13_Project_Genesis\Validators\validate_build_0045_retatrutide_longitudinal_review_handoff.py") $Repository --report (Join-Path $ReportRoot "BUILD_0045_VALIDATOR.json");Assert-Exit "Validator"
  & $Python.Source -B -m unittest discover -s (Join-Path $Repository "13_Project_Genesis\Tests") -p "test_build_0045_retatrutide_longitudinal_review_handoff.py";Assert-Exit "Tests"
  $O=Join-Path $ReportRoot "Runtime_Outputs";New-Item -ItemType Directory -Path $O -Force|Out-Null;$J=Join-Path $O "journey.json";$S=Join-Path $O "schedule.json";$HJ=Join-Path $O "handoff.json";$HM=Join-Path $O "handoff.md"
  & $Python.Source -B (Join-Path $Repository "Scripts\build_retatrutide_longitudinal_journey.py") (Join-Path $Repository "05_Monitoring\Retatrutide\Examples\longitudinal_journey_seed.example.json") --output $J;Assert-Exit "Journey"
  & $Python.Source -B (Join-Path $Repository "Scripts\generate_retatrutide_review_schedule.py") $J --policy (Join-Path $Repository "13_Project_Genesis\AI\retatrutide_review_scheduling_policy.json") --as-of "2026-07-20T12:00:00Z" --output $S;Assert-Exit "Schedule"
  & $Python.Source -B (Join-Path $Repository "Scripts\generate_retatrutide_clinician_handoff.py") $J $S --output-json $HJ --output-md $HM;Assert-Exit "Handoff"
  $Artifacts=@(Get-ChildItem $Repository -Recurse -Force|Where-Object{$_.Name -eq "__pycache__" -or $_.Extension -in @(".pyc",".pyo")});if($Artifacts.Count -gt 0){throw "Runtime artifacts detected."}
  $Deleted=@(git -C $Repository status --short --untracked-files=all|Where-Object{$_.Substring(0,2) -match "D"});if($Deleted.Count -gt 0){throw "Unexpected deletions detected."}
  git -C $Repository diff --check;Assert-Exit "git diff --check";git -C $Repository add -A;Assert-Exit "Git stage";git -C $Repository diff --cached --check;Assert-Exit "git diff --cached --check"
  git -C $Repository diff --cached --stat
  if((Read-Host "Review staged changes. Type COMMIT to commit and push") -cne "COMMIT"){$Stopped=$true}else{git -C $Repository commit -m $CommitMessage;Assert-Exit "Git commit";git -C $Repository push origin main;Assert-Exit "Git push";$CommitPushed=$true}
 }
}catch{$Failure=$_}
finally{
 if($Stopped -and $AppliedBackup -and -not $CommitPushed){try{$RollbackReport=Join-Path $ReportRoot "BUILD_0045_ROLLBACK.json";& (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0045_Import.ps1") -Repository $Repository -Report $RollbackReport -Rollback $AppliedBackup}catch{if($null -eq $Failure){$Failure=$_}}}
 if($null -ne $Failure -and $AppliedBackup -and -not $CommitPushed){try{$RollbackReport=Join-Path $ReportRoot "BUILD_0045_ROLLBACK.json";& (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0045_Import.ps1") -Repository $Repository -Report $RollbackReport -Rollback $AppliedBackup}catch{}}
 try{$Restart=Start-OneDriveRobustly $OneDriveState;Write-Host ("ONEDRIVE RESTART: "+$Restart) -ForegroundColor Green}catch{if($null -eq $Failure){$Failure=$_}}
 if($ExtractRoot -and (Test-Path $ExtractRoot)){Remove-Item $ExtractRoot -Recurse -Force -ErrorAction SilentlyContinue}
}
if($null -ne $Failure){Write-Host "BUILD 0045 STOPPED - FAIL-CLOSED" -ForegroundColor Red;throw $Failure}
if($Stopped){Write-Host "BUILD 0045 STOPPED WITHOUT COMMIT" -ForegroundColor Yellow;exit 0}
if($CommitPushed){Write-Host "BUILD 0045 COMMITTED AND PUSHED" -ForegroundColor Green;Write-Host "Next gate: confirm GitHub Actions green and record ACTIONS_GREEN_CLOSED."}
