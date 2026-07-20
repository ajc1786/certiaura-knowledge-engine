[CmdletBinding()]
param(
    [string]$ExpectedPackageSha256 = "",
    [string]$Repository = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
    [string]$BackupRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Backups",
    [string]$ReportRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0041"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$BuildNumber = "0041"
$ExpectedHead = "6f4dfb11dfdc4b28fe736972864ec1acf1a1e056"
$CommitMessage = "Add Certiaura Build 0041 retatrutide evidence corpus citation graph and scientific review baseline"

function Write-Step([string]$Message) {
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Assert-LastExitCode([string]$Action) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Action failed with exit code $LASTEXITCODE."
    }
}

function Resolve-Python {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue }
    if ($null -eq $Python) { throw "Python was not found on PATH." }
    return $Python.Source
}

function Resolve-ExpectedPackageSha256([string]$SuppliedSha256) {
    $Value = [string]$SuppliedSha256
    if ([string]::IsNullOrWhiteSpace($Value)) {
        $ShaFile = Join-Path $PSScriptRoot "BUILD_PACKAGE.sha256"
        if (-not (Test-Path -LiteralPath $ShaFile -PathType Leaf)) {
            throw "BUILD_PACKAGE.sha256 is missing beside the launcher."
        }
        $FirstLine = [string](Get-Content -LiteralPath $ShaFile -TotalCount 1)
        $Parts = @($FirstLine -split "\s+")
        $Value = [string]($Parts | Select-Object -First 1)
    }
    $Value = $Value.Trim().ToUpperInvariant()
    if ($Value -notmatch "^[A-F0-9]{64}$") {
        throw "The expected package SHA-256 is missing or invalid."
    }
    return $Value
}

function Resolve-PackageBesideLauncher([string]$ExpectedSha256) {
    $Matches = New-Object System.Collections.Generic.List[string]
    $ZipFiles = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter "*.zip" -File -ErrorAction Stop)
    foreach ($ZipFile in $ZipFiles) {
        $Hash = (Get-FileHash -LiteralPath $ZipFile.FullName -Algorithm SHA256).Hash.ToUpperInvariant()
        if ($Hash -eq $ExpectedSha256) {
            $Matches.Add([string]$ZipFile.FullName)
        }
    }
    if ($Matches.Count -ne 1) {
        throw "Expected exactly one inner build ZIP beside the launcher matching SHA-256 $ExpectedSha256; found $($Matches.Count). Delete the old extracted folder, extract the latest bundle into a new empty folder, and rerun START_BUILD_0041.cmd."
    }
    return [string]($Matches | Select-Object -First 1)
}

function Resolve-OneDriveExecutable([string]$PreferredPath) {
    $CandidatePaths = @(
        $PreferredPath,
        (Join-Path $env:LOCALAPPDATA "Microsoft\OneDrive\OneDrive.exe"),
        (Join-Path $env:ProgramFiles "Microsoft OneDrive\OneDrive.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Microsoft OneDrive\OneDrive.exe")
    )
    foreach ($Candidate in $CandidatePaths) {
        $CandidatePath = [string]$Candidate
        if ([string]::IsNullOrWhiteSpace($CandidatePath)) { continue }
        if (Test-Path -LiteralPath $CandidatePath -PathType Leaf) {
            return $CandidatePath
        }
    }
    return $null
}

function Stop-OneDriveSafely {
    $State = [ordered]@{ WasRunning = $false; Executable = $null }
    $Processes = @(Get-Process -Name "OneDrive" -ErrorAction SilentlyContinue)
    if ($Processes.Count -gt 0) {
        $State.WasRunning = $true
        foreach ($Process in $Processes) {
            try {
                $ProcessPath = [string]$Process.Path
                if (-not [string]::IsNullOrWhiteSpace($ProcessPath)) {
                    $State.Executable = $ProcessPath
                    break
                }
            } catch { }
        }
        $Processes | Stop-Process -Force
        Start-Sleep -Seconds 2
        if (Get-Process -Name "OneDrive" -ErrorAction SilentlyContinue) {
            throw "OneDrive could not be stopped. Stop it manually and rerun the starter."
        }
    }
    return [pscustomobject]$State
}

function Start-OneDriveIfRequired($State) {
    if (-not $State.WasRunning) { return }
    $OneDrivePath = Resolve-OneDriveExecutable -PreferredPath ([string]$State.Executable)
    if ([string]::IsNullOrWhiteSpace([string]$OneDrivePath)) {
        Write-Warning "OneDrive was running before the build but its executable could not be located for restart. Restart OneDrive manually."
        return
    }
    Write-Host "Restarting OneDrive: $OneDrivePath"
    Start-Process -FilePath ([string]$OneDrivePath) -ErrorAction Stop | Out-Null
    Start-Sleep -Seconds 5
    if (-not (Get-Process -Name "OneDrive" -ErrorAction SilentlyContinue)) {
        Write-Warning "OneDrive did not confirm as running. Restart OneDrive manually."
    }
}

$PackageSha256 = Resolve-ExpectedPackageSha256 -SuppliedSha256 $ExpectedPackageSha256
$TempRoot = $null
$OneDriveState = [pscustomobject]@{ WasRunning = $false; Executable = $null }

try {
    Write-Step "Resolve the bundled package by SHA-256"
    $Package = Resolve-PackageBesideLauncher -ExpectedSha256 $PackageSha256
    Write-Host "Package: $Package"
    Write-Host "Verified package SHA-256: $PackageSha256"

    Write-Step "Verify repository checkpoint"
    if (-not (Test-Path -LiteralPath (Join-Path $Repository ".git") -PathType Container)) {
        throw "Repository is not a Git repository: $Repository"
    }

    git -C $Repository status --porcelain --untracked-files=all
    Assert-LastExitCode "Git status"
    $Dirty = @(git -C $Repository status --porcelain --untracked-files=all)
    Assert-LastExitCode "Git clean-status check"
    if ($Dirty.Count -gt 0) { throw "Repository is not clean. Resolve all changes before importing Build $BuildNumber." }

    git -C $Repository fetch origin
    Assert-LastExitCode "Git fetch"
    git -C $Repository pull --ff-only
    Assert-LastExitCode "Git pull --ff-only"

    $Head = (git -C $Repository rev-parse HEAD).Trim()
    Assert-LastExitCode "Read repository HEAD"
    if ($Head -ne $ExpectedHead) {
        throw "Expected Build 0040 checkpoint $ExpectedHead but repository HEAD is $Head. Do not continue until the checkpoint is explicitly reconciled."
    }

    New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $PreflightReport = Join-Path $ReportRoot "BUILD_0041_PREFLIGHT_$Timestamp.json"
    $DryRunReport = Join-Path $ReportRoot "BUILD_0041_DRY_RUN_$Timestamp.json"
    $ApplyReport = Join-Path $ReportRoot "BUILD_0041_APPLY_$Timestamp.json"
    $ValidatorReport = Join-Path $ReportRoot "BUILD_0041_VALIDATOR_$Timestamp.json"

    Write-Step "Extract controlled launchers"
    $TempRoot = Join-Path $env:TEMP ("Certiaura_0041_QuickRun_" + [guid]::NewGuid().ToString("N"))
    Expand-Archive -LiteralPath $Package -DestinationPath $TempRoot -Force

    $PreflightScript = Join-Path $TempRoot "Scripts\Invoke_Certiaura_Build_0041_Preflight.ps1"
    $ImportScript = Join-Path $TempRoot "Scripts\Invoke_Certiaura_Build_0041_Import.ps1"
    foreach ($Required in @($PreflightScript, $ImportScript)) {
        if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) { throw "Required package launcher is missing: $Required" }
    }

    Write-Step "Run package preflight"
    & $PreflightScript -Package $Package -Report $PreflightReport
    if (-not (Test-Path -LiteralPath $PreflightReport -PathType Leaf)) { throw "Build 0041 preflight report was not produced." }

    Write-Step "Run Project Genesis dry-run"
    & $ImportScript -Repository $Repository -Package $Package -PackageSha256 $PackageSha256 -Report $DryRunReport
    if (-not (Test-Path -LiteralPath $DryRunReport -PathType Leaf)) { throw "Build 0041 dry-run report was not produced." }

    $DryRun = Get-Content -LiteralPath $DryRunReport -Raw | ConvertFrom-Json
    if (-not $DryRun.valid -or $DryRun.transaction_status -ne "DRY_RUN_VALIDATED") {
        throw "Dry-run report is not valid. Review $DryRunReport"
    }

    Write-Host "Dry-run validated." -ForegroundColor Green
    Write-Host "Package files: $($DryRun.package_file_count)"
    Write-Host "Formal assets: $($DryRun.formal_asset_count)"
    Write-Host "Expected register total: $($DryRun.expected_register_total)"
    Write-Host "Proposed identifiers: $(@($DryRun.allocated_identifiers).Count)"
    Write-Host "Dry-run report: $DryRunReport"

    $ApplyConfirmation = Read-Host "Review the dry-run report. Type APPLY to perform the transactional import"
    if ($ApplyConfirmation -cne "APPLY") {
        Write-Host "Stopped after successful dry-run. No repository files were changed." -ForegroundColor Yellow
        return
    }

    Write-Step "Stop OneDrive for controlled repository writes"
    $OneDriveState = Stop-OneDriveSafely

    Write-Step "Apply Build 0041 transactionally"
    & $ImportScript -Repository $Repository -Package $Package -PackageSha256 $PackageSha256 -Report $ApplyReport -BackupRoot $BackupRoot -Apply
    if (-not (Test-Path -LiteralPath $ApplyReport -PathType Leaf)) { throw "Build 0041 apply report was not produced." }

    $ApplyResult = Get-Content -LiteralPath $ApplyReport -Raw | ConvertFrom-Json
    if (-not $ApplyResult.valid -or -not $ApplyResult.applied) {
        throw "Apply report is not valid. Review $ApplyReport"
    }
    Write-Host "Transactional import applied." -ForegroundColor Green
    Write-Host "Backup: $($ApplyResult.backup_path)"

    Write-Step "Run scientific validator and regression tests"
    $Python = Resolve-Python
    & $Python -B (Join-Path $Repository "13_Project_Genesis\Validators\validate_retatrutide_evidence_corpus.py") $Repository --report $ValidatorReport
    Assert-LastExitCode "Retatrutide evidence validator"

    $TestsPath = Join-Path $Repository "13_Project_Genesis\Tests"
    & $Python -B -m unittest discover -s $TestsPath -p "test_build_0041_*.py"
    Assert-LastExitCode "Build 0041 regression tests"

    Write-Step "Check runtime artefacts and repository hygiene"
    $RuntimeArtefacts = @(Get-ChildItem -LiteralPath $Repository -Recurse -Force -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -in @("__pycache__") -or $_.Extension -in @(".pyc", ".pyo") -or $_.Name -match "^(GUIDED_DRY_RUN_REPORT|GUIDED_DRY_RUN_EXECUTIVE_SUMMARY).*\.json$"
    })
    if ($RuntimeArtefacts.Count -gt 0) {
        $RuntimeArtefacts.FullName | ForEach-Object { Write-Host $_ -ForegroundColor Red }
        throw "Runtime artefacts were detected. Remove them before staging."
    }

    $Deleted = @(git -C $Repository status --short --untracked-files=all | Where-Object { $_ -match "^\s*D|^D" })
    Assert-LastExitCode "Git deletion check"
    if ($Deleted.Count -gt 0) {
        $Deleted | ForEach-Object { Write-Host $_ -ForegroundColor Red }
        throw "Unexpected deletions detected. Import is blocked."
    }

    Write-Step "Stage and run mandatory Git checks"
    git -C $Repository add -A
    Assert-LastExitCode "Git stage"

    git -C $Repository diff --check
    Assert-LastExitCode "git diff --check"

    git -C $Repository diff --cached --check
    Assert-LastExitCode "git diff --cached --check"

    $Unstaged = @(git -C $Repository diff --name-only)
    Assert-LastExitCode "Unstaged change check"
    if ($Unstaged.Count -gt 0) {
        $Unstaged | ForEach-Object { Write-Host $_ -ForegroundColor Red }
        throw "Unstaged changes remain after staging."
    }

    Write-Host "`nStaged Build 0041 changes:" -ForegroundColor Cyan
    git -C $Repository status --short --untracked-files=all
    Assert-LastExitCode "Final Git status"

    $CommitConfirmation = Read-Host "Review the staged changes. Type COMMIT to commit and push using the locked message"
    if ($CommitConfirmation -cne "COMMIT") {
        Write-Host "Build 0041 is applied and staged but not committed or pushed." -ForegroundColor Yellow
        Write-Host "Commit message: $CommitMessage"
        return
    }

    Write-Step "Commit and push Build 0041"
    git -C $Repository commit -m $CommitMessage
    Assert-LastExitCode "Git commit"

    git -C $Repository push origin main
    Assert-LastExitCode "Git push"

    $NewHead = (git -C $Repository rev-parse HEAD).Trim()
    Assert-LastExitCode "Read committed HEAD"

    Write-Host "`nBUILD 0041 COMMITTED AND PUSHED" -ForegroundColor Green
    Write-Host "Commit: $NewHead"
    Write-Host "Next gate: confirm GitHub Actions green, verify the Build 0041 lessons-learned record, then record ACTIONS_GREEN_CLOSED."
    Write-Host "Reports: $ReportRoot"
}
catch {
    Write-Host "`nBUILD 0041 STOPPED - FAIL-CLOSED" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    throw
}
finally {
    if ($TempRoot -and (Test-Path -LiteralPath $TempRoot)) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    Start-OneDriveIfRequired -State $OneDriveState
}
