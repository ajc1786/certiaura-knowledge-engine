[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Package,
 [Parameter(Mandatory=$true)][string]$ExpectedPackageSha256,
 [string]$Repository = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
 [string]$BackupRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Backups",
 [string]$ReportRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0043"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$CommitMessage = "Add Certiaura Build 0043 retatrutide patient journey report generation and AI query integration baseline"
$RequiredBuild0042Commits = @("d1557f4cd7d4f4bc05385929e047f44d1e72d214","96324d10ddcb0c0e8e553a1cf678f74d0aa62902")
$RequiredClosurePrefix = "13a458561afbcbe47c11a"
function Assert-Exit([string]$Name) { if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit code $LASTEXITCODE." } }
function Stop-OneDriveSafely {
 $State=[ordered]@{WasRunning=$false;Executable=$null}; $P=@(Get-Process -Name OneDrive -ErrorAction SilentlyContinue)
 if ($P.Count -gt 0) { $State.WasRunning=$true; try{$State.Executable=$P[0].Path}catch{}; $P|Stop-Process -Force; Start-Sleep -Seconds 2; if(Get-Process -Name OneDrive -ErrorAction SilentlyContinue){throw "OneDrive could not be stopped."} }
 return [pscustomobject]$State
}
function Start-OneDriveIfRequired($State) {
 if(-not $State.WasRunning){return}; $C=@($State.Executable,(Join-Path $env:LOCALAPPDATA "Microsoft\OneDrive\OneDrive.exe"),(Join-Path $env:ProgramFiles "Microsoft OneDrive\OneDrive.exe"),(Join-Path ${env:ProgramFiles(x86)} "Microsoft OneDrive\OneDrive.exe"))|Where-Object{$_ -and (Test-Path -LiteralPath $_ -PathType Leaf)}|Select-Object -Unique
 if($C.Count -gt 0){Start-Process -FilePath $C[0]|Out-Null}else{Write-Warning "OneDrive restart path could not be resolved."}
}
$OneDrive=[pscustomobject]@{WasRunning=$false;Executable=$null}; $Extract=$null
try {
 if ($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -lt 1) { throw "Run this workflow in Windows PowerShell 5.1." }
 if (-not (Test-Path -LiteralPath $Package -PathType Leaf)) { throw "Package not found: $Package" }
 $ActualPackageSha256=(Get-FileHash -LiteralPath $Package -Algorithm SHA256).Hash
 if ($ActualPackageSha256 -ne $ExpectedPackageSha256.ToUpperInvariant()) { throw "Package SHA-256 mismatch. Expected $ExpectedPackageSha256 but found $ActualPackageSha256." }
 if (-not (Test-Path -LiteralPath (Join-Path $Repository ".git") -PathType Container)) { throw "Repository is not a Git repository." }
 $Dirty=@(git -C $Repository status --porcelain --untracked-files); Assert-Exit "Git status"; if($Dirty.Count -gt 0){throw "Repository is not clean."}
 git -C $Repository fetch origin; Assert-Exit "Git fetch"; git -C $Repository pull --ff-only; Assert-Exit "Git pull --ff-only"
 foreach($C in $RequiredBuild0042Commits){ git -C $Repository merge-base --is-ancestor $C HEAD; if($LASTEXITCODE -ne 0){throw "Required Build 0042 commit is not an ancestor of HEAD: $C"} }
 $Closure=@(git -C $Repository rev-list --all | Where-Object { $_ -like ($RequiredClosurePrefix + "*") }); Assert-Exit "Closure checkpoint search"; if($Closure.Count -ne 1){throw "Expected one Build 0042 closure checkpoint matching $RequiredClosurePrefix; found $($Closure.Count)."}
 New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
 $Extract=Join-Path $env:TEMP ("Certiaura_0043_Run_"+[guid]::NewGuid().ToString("N")); Expand-Archive -LiteralPath $Package -DestinationPath $Extract -Force
 & (Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0043_Windows_PS51_Regression.ps1") -Package $Package -ReportRoot (Join-Path $ReportRoot "Windows_PS51_Regression")
 $Pre=Join-Path $ReportRoot "BUILD_0043_PREFLIGHT.json"; $Dry=Join-Path $ReportRoot "BUILD_0043_DRY_RUN.json"; $Apply=Join-Path $ReportRoot "BUILD_0043_APPLY.json"
 & (Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0043_Preflight.ps1") -Package $Package -Report $Pre
 & (Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0043_Import.ps1") -Package $Package -Repository $Repository -Report $Dry
 $D=Get-Content -LiteralPath $Dry -Raw|ConvertFrom-Json; if($D.valid -ne $true -or $D.transaction_status -ne "DRY_RUN_VALIDATED"){throw "Dry-run did not validate."}
 $Confirm=Read-Host "Review the dry-run report. Type APPLY to continue"; if($Confirm -cne "APPLY"){Write-Host "Stopped after dry-run. No repository changes were applied." -ForegroundColor Yellow; return}
 $OneDrive=Stop-OneDriveSafely
 & (Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0043_Import.ps1") -Package $Package -Repository $Repository -Report $Apply -BackupRoot $BackupRoot -Apply
 $A=Get-Content -LiteralPath $Apply -Raw|ConvertFrom-Json; if($A.valid -ne $true -or $A.applied -ne $true){throw "Apply did not validate."}
 $Python=Get-Command python -ErrorAction SilentlyContinue; if($null -eq $Python){$Python=Get-Command py -ErrorAction SilentlyContinue}; if($null -eq $Python){throw "Python not found."}
 & $Python.Source -B (Join-Path $Repository "13_Project_Genesis\Validators\validate_build_0043_retatrutide_patient_journey_ai.py") $Repository --report (Join-Path $ReportRoot "BUILD_0043_VALIDATOR.json"); Assert-Exit "Build 0043 validator"
 & $Python.Source -B -m unittest discover -s (Join-Path $Repository "13_Project_Genesis\Tests") -p "test_build_0043_retatrutide_patient_journey_ai.py"; Assert-Exit "Build 0043 tests"
 $Artifacts=@(Get-ChildItem -LiteralPath $Repository -Recurse -Force -ErrorAction SilentlyContinue|Where-Object{$_.Name -eq "__pycache__" -or $_.Extension -eq ".pyc" -or $_.Extension -eq ".pyo" -or $_.Name -match "^(GUIDED_DRY_RUN_REPORT|GUIDED_DRY_RUN_EXECUTIVE_SUMMARY).*\.json$"}); if($Artifacts.Count -gt 0){throw "Runtime artefacts detected."}
 $Deleted=@(git -C $Repository status --short --untracked-files|Where-Object{$_ -match "^\s*D|^D"}); Assert-Exit "Deletion check"; if($Deleted.Count -gt 0){throw "Unexpected deletions detected."}
 git -C $Repository add -A; Assert-Exit "Git stage"; git -C $Repository diff --check; Assert-Exit "git diff --check"; git -C $Repository diff --cached --check; Assert-Exit "git diff --cached --check"
 $Unstaged=@(git -C $Repository diff --name-only); Assert-Exit "Unstaged check"; if($Unstaged.Count -gt 0){throw "Unstaged changes remain."}
 git -C $Repository status --short --untracked-files
 $Commit=Read-Host "Review staged changes. Type COMMIT to commit and push"; if($Commit -cne "COMMIT"){Write-Host "Applied and staged, but not committed or pushed." -ForegroundColor Yellow; Write-Host $CommitMessage; return}
 git -C $Repository commit -m $CommitMessage; Assert-Exit "Git commit"; git -C $Repository push origin main; Assert-Exit "Git push"
 Write-Host "BUILD 0043 COMMITTED AND PUSHED" -ForegroundColor Green
 Write-Host "Next gate: confirm GitHub Actions green, complete lessons learned, and record ACTIONS_GREEN_CLOSED."
}
catch { Write-Host "BUILD 0043 STOPPED - FAIL-CLOSED" -ForegroundColor Red; Write-Host $_.Exception.Message -ForegroundColor Red; throw }
finally { if($Extract -and (Test-Path -LiteralPath $Extract)){Remove-Item -LiteralPath $Extract -Recurse -Force -ErrorAction SilentlyContinue}; Start-OneDriveIfRequired -State $OneDrive }
