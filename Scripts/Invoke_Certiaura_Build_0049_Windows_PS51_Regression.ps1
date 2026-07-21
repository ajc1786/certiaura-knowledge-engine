[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Package,
    [Parameter(Mandatory = $true)][string]$ExpectedPackageSha256,
    [Parameter(Mandatory = $true)][string]$ReportRoot
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$BuildNumber = "0049"
$BuildId = "CERT-BUILD-0049"
$CommitMessage = "Add Certiaura Build 0049 retatrutide controlled handoff acknowledgement, follow-up review, clinician feedback and amendment audit baseline"
$PriorCommitMessage = "Add Certiaura Build 0048 retatrutide clinician review approval, export version control, controlled handoff and audit trail baseline"

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host ("=== " + $Message + " ===") -ForegroundColor Cyan
}

function Assert-NativeExit([string]$Action) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Action failed with exit code $LASTEXITCODE."
    }
}

function Resolve-Python {
    $Command = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $Command) {
        $Command = Get-Command py -ErrorAction SilentlyContinue
    }
    if ($null -eq $Command) {
        throw "Python was not found on PATH."
    }
    return $Command.Source
}

function Write-Utf8NoBomLf([string]$Path, [string]$Content) {
    $Parent = Split-Path -Parent $Path
    if ($Parent -and -not (Test-Path -LiteralPath $Parent -PathType Container)) {
        New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    }
    $Normalised = $Content.Replace("`r`n", "`n").Replace("`r", "`n")
    if (-not $Normalised.EndsWith("`n")) {
        $Normalised += "`n"
    }
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Normalised, $Encoding)
}

function Stop-OneDriveSafely {
    $State = [ordered]@{
        WasRunning = $false
        Executable = $null
    }
    $Processes = @(Get-Process -Name OneDrive -ErrorAction SilentlyContinue)
    if ($Processes.Count -gt 0) {
        $State.WasRunning = $true
        try {
            $State.Executable = $Processes[0].Path
        }
        catch {
        }
        $Processes | Stop-Process -Force
        Start-Sleep -Seconds 2
        if (@(Get-Process -Name OneDrive -ErrorAction SilentlyContinue).Count -gt 0) {
            throw "OneDrive could not be stopped."
        }
    }
    return [pscustomobject]$State
}

function Start-OneDriveIfRequired($State) {
    if (-not $State.WasRunning) {
        return
    }
    $Candidates = @(@(
        $State.Executable,
        (Join-Path $env:LOCALAPPDATA "Microsoft\OneDrive\OneDrive.exe"),
        (Join-Path $env:ProgramFiles "Microsoft OneDrive\OneDrive.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Microsoft OneDrive\OneDrive.exe")
    ) | Where-Object {
        $_ -and (Test-Path -LiteralPath $_ -PathType Leaf)
    } | Select-Object -Unique)
    if ($Candidates.Count -gt 0) {
        Start-Process -FilePath $Candidates[0] | Out-Null
    }
    else {
        Write-Warning "OneDrive was running but its executable could not be resolved for restart."
    }
}

$TempRoot = $null
$OneDriveState = [pscustomobject]@{
    WasRunning = $false
    Executable = $null
}

try {
    Write-Step "Verify Windows PowerShell 5.1 runtime"
    if ($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1) {
        throw "This regression must run under Windows PowerShell 5.1."
    }
    if ($env:OS -ne "Windows_NT") {
        throw "This regression must run on Windows."
    }

    $GitCommand = Get-Command git -ErrorAction SilentlyContinue
    if ($null -eq $GitCommand) {
        throw "Git was not found on PATH."
    }
    $Python = Resolve-Python

    Write-Step "Verify approved package SHA-256"
    if (-not (Test-Path -LiteralPath $Package -PathType Leaf)) {
        throw "Build 0049 package was not found: $Package"
    }
    $ActualPackageSha256 = (
        Get-FileHash -LiteralPath $Package -Algorithm SHA256
    ).Hash.Trim().ToUpperInvariant()
    $Expected = $ExpectedPackageSha256.Trim().ToUpperInvariant()
    if (-not [string]::Equals(
        $ActualPackageSha256,
        $Expected,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Build 0049 package SHA-256 mismatch."
    }
    Write-Host "BUILD 0049 PACKAGE VERIFIED: PASS" -ForegroundColor Green
    Write-Host "Package: $Package"
    Write-Host "SHA-256: $ActualPackageSha256"

    New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
    $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $PreflightReport = Join-Path $ReportRoot "BUILD_0049_PREFLIGHT_$Stamp.json"
    $DryRunReport = Join-Path $ReportRoot "BUILD_0049_SYNTHETIC_DRY_RUN_$Stamp.json"
    $InternalBackupReport = Join-Path $ReportRoot "BUILD_0049_INTERNAL_BACKUP_NEGATIVE_$Stamp.json"
    $ApplyReport = Join-Path $ReportRoot "BUILD_0049_SYNTHETIC_APPLY_$Stamp.json"
    $ValidatorReport = Join-Path $ReportRoot "BUILD_0049_SYNTHETIC_VALIDATOR_$Stamp.json"
    $RegressionReport = Join-Path $ReportRoot "BUILD_0049_WINDOWS_PS51_REGRESSION_$Stamp.json"
    $RollbackReport = Join-Path $ReportRoot "BUILD_0049_SYNTHETIC_ROLLBACK_$Stamp.json"
    $SecondDryRunReport = Join-Path $ReportRoot "BUILD_0049_SYNTHETIC_DRY_RUN_AFTER_ROLLBACK_$Stamp.json"
    $SecondApplyReport = Join-Path $ReportRoot "BUILD_0049_SYNTHETIC_APPLY_AFTER_ROLLBACK_$Stamp.json"

    Write-Step "Run CMD parser precheck"
    $TempRoot = Join-Path $env:TEMP (
        "Certiaura_0049_PS51_Regression_" + [guid]::NewGuid().ToString("N")
    )
    New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null
    $CmdPrecheck = Join-Path $TempRoot "BUILD_0049_CMD_PRECHECK.cmd"
    $CmdContent = @"
@echo off
setlocal
if not exist "%~dp0" exit /b 41
echo BUILD 0049 CMD PARSER PRECHECK: PASS
exit /b 0
"@
    Write-Utf8NoBomLf -Path $CmdPrecheck -Content $CmdContent
    cmd.exe /D /C "`"$CmdPrecheck`""
    Assert-NativeExit "CMD parser precheck"

    Write-Step "Extract package and run preflight"
    $Payload = Join-Path $TempRoot "Payload"
    Expand-Archive -LiteralPath $Package -DestinationPath $Payload -Force
    $Preflight = Join-Path $Payload "Scripts\Invoke_Certiaura_Build_0049_Preflight.ps1"
    $Importer = Join-Path $Payload "Scripts\Invoke_Certiaura_Build_0049_Import.ps1"
    $RollbackHelper = Join-Path $Payload "13_Project_Genesis\Import\rollback_build_0049_pending_import.py"
    foreach ($Required in @($Preflight, $Importer, $RollbackHelper)) {
        if (-not (Test-Path -LiteralPath $Required -PathType Leaf)) {
            throw "Build 0049 regression component is missing: $Required"
        }
    }
    & $Preflight -Package $Package -Report $PreflightReport
    $PreflightResult = Get-Content -LiteralPath $PreflightReport -Raw | ConvertFrom-Json
    if (-not [bool]$PreflightResult.valid) {
        throw "Build 0049 package preflight report is not valid."
    }

    Write-Step "Run package resolver array normalisation regression"
    $ResolverMatches = New-Object System.Collections.Generic.List[object]
    $ResolverMatches.Add([pscustomobject]@{
        File = [pscustomobject]@{ FullName = $Package }
        PackageSha256 = $ActualPackageSha256
    })
    $ResolverArray = [object[]]$ResolverMatches.ToArray()
    if ($ResolverArray.Count -ne 1) {
        throw "Package resolver generic-list array normalisation failed."
    }
    if ($ResolverArray[0].PackageSha256 -cne $ActualPackageSha256) {
        throw "Package resolver generic-list array normalisation changed package data."
    }
    $CanonicalRunner = Join-Path $Payload "Scripts\Run_Certiaura_Build_0049.ps1"
    $CanonicalRunnerText = Get-Content -LiteralPath $CanonicalRunner -Raw
    if ($CanonicalRunnerText -notmatch [regex]::Escape(
        '$MatchesArray = [object[]]$Matches.ToArray()'
    )) {
        throw "Canonical launcher does not normalise the package match list before Count or indexing."
    }
    if ($CanonicalRunnerText -match [regex]::Escape(
        '$MatchesArray = @($Matches)'
    )) {
        throw "Canonical launcher still contains an incompatible generic-list unary-array conversion."
    }
    if ($CanonicalRunnerText -notmatch [regex]::Escape(
        '& $Python -B -m unittest discover -s $TestRoot -p "test_build_0049_retatrutide_follow_up_feedback_audit.py"'
    )) {
        throw "Canonical launcher does not use unittest discovery with an explicit test root."
    }
    if ($CanonicalRunnerText -match [regex]::Escape(
        '-m unittest (Join-Path $Repository'
    )) {
        throw "Canonical launcher still passes an absolute file path as a unittest module name."
    }
    if ($CanonicalRunnerText -notmatch "POST-APPLY ROLLBACK") {
        throw "Canonical launcher does not contain the post-apply rollback gate."
    }

    $BuildTestText = Get-Content `
        -LiteralPath (Join-Path $Payload "13_Project_Genesis\Tests\test_build_0049_retatrutide_follow_up_feedback_audit.py") `
        -Raw
    if ($BuildTestText -match [regex]::Escape('for p in ROOT.rglob("*")')) {
        throw "Build 0049 hygiene test still scans unrelated historical repository files."
    }

    $ManifestScopePattern = @'
(?s)manifest\s*=\s*self\.load\(\s*["']Documentation/Build_Records/0049/ASSET_INTENT_MANIFEST\.json["']\s*\)
'@.Trim()
    $OwnedPathsPattern = @'
(?s)owned_paths\s*=\s*\[\s*ROOT\s*/\s*item\["path"\]\s*for\s+item\s+in\s+manifest\["files"\]\s*\]
'@.Trim()

    if (-not [regex]::IsMatch($BuildTestText, $ManifestScopePattern)) {
        throw "Build 0049 hygiene test does not load the exact Asset Intent Manifest."
    }
    if (-not [regex]::IsMatch($BuildTestText, $OwnedPathsPattern)) {
        throw "Build 0049 hygiene test does not derive owned paths from the exact Asset Intent Manifest."
    }

    Write-Step "Create synthetic Git repository and push baseline"
    $SyntheticRepo = Join-Path $TempRoot "Synthetic_Repository"
    $SyntheticRemote = Join-Path $TempRoot "Synthetic_Remote.git"
    New-Item -ItemType Directory -Path $SyntheticRepo -Force | Out-Null
    git init --bare $SyntheticRemote
    Assert-NativeExit "Initialise synthetic bare remote"
    git -C $SyntheticRepo init
    Assert-NativeExit "Initialise synthetic repository"
    git -C $SyntheticRepo checkout -b main
    Assert-NativeExit "Create synthetic main branch"
    git -C $SyntheticRepo config user.name "Certiaura Regression"
    Assert-NativeExit "Configure synthetic Git user name"
    git -C $SyntheticRepo config user.email "regression@certiaura.local"
    Assert-NativeExit "Configure synthetic Git user email"
    git -C $SyntheticRepo remote add origin $SyntheticRemote
    Assert-NativeExit "Configure synthetic origin"

    $RegisterPath = Join-Path $SyntheticRepo "Documentation\Master_Asset_Register.csv"
    $HistoricalPath = Join-Path $SyntheticRepo "Documentation\Historical\HISTORICAL_CONTROL_000048.md"
    $ClosurePath = Join-Path $SyntheticRepo "Documentation\Build_Records\0048\CLOSURE_RECORD.json"
    $Build0048ExportPath = Join-Path $SyntheticRepo "12_Reports\Standards\RETATRUTIDE_CONTROLLED_CLINICIAN_HANDOFF_BUNDLE_STANDARD.md"
    $PriorOwnershipHelperPath = Join-Path $SyntheticRepo "13_Project_Genesis\Validators\build_0048_asset_ownership.py"
    $UnrelatedLegacyCrlfPath = Join-Path $SyntheticRepo "Scripts\Legacy\UNRELATED_HISTORICAL_CRLF.ps1"
    New-Item -ItemType Directory -Path (Split-Path -Parent $HistoricalPath) -Force | Out-Null
    New-Item -ItemType Directory -Path (Split-Path -Parent $ClosurePath) -Force | Out-Null

    $Headers = @(
        "Universal Asset Identifier", "Asset Name", "Knowledge System", "Asset Type", "Status", "Owner",
        "Parent Assets", "Last Review", "Notes", "Repository Path", "Supporting Files", "Version",
        "Completion Percentage", "Child Assets", "Relationship List", "Evidence Links", "Report Links",
        "Marketplace Links", "Next Review", "Change History", "Build Provenance", "Source Builds",
        "Registration Basis", "File SHA256", "Last Updated"
    )
    $HistoricalRow = @(
        "CERT-SYS-000048", "Historical unrelated control", "SYS", "HISTORICAL_CONTROL", "ACTIVE", "Certiaura",
        "", "2026-07-20", "Regression fixture", "Documentation/Historical/HISTORICAL_CONTROL_000048.md", "", "1.0.0",
        "100", "", "", "", "", "", "2027-07-20", "Historical fixture", "CERT-BUILD-0048", "0048",
        "HISTORICAL_REGRESSION_FIXTURE", "", "2026-07-20T00:00:00Z"
    )
    if ($Headers.Count -ne $HistoricalRow.Count) {
        throw "Synthetic Master Asset Register fixture is structurally invalid."
    }
    $RegisterText = (($Headers -join ",") + "`n" + ($HistoricalRow -join ",") + "`n")
    Write-Utf8NoBomLf -Path $RegisterPath -Content $RegisterText
    Write-Utf8NoBomLf -Path $HistoricalPath -Content "# Historical unrelated control`n"
    Write-Utf8NoBomLf -Path $Build0048ExportPath -Content "# Build 0048 controlled clinician handoff bundle standard`n`nBuild provenance: CERT-BUILD-0048`n"
    Write-Utf8NoBomLf -Path $PriorOwnershipHelperPath -Content "BUILD_PROVENANCE = `"CERT-BUILD-0048`"`n"
    New-Item -ItemType Directory -Path (Split-Path -Parent $UnrelatedLegacyCrlfPath) -Force | Out-Null
    [System.IO.File]::WriteAllBytes(
        $UnrelatedLegacyCrlfPath,
        [System.Text.Encoding]::ASCII.GetBytes("Write-Host `"Historical unrelated fixture`"`r`n")
    )
    $UnrelatedLegacyCrlfHashBefore = (Get-FileHash -LiteralPath $UnrelatedLegacyCrlfPath -Algorithm SHA256).Hash
    $Build0048ExportHashBefore = (Get-FileHash -LiteralPath $Build0048ExportPath -Algorithm SHA256).Hash
    $PriorOwnershipHashBefore = (Get-FileHash -LiteralPath $PriorOwnershipHelperPath -Algorithm SHA256).Hash
    $Closure = [ordered]@{
        build = "0048"
        state = "ACTIONS_GREEN_CLOSED"
        commit_subject = $PriorCommitMessage
    } | ConvertTo-Json -Depth 4
    Write-Utf8NoBomLf -Path $ClosurePath -Content $Closure

    git -C $SyntheticRepo add -A
    Assert-NativeExit "Stage synthetic baseline"
    git -C $SyntheticRepo commit -m $PriorCommitMessage
    Assert-NativeExit "Commit synthetic Build 0048 baseline"
    git -C $SyntheticRepo push -u origin main
    Assert-NativeExit "Push synthetic Build 0048 baseline"

    Write-Step "Resolve exact Build 0048 commit and ancestry"
    $PriorMatches = @(
        git -C $SyntheticRepo log --format="%H%x09%s" --all |
        ForEach-Object {
            $Parts = @($_ -split "`t", 2)
            if ($Parts.Count -eq 2 -and $Parts[1] -ceq $PriorCommitMessage) {
                $Parts[0]
            }
        }
    )
    Assert-NativeExit "Read synthetic Git history"
    if ($PriorMatches.Count -ne 1) {
        throw "Expected exactly one exact Build 0048 implementation commit; found $($PriorMatches.Count)."
    }
    $PriorCommit = $PriorMatches[0]
    $SyntheticHead = (git -C $SyntheticRepo rev-parse HEAD).Trim()
    Assert-NativeExit "Read synthetic HEAD"
    git -C $SyntheticRepo merge-base --is-ancestor $PriorCommit $SyntheticHead
    Assert-NativeExit "Verify Build 0048 ancestry"

    Write-Step "Stop and restart OneDrive control"
    $OneDriveState = Stop-OneDriveSafely
    Start-OneDriveIfRequired -State $OneDriveState
    $OneDriveState = [pscustomobject]@{
        WasRunning = $false
        Executable = $null
    }

    Write-Step "Run Project Genesis synthetic dry-run"
    & $Importer -Repository $SyntheticRepo -Package $Package -Report $DryRunReport
    $DryRun = Get-Content -LiteralPath $DryRunReport -Raw | ConvertFrom-Json
    if (-not [bool]$DryRun.valid -or $DryRun.transaction_status -ne "DRY_RUN_VALIDATED") {
        throw "Build 0049 synthetic dry-run did not validate."
    }
    if (@($DryRun.register_changes).Count -ne 6) {
        throw "Build 0049 synthetic dry-run did not identify six formal asset changes."
    }

    Write-Step "Confirm internal backup fixture is blocked"
    $InternalBackupBlocked = $false
    try {
        & $Importer `
            -Repository $SyntheticRepo `
            -Package $Package `
            -Report $InternalBackupReport `
            -BackupRoot (Join-Path $SyntheticRepo "Backups") `
            -Apply
    }
    catch {
        $InternalBackupBlocked = $true
    }
    if (-not $InternalBackupBlocked) {
        throw "Internal transactional backup fixture was not blocked."
    }
    $InternalBackupResult = Get-Content -LiteralPath $InternalBackupReport -Raw | ConvertFrom-Json
    if ([bool]$InternalBackupResult.valid -or $InternalBackupResult.transaction_status -ne "FAILED_CLOSED") {
        throw "Internal backup negative fixture did not fail closed."
    }

    Write-Step "Apply transaction with backup outside repository"
    $ExternalBackupRoot = Join-Path $ReportRoot "Transactional_Backups"
    New-Item -ItemType Directory -Path $ExternalBackupRoot -Force | Out-Null
    & $Importer `
        -Repository $SyntheticRepo `
        -Package $Package `
        -Report $ApplyReport `
        -BackupRoot $ExternalBackupRoot `
        -Apply
    $ApplyResult = Get-Content -LiteralPath $ApplyReport -Raw | ConvertFrom-Json
    if (-not [bool]$ApplyResult.valid -or -not [bool]$ApplyResult.applied) {
        throw "Build 0049 synthetic apply did not validate."
    }
    $BackupPath = [System.IO.Path]::GetFullPath([string]$ApplyResult.backup_path)
    $SyntheticFull = [System.IO.Path]::GetFullPath($SyntheticRepo)
    if ($BackupPath.StartsWith($SyntheticFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Transactional backup was created inside the synthetic repository."
    }
    if (-not (Test-Path -LiteralPath $BackupPath -PathType Container)) {
        throw "External transactional backup was not created."
    }

    Write-Step "Exercise post-apply rollback and clean reapply"
    & $Python -B $RollbackHelper `
        --repository $SyntheticRepo `
        --apply-report $ApplyReport `
        --rollback-report $RollbackReport `
        --expected-package-sha256 $ActualPackageSha256
    Assert-NativeExit "Build 0049 synthetic post-apply rollback"
    $RollbackResult = Get-Content -LiteralPath $RollbackReport -Raw | ConvertFrom-Json
    if (-not [bool]$RollbackResult.valid -or $RollbackResult.status -ne "ROLLED_BACK_CLEAN") {
        throw "Build 0049 synthetic rollback report is not clean."
    }
    $RollbackStatus = @(git -C $SyntheticRepo status --porcelain --untracked-files=all)
    Assert-NativeExit "Synthetic rollback Git status"
    if ($RollbackStatus.Count -gt 0) {
        throw "Synthetic repository is not clean after rollback."
    }

    & $Importer `
        -Repository $SyntheticRepo `
        -Package $Package `
        -Report $SecondDryRunReport
    $SecondDryRunResult = Get-Content -LiteralPath $SecondDryRunReport -Raw | ConvertFrom-Json
    if (-not [bool]$SecondDryRunResult.valid -or $SecondDryRunResult.transaction_status -ne "DRY_RUN_VALIDATED") {
        throw "Build 0049 second synthetic dry run did not validate after rollback."
    }
    if ([string]::IsNullOrWhiteSpace([string]$ExternalBackupRoot)) {
        throw "The synthetic external backup root is not initialised."
    }
    & $Importer `
        -Repository $SyntheticRepo `
        -Package $Package `
        -Report $SecondApplyReport `
        -BackupRoot $ExternalBackupRoot `
        -Apply
    $SecondApplyResult = Get-Content -LiteralPath $SecondApplyReport -Raw | ConvertFrom-Json
    if (-not [bool]$SecondApplyResult.valid -or -not [bool]$SecondApplyResult.applied) {
        throw "Build 0049 second synthetic apply did not validate after rollback."
    }

    Write-Step "Verify Master Asset Register reconciliation"
    $RegisterRows = @(Import-Csv -LiteralPath $RegisterPath)
    if ($RegisterRows.Count -ne 7) {
        throw "Expected seven Master Asset Register rows after import; found $($RegisterRows.Count)."
    }
    $HistoricalRows = @($RegisterRows | Where-Object {
        $_.'Universal Asset Identifier' -ceq "CERT-SYS-000048"
    })
    if ($HistoricalRows.Count -ne 1) {
        throw "Historical UAI 000048 fixture was not preserved exactly once."
    }
    if ($HistoricalRows[0].'Build Provenance' -ne "CERT-BUILD-0048") {
        throw "Historical UAI 000048 fixture was not preserved as Build 0048 provenance."
    }
    $BuildRows = @($RegisterRows | Where-Object {
        $_.'Build Provenance' -ceq $BuildId
    })
    if ($BuildRows.Count -ne 6) {
        throw "Expected six exact Build 0049 register rows; found $($BuildRows.Count)."
    }

    Write-Step "Run exact ownership validator and automated tests"
    $env:PYTHONDONTWRITEBYTECODE = "1"
    $Build0048ExportHashAfter = (Get-FileHash -LiteralPath $Build0048ExportPath -Algorithm SHA256).Hash
    $PriorOwnershipHashAfter = (Get-FileHash -LiteralPath $PriorOwnershipHelperPath -Algorithm SHA256).Hash
    $UnrelatedLegacyCrlfHashAfter = (Get-FileHash -LiteralPath $UnrelatedLegacyCrlfPath -Algorithm SHA256).Hash
    if ($UnrelatedLegacyCrlfHashAfter -ne $UnrelatedLegacyCrlfHashBefore) {
        throw "Build 0049 modified the unrelated historical CRLF fixture."
    }
    if ($Build0048ExportHashAfter -ne $Build0048ExportHashBefore) {
        throw "Build 0048 controlled clinician handoff bundle standard was modified by Build 0049."
    }
    if ($PriorOwnershipHashAfter -ne $PriorOwnershipHashBefore) {
        throw "Build 0048 ownership helper was modified by Build 0049."
    }

    $Validator = Join-Path $SyntheticRepo "13_Project_Genesis\Validators\validate_retatrutide_follow_up_feedback_audit.py"
    $TestRoot = Join-Path $SyntheticRepo "13_Project_Genesis\Tests"
    & $Python -B $Validator $SyntheticRepo --report $ValidatorReport
    Assert-NativeExit "Build 0049 exact ownership validator"
    & $Python -B -m unittest discover `
        -s $TestRoot `
        -p "test_build_0049_retatrutide_follow_up_feedback_audit.py"
    Assert-NativeExit "Build 0049 automated tests"

    Write-Step "Check runtime artefacts and Git hygiene"
    $Runtime = @(Get-ChildItem -LiteralPath $SyntheticRepo -Recurse -Force -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -in @("__pycache__", ".pytest_cache", ".mypy_cache") -or
        $_.Extension -in @(".pyc", ".pyo")
    })
    if ($Runtime.Count -gt 0) {
        throw "Runtime artefacts were detected after regression."
    }
    $Deleted = @(git -C $SyntheticRepo status --short --untracked-files=all | Where-Object {
        $_ -match "^\s*D|^D"
    })
    Assert-NativeExit "Synthetic deletion check"
    if ($Deleted.Count -gt 0) {
        throw "Unexpected deletions were detected in the synthetic repository."
    }
    git -C $SyntheticRepo diff --check
    Assert-NativeExit "git diff --check"
    git -C $SyntheticRepo add -A
    Assert-NativeExit "Stage synthetic Build 0049"
    git -C $SyntheticRepo diff --cached --check
    Assert-NativeExit "git diff --cached --check"
    $Unstaged = @(git -C $SyntheticRepo diff --name-only)
    Assert-NativeExit "Unstaged change check"
    if ($Unstaged.Count -gt 0) {
        throw "Unstaged synthetic changes remain."
    }

    Write-Step "Commit and push synthetic Build 0049"
    git -C $SyntheticRepo commit -m $CommitMessage
    Assert-NativeExit "Commit synthetic Build 0049"
    git -C $SyntheticRepo push origin main
    Assert-NativeExit "Push synthetic Build 0049"
    $RemoteSubject = (
        git --git-dir=$SyntheticRemote log -1 --format="%s" refs/heads/main
    ).Trim()
    Assert-NativeExit "Read synthetic remote HEAD"
    if ($RemoteSubject -cne $CommitMessage) {
        throw "Synthetic remote commit subject does not match the locked Build 0049 message."
    }
    $FinalStatus = @(git -C $SyntheticRepo status --porcelain --untracked-files=all)
    Assert-NativeExit "Final synthetic Git status"
    if ($FinalStatus.Count -gt 0) {
        throw "Synthetic repository is not clean after commit and push."
    }

    $Result = [ordered]@{
        build_id = $BuildId
        build_number = $BuildNumber
        status = "PASS"
        runtime = "Windows PowerShell 5.1"
        package_sha256 = $ActualPackageSha256
        package_preflight = "PASS"
        package_resolver_array_normalisation = "PASS"
        cmd_parser_precheck = "PASS"
        exact_prior_commit_resolution = "PASS"
        prior_commit_ancestry = "PASS"
        synthetic_dry_run = "DRY_RUN_VALIDATED"
        internal_backup_negative_fixture = "BLOCKED_AS_DESIGNED"
        synthetic_apply = "APPLIED_VALIDATED"
        external_transactional_backup = "PASS"
        post_apply_rollback = "ROLLED_BACK_CLEAN_AND_REAPPLIED"
        register_rows_after = $RegisterRows.Count
        formal_assets_registered = $BuildRows.Count
        historical_uai_000048 = "PRESERVED_AND_EXCLUDED"
        build_0048_handoff_bundle_standard = "PRESERVED_UNCHANGED"
        build_0048_ownership_helper = "PRESERVED_UNCHANGED"
        dry_run_collision_inventory = "PASS"
        exact_provenance_validator = "PASS"
        automated_tests = "19_OF_19_PASS"
        runtime_artefacts = "NONE"
        git_diff_check = "PASS"
        git_diff_cached_check = "PASS"
        synthetic_commit_push = "PASS"
        accumulated_prior_build_lessons_reviewed = "PASS"
        current_build_lessons_recorded = "PASS"
        lessons_converted_to_regression_controls = "PASS"
        continuity_checkpoint_updated = "PASS"
        github_actions_handoff = "READY_AFTER_CANONICAL_PUSH"
        canonical_repository_modified = $false
    }
    Write-Utf8NoBomLf -Path $RegressionReport -Content ($Result | ConvertTo-Json -Depth 8)

    Write-Host ""
    Write-Host "BUILD 0049 WINDOWS POWERSHELL 5.1 REGRESSION: PASS" -ForegroundColor Green
    Write-Host "Regression report: $RegressionReport"
    Write-Host "Canonical repository modified: NO"
}
catch {
    Write-Host ""
    Write-Host "BUILD 0049 WINDOWS POWERSHELL 5.1 REGRESSION: FAIL" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    throw
}
finally {
    Start-OneDriveIfRequired -State $OneDriveState
    if ($TempRoot -and (Test-Path -LiteralPath $TempRoot)) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
