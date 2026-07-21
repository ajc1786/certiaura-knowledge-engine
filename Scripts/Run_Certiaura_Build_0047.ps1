[CmdletBinding()]
param(
    [string]$Repository = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
    [string]$BackupRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Backups",
    [string]$ReportRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0047"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$BuildNumber = "0047"
$PriorBuild = "0046"
$CommitMessage = "Add Certiaura Build 0047 retatrutide controlled longitudinal dashboard, alert review workflow and clinician export baseline"
$PriorCommitMessage = "Add Certiaura Build 0046 retatrutide evidence-linked longitudinal analytics, outcome trend visualisation and controlled alerting baseline"
$PackageNameHint = "Certiaura_Build_0047_Retatrutide_Dashboard_Clinician_Export_RC7.zip"
$ExpectedAssetIntentManifestSha256 = "2D29E3515A076BA02B330BAB2A5AD2B42F0120EB08353753C529322E163E3841"

function Write-Step([string]$Message) { Write-Host ""; Write-Host ("=== " + $Message + " ===") -ForegroundColor Cyan }
function Assert-Exit([string]$Action) { if ($LASTEXITCODE -ne 0) { throw "$Action failed with exit code $LASTEXITCODE." } }
function Resolve-Python {
    $Command = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $Command) { $Command = Get-Command py -ErrorAction SilentlyContinue }
    if ($null -eq $Command) { throw "Python was not found on PATH." }
    return $Command.Source
}
function Resolve-Package([string]$ExpectedManifestSha256, [string]$RegressionReportRoot) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $Roots = @(@(
        (Get-Location).Path,
        (Join-Path $env:USERPROFILE "Downloads"),
        (Join-Path $env:USERPROFILE "Dropbox\PC\Downloads"),
        (Join-Path $env:USERPROFILE "OneDrive\Documents\CERTIAURA\Builds")
    ) | Where-Object {
        $_ -and (Test-Path -LiteralPath $_ -PathType Container)
    } | Select-Object -Unique)

    $Matches = New-Object System.Collections.Generic.List[object]
    foreach ($Root in $Roots) {
        $Candidates = @(
            Get-ChildItem `
                -LiteralPath $Root `
                -Filter "Certiaura_Build_0047_Retatrutide_Dashboard_Clinician_Export*.zip" `
                -File `
                -ErrorAction SilentlyContinue
        )
        foreach ($Candidate in $Candidates) {
            $Archive = $null
            try {
                $Archive = [System.IO.Compression.ZipFile]::OpenRead($Candidate.FullName)
                $Entry = $Archive.GetEntry(
                    "Documentation/Build_Records/0047/ASSET_INTENT_MANIFEST.json"
                )
                if ($null -eq $Entry) {
                    continue
                }
                $Stream = $Entry.Open()
                try {
                    $Hasher = [System.Security.Cryptography.SHA256]::Create()
                    try {
                        $HashBytes = $Hasher.ComputeHash($Stream)
                    }
                    finally {
                        $Hasher.Dispose()
                    }
                    $ManifestHash = (
                        [System.BitConverter]::ToString($HashBytes)
                    ).Replace("-", "")
                    if ($ManifestHash -eq $ExpectedManifestSha256) {
                        $PackageHash = (
                            Get-FileHash `
                                -LiteralPath $Candidate.FullName `
                                -Algorithm SHA256
                        ).Hash.Trim().ToUpperInvariant()
                        $Matches.Add([pscustomobject]@{
                            File = $Candidate
                            PackageSha256 = $PackageHash
                        })
                    }
                }
                finally {
                    $Stream.Dispose()
                }
            }
            catch {
            }
            finally {
                if ($null -ne $Archive) {
                    $Archive.Dispose()
                }
            }
        }
    }

    if ($Matches.Count -eq 0) {
        throw "No Build 0047 ZIP matches Asset Intent Manifest SHA-256 $ExpectedManifestSha256. Place $PackageNameHint in Downloads and rerun."
    }

    $DistinctPackageHashes = @(
        $Matches |
        Group-Object -Property PackageSha256
    )

    $ApprovedMatches = [object[]]$Matches.ToArray()
    if ($DistinctPackageHashes.Count -gt 1) {
        $PreReleaseRoot = Join-Path $RegressionReportRoot "Pre_Release"
        $RegressionReports = @(
            Get-ChildItem `
                -LiteralPath $PreReleaseRoot `
                -File `
                -Filter "BUILD_0047_WINDOWS_PS51_REGRESSION_*.json" `
                -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending
        )
        if ($RegressionReports.Count -eq 0) {
            throw "Multiple distinct Build 0047 packages were found and no Windows PowerShell 5.1 PASS report identifies the approved package."
        }
        $LatestRegression = Get-Content `
            -LiteralPath $RegressionReports[0].FullName `
            -Raw |
            ConvertFrom-Json
        if ($LatestRegression.status -ne "PASS") {
            throw "Multiple distinct Build 0047 packages were found and the latest Windows PowerShell 5.1 regression report is not PASS."
        }
        $ApprovedPackageHash = (
            [string]$LatestRegression.package_sha256
        ).Trim().ToUpperInvariant()
        $ApprovedMatches = @(
            $Matches |
            Where-Object {
                [string]::Equals(
                    $_.PackageSha256,
                    $ApprovedPackageHash,
                    [System.StringComparison]::OrdinalIgnoreCase
                )
            }
        )
        if ($ApprovedMatches.Count -eq 0) {
            throw "The latest passed Build 0047 regression report does not match any available Build 0047 package."
        }
        Write-Warning (
            "Multiple Build 0047 package revisions were found. " +
            "Using the package approved by: $($RegressionReports[0].FullName)"
        )
    }

    $OrderedMatches = @(
        $ApprovedMatches |
        Sort-Object `
            @{ Expression = { $_.File.LastWriteTimeUtc }; Descending = $true }, `
            @{ Expression = { $_.File.FullName }; Descending = $false }
    )
    $Selected = $OrderedMatches[0]

    if ($ApprovedMatches.Count -gt 1) {
        Write-Warning (
            "Found $($ApprovedMatches.Count) byte-identical copies of the approved Build 0047 package. " +
            "Using: $($Selected.File.FullName)"
        )
    }

    return $Selected.File.FullName
}
function Stop-OneDriveSafely {
    $State = [ordered]@{ WasRunning = $false; Executable = $null }
    $Processes = @(Get-Process -Name OneDrive -ErrorAction SilentlyContinue)
    if ($Processes.Count -gt 0) {
        $State.WasRunning = $true
        try { $State.Executable = $Processes[0].Path } catch { }
        $Processes | Stop-Process -Force
        Start-Sleep -Seconds 2
        if (@(Get-Process -Name OneDrive -ErrorAction SilentlyContinue).Count -gt 0) { throw "OneDrive could not be stopped." }
    }
    return [pscustomobject]$State
}
function Start-OneDriveIfRequired($State) {
    if (-not $State.WasRunning) { return }
    $Candidates = @(@($State.Executable, (Join-Path $env:LOCALAPPDATA "Microsoft\OneDrive\OneDrive.exe"), (Join-Path $env:ProgramFiles "Microsoft OneDrive\OneDrive.exe"), (Join-Path ${env:ProgramFiles(x86)} "Microsoft OneDrive\OneDrive.exe")) |
        Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Leaf) } | Select-Object -Unique)
    if ($Candidates.Count -gt 0) { Start-Process -FilePath $Candidates[0] | Out-Null }
    else { Write-Warning "OneDrive was running but its executable could not be resolved for restart." }
}

$OneDriveState = [pscustomobject]@{ WasRunning = $false; Executable = $null }
$TempRoot = $null
$ApplyCompleted = $false
$CommitCompleted = $false
$RollbackHelper = $null
$RollbackReport = $null
$ApplyReport = $null
try {
    Write-Step "Resolve package and calculate SHA-256"
    $Package = Resolve-Package `
        -ExpectedManifestSha256 $ExpectedAssetIntentManifestSha256 `
        -RegressionReportRoot $ReportRoot
    $PackageSha256 = (Get-FileHash -LiteralPath $Package -Algorithm SHA256).Hash
    Write-Host "Package: $Package"
    Write-Host "Package SHA-256: $PackageSha256"

    Write-Step "Verify clean canonical repository and Build 0046 closure"
    if (-not (Test-Path -LiteralPath (Join-Path $Repository ".git") -PathType Container)) { throw "Repository is not a Git working tree." }
    $Dirty = @(git -C $Repository status --porcelain --untracked-files=all)
    Assert-Exit "Git status"
    if ($Dirty.Count -gt 0) { throw "Repository is not clean." }
    git -C $Repository fetch origin
    Assert-Exit "Git fetch"
    git -C $Repository pull --ff-only
    Assert-Exit "Git pull"
    $ClosureCandidates = @(@(
        (Join-Path $Repository "Documentation\Build_Records\0046\CLOSURE_RECORD.json"),
        (Join-Path $Repository "Documentation\Build_Records\0046\PACKAGE_VERSION.json"),
        (Join-Path $Repository "Documentation\Build_Records\0046\CONTINUITY_CHECKPOINT_DELTA.json"),
        (Join-Path $Repository "Documentation\Build_Records\0046\PRODUCTION_DASHBOARD_UPDATE.json"),
        (Join-Path $Repository "Documentation\Build_Records\0046\LESSONS_LEARNED_REVIEW.md"),
        (Join-Path $Repository "Documentation\Build_Records\0046\BUILD_MANIFEST.json")
    ) | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf })
    if ($ClosureCandidates.Count -eq 0) { throw "No Build 0046 checkpoint record was found." }
    $ClosureText = ($ClosureCandidates | ForEach-Object { Get-Content -LiteralPath $_ -Raw }) -join "`n"
    if ($ClosureText -notmatch "ACTIONS_GREEN_CLOSED") { throw "Build 0046 is not evidenced as ACTIONS_GREEN_CLOSED." }
    $ExpectedHead = (git -C $Repository rev-parse HEAD).Trim()
    Assert-Exit "Read repository HEAD"
    $PriorCommitMatches = @(
        git -C $Repository log --format="%H%x09%s" --all |
        ForEach-Object {
            $Parts = @($_ -split "`t", 2)
            if ($Parts.Count -eq 2 -and $Parts[1] -ceq $PriorCommitMessage) {
                $Parts[0]
            }
        }
    )
    Assert-Exit "Resolve exact Build 0046 implementation commit"
    if ($PriorCommitMatches.Count -ne 1) {
        throw "Expected exactly one exact Build 0046 implementation commit; found $($PriorCommitMatches.Count)."
    }
    $PriorCommit = $PriorCommitMatches[0]
    git -C $Repository merge-base --is-ancestor $PriorCommit $ExpectedHead
    Assert-Exit "Verify Build 0046 implementation ancestry"
    Write-Host "Verified prior checkpoint HEAD: $ExpectedHead"
    Write-Host "Verified Build 0046 implementation commit: $PriorCommit"

    $PreReleaseRoot = Join-Path $ReportRoot "Pre_Release"
    $RegressionReports = @(
        Get-ChildItem `
            -LiteralPath $PreReleaseRoot `
            -File `
            -Filter "BUILD_0047_WINDOWS_PS51_REGRESSION_*.json" `
            -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending
    )
    if ($RegressionReports.Count -eq 0) {
        throw "No passed Build 0047 Windows PowerShell 5.1 pre-release regression report was found."
    }
    $RegressionResult = Get-Content -LiteralPath $RegressionReports[0].FullName -Raw | ConvertFrom-Json
    if ($RegressionResult.status -ne "PASS") {
        throw "The latest Build 0047 Windows PowerShell 5.1 regression report is not PASS."
    }
    if (-not [string]::Equals(
        [string]$RegressionResult.package_sha256,
        $PackageSha256,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "The passed Build 0047 regression report does not match the selected package SHA-256."
    }
    Write-Host "Verified pre-release regression report: $($RegressionReports[0].FullName)"

    New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
    $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $PreflightReport = Join-Path $ReportRoot "BUILD_0047_PREFLIGHT_$Stamp.json"
    $DryRunReport = Join-Path $ReportRoot "BUILD_0047_DRY_RUN_$Stamp.json"
    $ApplyReport = Join-Path $ReportRoot "BUILD_0047_APPLY_$Stamp.json"
    $ValidatorReport = Join-Path $ReportRoot "BUILD_0047_VALIDATOR_$Stamp.json"
    $RollbackReport = Join-Path $ReportRoot "BUILD_0047_ROLLBACK_$Stamp.json"

    Write-Step "Extract controlled launchers"
    $TempRoot = Join-Path $env:TEMP ("Certiaura_0047_QuickRun_" + [guid]::NewGuid().ToString("N"))
    Expand-Archive -LiteralPath $Package -DestinationPath $TempRoot -Force
    $Preflight = Join-Path $TempRoot "Scripts\Invoke_Certiaura_Build_0047_Preflight.ps1"
    $Importer = Join-Path $TempRoot "Scripts\Invoke_Certiaura_Build_0047_Import.ps1"
    $RollbackHelper = Join-Path $TempRoot "13_Project_Genesis\Import\rollback_build_0047_pending_import.py"
    foreach ($Required in @($Preflight, $Importer, $RollbackHelper)) { if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) { throw "Missing launcher: $Required" } }

    Write-Step "Run package preflight"
    & $Preflight -Package $Package -Report $PreflightReport
    if ($LASTEXITCODE -ne 0) { throw "Build 0047 preflight failed." }

    Write-Step "Run Project Genesis dry-run"
    & $Importer -Repository $Repository -Package $Package -Report $DryRunReport
    if ($LASTEXITCODE -ne 0) { throw "Build 0047 dry-run failed." }
    $DryRun = Get-Content -LiteralPath $DryRunReport -Raw | ConvertFrom-Json
    if (-not [bool]$DryRun.valid -or $DryRun.transaction_status -ne "DRY_RUN_VALIDATED") { throw "Dry-run report is not valid." }
    Write-Host "Dry-run validated. Formal assets: $(@($DryRun.register_changes).Count)" -ForegroundColor Green

    $ApplyConfirmation = Read-Host "Review the dry-run report. Type APPLY to perform the transactional import"
    if ($ApplyConfirmation -cne "APPLY") { Write-Host "Stopped after dry-run. No repository files were changed." -ForegroundColor Yellow; return }

    Write-Step "Stop OneDrive for controlled writes"
    $OneDriveState = Stop-OneDriveSafely

    Write-Step "Apply transaction with backup outside repository"
    & $Importer -Repository $Repository -Package $Package -Report $ApplyReport -BackupRoot $BackupRoot -Apply
    if ($LASTEXITCODE -ne 0) { throw "Build 0047 apply failed." }
    $ApplyResult = Get-Content -LiteralPath $ApplyReport -Raw | ConvertFrom-Json
    if (-not [bool]$ApplyResult.valid -or -not [bool]$ApplyResult.applied) { throw "Apply report is not valid." }
    Write-Host "Backup: $($ApplyResult.backup_path)"
    $ApplyCompleted = $true

    Write-Step "Run Build 0047 validator and tests"
    $Python = Resolve-Python
    $env:PYTHONDONTWRITEBYTECODE = "1"
    & $Python -B (Join-Path $Repository "13_Project_Genesis\Validators\validate_retatrutide_longitudinal_dashboard.py") $Repository --report $ValidatorReport
    Assert-Exit "Build 0047 validator"
    $TestRoot = Join-Path $Repository "13_Project_Genesis\Tests"
    & $Python -B -m unittest discover -s $TestRoot -p "test_build_0047_retatrutide_dashboard.py"
    Assert-Exit "Build 0047 regression tests"

    Write-Step "Check runtime artefacts and Git hygiene"
    $Runtime = @(Get-ChildItem -LiteralPath $Repository -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -in @("__pycache__", ".pytest_cache", ".mypy_cache") -or $_.Extension -in @(".pyc", ".pyo") })
    if ($Runtime.Count -gt 0) { throw "Runtime artefacts detected." }
    $Deleted = @(git -C $Repository status --short --untracked-files=all | Where-Object { $_ -match "^\s*D|^D" })
    Assert-Exit "Git deletion check"
    if ($Deleted.Count -gt 0) { throw "Unexpected deletions detected." }
    git -C $Repository add -A
    Assert-Exit "Git stage"
    git -C $Repository diff --check
    Assert-Exit "git diff --check"
    git -C $Repository diff --cached --check
    Assert-Exit "git diff --cached --check"
    $Unstaged = @(git -C $Repository diff --name-only)
    Assert-Exit "Unstaged change check"
    if ($Unstaged.Count -gt 0) { throw "Unstaged changes remain." }
    git -C $Repository status --short --untracked-files=all
    Assert-Exit "Final Git status"

    $CommitConfirmation = Read-Host "Type COMMIT to commit and push using the locked message"
    if ($CommitConfirmation -cne "COMMIT") { Write-Host "Build 0047 is staged but not committed." -ForegroundColor Yellow; Write-Host $CommitMessage; return }
    git -C $Repository commit -m $CommitMessage
    Assert-Exit "Git commit"
    $CommitCompleted = $true
    git -C $Repository push origin main
    Assert-Exit "Git push"
    Write-Host "BUILD 0047 COMMITTED AND PUSHED" -ForegroundColor Green
    Write-Host "Next gate: confirm GitHub Actions green and record ACTIONS_GREEN_CLOSED."
}
catch {
    $OriginalError = $_
    if ($ApplyCompleted -and -not $CommitCompleted) {
        Write-Step "Rollback post-apply transaction"
        try {
            if (-not $RollbackHelper -or -not (Test-Path -LiteralPath $RollbackHelper -PathType Leaf)) {
                throw "Build 0047 rollback helper is unavailable."
            }
            if (-not $ApplyReport -or -not (Test-Path -LiteralPath $ApplyReport -PathType Leaf)) {
                throw "Build 0047 apply report is unavailable for rollback."
            }
            $RollbackPython = Resolve-Python
            & $RollbackPython -B $RollbackHelper `
                --repository $Repository `
                --apply-report $ApplyReport `
                --rollback-report $RollbackReport `
                --expected-package-sha256 $PackageSha256
            if ($LASTEXITCODE -ne 0) {
                throw "Build 0047 post-apply rollback failed with exit code $LASTEXITCODE."
            }
            $RollbackResult = Get-Content -LiteralPath $RollbackReport -Raw | ConvertFrom-Json
            if (-not [bool]$RollbackResult.valid -or $RollbackResult.status -ne "ROLLED_BACK_CLEAN") {
                throw "Build 0047 rollback report is not clean."
            }
            $ApplyCompleted = $false
            Write-Host "BUILD 0047 POST-APPLY ROLLBACK: PASS" -ForegroundColor Green
            Write-Host "Rollback report: $RollbackReport"
        }
        catch {
            Write-Host "BUILD 0047 POST-APPLY ROLLBACK: FAILED" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
            Write-Host "External backup and apply report have been retained for controlled recovery." -ForegroundColor Yellow
        }
    }
    Write-Host "BUILD 0047 STOPPED - FAIL-CLOSED" -ForegroundColor Red
    Write-Host $OriginalError.Exception.Message -ForegroundColor Red
    throw $OriginalError
}
finally {
    if ($TempRoot -and (Test-Path -LiteralPath $TempRoot)) { Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue }
    Start-OneDriveIfRequired -State $OneDriveState
}
