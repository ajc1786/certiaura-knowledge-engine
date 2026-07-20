[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Package,[Parameter(Mandatory=$true)][string]$ExpectedPackageSha256,[string]$Repository="$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",[string]$BackupRoot="$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Backups",[string]$ReportRoot="$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0046")
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
$CommitMessage="Add Certiaura Build 0046 retatrutide evidence-linked longitudinal analytics, outcome trend visualisation and controlled alerting baseline"
$RequiredPriorSubject="Add Certiaura Build 0045 retatrutide longitudinal journey tracking, review scheduling and clinician handoff baseline"
$ExtractRoot=$null;$OneDriveState=[pscustomobject]@{WasRunning=$false;Executable=$null};$Failure=$null;$AppliedBackup=$null;$CommitPushed=$false;$Stopped=$false
function Assert-Exit{param([string]$Operation);if($LASTEXITCODE -ne 0){throw "$Operation failed with exit code $LASTEXITCODE."}}
function Get-Python{$P=Get-Command python -ErrorAction SilentlyContinue;if($null -eq $P){$P=Get-Command py -ErrorAction SilentlyContinue};if($null -eq $P){throw "Python was not found on PATH."};return $P}
function Stop-OneDriveSafely{$P=@(Get-Process OneDrive -ErrorAction SilentlyContinue);$S=[ordered]@{WasRunning=$false;Executable=$null};if($P.Count -gt 0){$S.WasRunning=$true;try{$S.Executable=$P[0].Path}catch{};$P|Stop-Process -Force;Start-Sleep 2;if(@(Get-Process OneDrive -ErrorAction SilentlyContinue).Count -gt 0){throw "OneDrive could not be stopped."}};return [pscustomobject]$S}
function Start-OneDriveRobustly{param($State);if(-not $State.WasRunning){return "NOT_REQUIRED"};$C=New-Object System.Collections.Generic.List[string];if($State.Executable){$C.Add([string]$State.Executable)};if($env:LOCALAPPDATA){$C.Add((Join-Path $env:LOCALAPPDATA "Microsoft\OneDrive\OneDrive.exe"))};if($env:ProgramFiles){$C.Add((Join-Path $env:ProgramFiles "Microsoft OneDrive\OneDrive.exe"))};$X=[Environment]::GetEnvironmentVariable("ProgramFiles(x86)");if($X){$C.Add((Join-Path $X "Microsoft OneDrive\OneDrive.exe"))};$R=@($C|Where-Object{$_ -and (Test-Path -LiteralPath $_ -PathType Leaf)}|Select-Object -Unique);if($R.Count -eq 0){throw "OneDrive restart executable could not be resolved."};Start-Process -FilePath $R[0]|Out-Null;Start-Sleep 5;if(@(Get-Process OneDrive -ErrorAction SilentlyContinue).Count -eq 0){throw "OneDrive did not restart."};return "PASS"}
try{
 if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -lt 1){throw "Run in Windows PowerShell 5.1."}
 if(-not(Test-Path $Package -PathType Leaf)){throw "Package not found."};$Actual=(Get-FileHash $Package -Algorithm SHA256).Hash;if(-not [string]::Equals($Actual.Trim(),$ExpectedPackageSha256.Trim(),[StringComparison]::OrdinalIgnoreCase)){throw "Package SHA-256 mismatch."}
 if(-not(Test-Path (Join-Path $Repository ".git") -PathType Container)){throw "Canonical repository not found."}
 $Dirty=@(git -C $Repository status --porcelain --untracked-files=all);Assert-Exit "Initial Git status";if($Dirty.Count -gt 0){$Dirty|ForEach-Object{Write-Host $_ -ForegroundColor Yellow};throw "Repository is not clean."}
 if((Test-Path (Join-Path $Repository ".certiaura_backups")) -and @(Get-ChildItem (Join-Path $Repository ".certiaura_backups") -Recurse -Force -ErrorAction SilentlyContinue).Count -gt 0){throw "Internal repository backup content is prohibited."}
 $Registers=@(Get-ChildItem $Repository -Recurse -File -Filter "Master_Asset_Register.csv"|Where-Object{$_.FullName -notmatch "[\\/]\.git[\\/]" -and $_.FullName -notmatch "[\\/]\.certiaura_backups[\\/]"});$Canonical=Join-Path $Repository "Documentation\Master_Asset_Register.csv";if($Registers.Count -ne 1 -or $Registers[0].FullName -ne $Canonical){throw "Canonical Master Asset Register is missing or ambiguous."}
 git -C $Repository fetch origin;Assert-Exit "Git fetch";git -C $Repository pull --ff-only;Assert-Exit "Git pull"
 $PriorMatches=@(git -C $Repository log --all --format="%H`t%s"|Where-Object{$_ -like ("*`t"+$RequiredPriorSubject)});Assert-Exit "Build 0045 commit resolution";if($PriorMatches.Count -ne 1){throw "Expected exactly one Build 0045 implementation commit by exact subject."};$PriorParts=$PriorMatches[0] -split "`t",2;$PriorHash=$PriorParts[0];$PriorSubject=$PriorParts[1];git -C $Repository merge-base --is-ancestor $PriorHash HEAD;if($LASTEXITCODE -ne 0){throw "Build 0045 implementation commit is not an ancestor of HEAD."}
 New-Item -ItemType Directory -Path $ReportRoot -Force|Out-Null;$Closure=[ordered]@{build_number="0045";status="ACTIONS_GREEN_CLOSED";commit=$PriorHash;commit_subject=$PriorSubject;confirmation="USER_CONFIRMED_GITHUB_ACTIONS_GREEN"};$Closure|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $ReportRoot "BUILD_0045_CLOSURE_RESOLUTION.json") -Encoding UTF8
 $ExtractRoot=Join-Path $env:TEMP ("Certiaura_0046_Run_"+[guid]::NewGuid().ToString("N"));Expand-Archive $Package $ExtractRoot -Force
 & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0046_Windows_PS51_Regression.ps1") -Package $Package -ExpectedPackageSha256 $ExpectedPackageSha256 -ReportRoot (Join-Path $ReportRoot "Windows_PS51_Regression") -SourceRepository $Repository
 if($LASTEXITCODE -ne 0){throw "Build 0046 release regression failed."}
 $Pre=Join-Path $ReportRoot "BUILD_0046_PREFLIGHT.json";$DryPath=Join-Path $ReportRoot "BUILD_0046_DRY_RUN.json";$ApplyPath=Join-Path $ReportRoot "BUILD_0046_APPLY.json"
 & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0046_Preflight.ps1") -Package $Package -Report $Pre
 & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0046_Import.ps1") -Package $Package -Repository $Repository -Report $DryPath
 $Dry=Get-Content $DryPath -Raw|ConvertFrom-Json;if($Dry.valid -ne $true -or $Dry.transaction_status -ne "DRY_RUN_VALIDATED" -or @($Dry.conflicts).Count -gt 0 -or @($Dry.errors).Count -gt 0){throw "Build 0046 dry-run did not validate."}
 if((Read-Host "Review the dry-run report. Type APPLY to continue").Trim().ToUpperInvariant() -ne "APPLY"){$Stopped=$true}else{
  $OneDriveState=Stop-OneDriveSafely
  & (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0046_Import.ps1") -Package $Package -Repository $Repository -Report $ApplyPath -BackupRoot $BackupRoot -Apply
  $Apply=Get-Content $ApplyPath -Raw|ConvertFrom-Json;if($Apply.valid -ne $true -or $Apply.transaction_status -ne "APPLIED_VALIDATED"){throw "Build 0046 apply did not validate."};$AppliedBackup=$Apply.backup_path;if(-not(Test-Path $AppliedBackup -PathType Container)){throw "External backup missing."}
  $Python=Get-Python;& $Python.Source -B (Join-Path $Repository "13_Project_Genesis\Validators\validate_build_0046_retatrutide_analytics_visualisation_alerting.py") $Repository --report (Join-Path $ReportRoot "BUILD_0046_VALIDATOR.json");Assert-Exit "Validator"
  & $Python.Source -B -m unittest discover -s (Join-Path $Repository "13_Project_Genesis\Tests") -p "test_build_0046_retatrutide_analytics_visualisation_alerting.py";Assert-Exit "Tests"
  $O=Join-Path $ReportRoot "Runtime_Outputs";New-Item -ItemType Directory -Path $O -Force|Out-Null;$A=Join-Path $O "analytics.json";$TJ=Join-Path $O "trend.json";$TS=Join-Path $O "trend.svg";$C=Join-Path $O "alert.json"
  & $Python.Source -B (Join-Path $Repository "Scripts\analyze_retatrutide_longitudinal_outcomes.py") (Join-Path $Repository "05_Monitoring\Retatrutide\Analytics\Examples\analytics_journey.example.json") --policy (Join-Path $Repository "13_Project_Genesis\AI\retatrutide_controlled_alerting_policy.json") --output $A;Assert-Exit "Analytics"
  & $Python.Source -B (Join-Path $Repository "Scripts\render_retatrutide_outcome_trends.py") $A --output-json $TJ --output-svg $TS;Assert-Exit "Trend"
  & $Python.Source -B (Join-Path $Repository "Scripts\evaluate_retatrutide_controlled_alerts.py") (Join-Path $Repository "05_Monitoring\Retatrutide\Analytics\Examples\analytics_journey.example.json") $A (Join-Path $Repository "05_Monitoring\Retatrutide\Analytics\Examples\review_schedule.example.json") --policy (Join-Path $Repository "13_Project_Genesis\AI\retatrutide_controlled_alerting_policy.json") --output $C;Assert-Exit "Alert"
  $Artifacts=@(Get-ChildItem $Repository -Recurse -Force|Where-Object{$_.Name -eq "__pycache__" -or $_.Extension -in @(".pyc",".pyo")});if($Artifacts.Count -gt 0){throw "Runtime artifacts detected."}
  $Deleted=@(git -C $Repository status --short --untracked-files=all|Where-Object{$_.Length -ge 2 -and $_.Substring(0,2) -match "D"});if($Deleted.Count -gt 0){throw "Unexpected deletions detected."}
  git -C $Repository diff --check;Assert-Exit "git diff --check";git -C $Repository add -A;Assert-Exit "Git stage";git -C $Repository diff --cached --check;Assert-Exit "git diff --cached --check"
  git -C $Repository --no-pager diff --cached --stat
  if((Read-Host "Review staged changes. Type COMMIT to commit and push").Trim().ToUpperInvariant() -ne "COMMIT"){$Stopped=$true}else{git -C $Repository commit -m $CommitMessage;Assert-Exit "Git commit";git -C $Repository push origin main;Assert-Exit "Git push";$CommitPushed=$true}
 }
}catch{$Failure=$_}
finally{
 if($Stopped -and $AppliedBackup -and -not $CommitPushed){try{$RollbackReport=Join-Path $ReportRoot "BUILD_0046_ROLLBACK.json";& (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0046_Import.ps1") -Repository $Repository -Report $RollbackReport -Rollback $AppliedBackup}catch{if($null -eq $Failure){$Failure=$_}}}
 if($null -ne $Failure -and $AppliedBackup -and -not $CommitPushed){try{$RollbackReport=Join-Path $ReportRoot "BUILD_0046_ROLLBACK.json";& (Join-Path $ExtractRoot "Scripts\Invoke_Certiaura_Build_0046_Import.ps1") -Repository $Repository -Report $RollbackReport -Rollback $AppliedBackup}catch{}}
 try{$Restart=Start-OneDriveRobustly $OneDriveState;Write-Host ("ONEDRIVE RESTART: "+$Restart) -ForegroundColor Green}catch{if($null -eq $Failure){$Failure=$_}}
 if($ExtractRoot -and (Test-Path $ExtractRoot)){Remove-Item $ExtractRoot -Recurse -Force -ErrorAction SilentlyContinue}
}
if($null -ne $Failure){Write-Host "BUILD 0046 STOPPED - FAIL-CLOSED" -ForegroundColor Red;throw $Failure}
if($Stopped){Write-Host "BUILD 0046 STOPPED WITHOUT COMMIT" -ForegroundColor Yellow;exit 0}
if($CommitPushed){Write-Host "BUILD 0046 COMMITTED AND PUSHED" -ForegroundColor Green;Write-Host "Next gate: confirm GitHub Actions green and record ACTIONS_GREEN_CLOSED."}
