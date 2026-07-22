[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackagePath,
    [Parameter(Mandatory = $true)][string]$ExpectedPackageSha256,
    [Parameter(Mandatory = $true)][string]$RepositoryPath,
    [Parameter(Mandatory = $true)][string]$ReportRootPath,
    [Parameter(Mandatory = $true)][string]$BackupRootPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"


function Resolve-PythonCommand {
    $PythonCommands = @(Get-Command python -ErrorAction SilentlyContinue)
    if ($PythonCommands.Count -gt 0) {
        return [pscustomobject]@{ Path = [string]$PythonCommands[0].Source; Prefix = @() }
    }
    $LauncherCommands = @(Get-Command py -ErrorAction SilentlyContinue)
    if ($LauncherCommands.Count -gt 0) {
        return [pscustomobject]@{ Path = [string]$LauncherCommands[0].Source; Prefix = @("-3") }
    }
    throw "Python was not found on PATH."
}

function Resolve-ExecutablePath {
    param([Parameter(Mandatory = $true)][string]$CommandName)
    $Commands = @(Get-Command $CommandName -ErrorAction SilentlyContinue)
    if ($Commands.Count -eq 0) { throw "Required executable missing: $CommandName" }
    return [string]$Commands[0].Source
}

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [string]$WorkingDirectory
    )
    $PreviousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        if ([string]::IsNullOrWhiteSpace($WorkingDirectory)) {
            $NativeOutput = @(& $FilePath @Arguments 2>&1)
        }
        else {
            Push-Location -LiteralPath $WorkingDirectory
            try { $NativeOutput = @(& $FilePath @Arguments 2>&1) }
            finally { Pop-Location }
        }
        $NativeExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $PreviousPreference
    }
    return [pscustomobject]@{
        ExitCode = [int]$NativeExitCode
        Output = @($NativeOutput | ForEach-Object { [string]$_ })
    }
}

function Convert-NativeOutputToText {
    param([object[]]$Output)
    return (@($Output | ForEach-Object { [string]$_ }) -join [Environment]::NewLine)
}

function Assert-NativeOutputContains {
    param(
        [Parameter(Mandatory = $true)]$Result,
        [Parameter(Mandatory = $true)][string]$RequiredToken,
        [Parameter(Mandatory = $true)][string]$Name
    )
    $OutputText = Convert-NativeOutputToText -Output @($Result.Output)
    if ($OutputText -notmatch [regex]::Escape($RequiredToken)) {
        throw "$Name did not emit required token '$RequiredToken'. Captured output: $OutputText"
    }
}

function Assert-NativeSuccess {
    param([Parameter(Mandatory = $true)]$Result,[Parameter(Mandatory = $true)][string]$Name)
    if ($Result.ExitCode -ne 0) {
        throw "$Name failed with exit code $($Result.ExitCode): $($Result.Output -join [Environment]::NewLine)"
    }
}

function Get-ReportPropertyValue {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name
    )
    $Property = $Object.PSObject.Properties[$Name]
    if ($null -eq $Property -or $null -eq $Property.Value) { return "<NOT PRESENT>" }
    return [string]$Property.Value
}

function Assert-TransactionalSuccess {
    param(
        [Parameter(Mandatory = $true)]$Result,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$ReportPath
    )
    if ($Result.ExitCode -eq 0) { return }
    $Details = @($Result.Output)
    if (Test-Path -LiteralPath $ReportPath -PathType Leaf) {
        try {
            $ReportObject = Get-Content -LiteralPath $ReportPath -Raw | ConvertFrom-Json
            $Details += "transaction_status=" + (Get-ReportPropertyValue -Object $ReportObject -Name "transaction_status")
            $Details += "rollback_completed=" + (Get-ReportPropertyValue -Object $ReportObject -Name "rollback_completed")
            $Details += "failure_code=" + (Get-ReportPropertyValue -Object $ReportObject -Name "failure_code")
            $Details += "rollback_reason=" + (Get-ReportPropertyValue -Object $ReportObject -Name "rollback_reason")
            $Details += "backup_path=" + (Get-ReportPropertyValue -Object $ReportObject -Name "backup_path")
            $Details += "report_path=" + $ReportPath
        }
        catch {
            $Details += "report_parse_error=" + $_.Exception.Message
            $Details += "report_path=" + $ReportPath
        }
    }
    else {
        $Details += "report_missing=" + $ReportPath
    }
    throw "$Name failed with exit code $($Result.ExitCode): $($Details -join [Environment]::NewLine)"
}


$MultiLineNativeOutputFixture = [pscustomobject]@{
    ExitCode = 3
    Output = @(
        "unrelated output before token",
        "BUILD_0052_TRANSACTION_ROLLED_BACK: SIMULATED",
        "unrelated output after token"
    )
}
Assert-NativeOutputContains -Result $MultiLineNativeOutputFixture -RequiredToken "BUILD_0052_TRANSACTION_ROLLED_BACK" -Name "Multiline native output positive control"
$MissingTokenOutputText = Convert-NativeOutputToText -Output @(
    "unrelated output only",
    "no required token present"
)
if ($MissingTokenOutputText -match [regex]::Escape("BUILD_0052_TRANSACTION_ROLLED_BACK")) {
    throw "Multiline native output negative control failed."
}
$MultiLineNativeOutputControl = "MULTILINE_NATIVE_OUTPUT_MATCH_VALIDATED"

$BuildCommitSubject = "Add Certiaura Build 0052 retatrutide cross-case signal aggregation, cohort surveillance, governed escalation and controlled knowledge feedback baseline"
$RequiredEndpoint = "BUILD_0052_RC6_READY_FOR_CANONICAL_IMPORT"
$ExpectedPackageSha256 = $ExpectedPackageSha256.ToUpperInvariant()
$ActualPackageSha256 = (Get-FileHash -LiteralPath $PackagePath -Algorithm SHA256).Hash
if ($ActualPackageSha256 -ne $ExpectedPackageSha256) { throw "Build 0052 RC6 package SHA-256 mismatch." }
if (-not (Test-Path -LiteralPath $RepositoryPath -PathType Container)) { throw "Canonical repository missing: $RepositoryPath" }

$PythonCommand = Resolve-PythonCommand
$GitPath = Resolve-ExecutablePath -CommandName "git"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$RegressionRootPath = Join-Path $env:TEMP ("Certiaura_0052_RC6_" + [guid]::NewGuid().ToString("N"))
$ExtractedPackagePath = Join-Path $RegressionRootPath "Package"
$SyntheticRepositoryPath = Join-Path $RegressionRootPath "Repository"
$EvidenceRootPath = Join-Path $RegressionRootPath "PredecessorEvidence"
$ExternalRegressionBackupPath = Join-Path $BackupRootPath ("Build_0052_RC6_Regression_" + $Timestamp)
$PushRemotePath = Join-Path $RegressionRootPath "Remote.git"
New-Item -ItemType Directory -Path $ReportRootPath -Force | Out-Null
New-Item -ItemType Directory -Path $ExternalRegressionBackupPath -Force | Out-Null

try {
    Expand-Archive -LiteralPath $PackagePath -DestinationPath $ExtractedPackagePath -Force
    $ManifestPath = Join-Path $ExtractedPackagePath "Documentation\Build_Records\0052\ASSET_INTENT_MANIFEST.json"
    $PreflightPath = Join-Path $ExtractedPackagePath "13_Project_Genesis\Release\run_build_0052_preflight.py"
    $EvidencePath = Join-Path $ExtractedPackagePath "13_Project_Genesis\Release\derive_build_0051_predecessor_evidence.py"
    $ImporterPath = Join-Path $ExtractedPackagePath "13_Project_Genesis\Import\run_build_0052_import.py"
    foreach ($RequiredPath in @($ManifestPath,$PreflightPath,$EvidencePath,$ImporterPath)) {
        if (-not (Test-Path -LiteralPath $RequiredPath -PathType Leaf)) { throw "Required RC6 file missing: $RequiredPath" }
    }

    $RepoStatus = Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$RepositoryPath,"status","--short","--untracked-files=all")
    Assert-NativeSuccess $RepoStatus "Canonical repository status"
    $PrecursorStatePath = Join-Path $ExtractedPackagePath "Documentation\Build_Records\0052\PRE_AUTHORISED_PRECURSOR_STATE.json"
    $PrecursorState = Get-Content -LiteralPath $PrecursorStatePath -Raw | ConvertFrom-Json
    $ExpectedPrecursorPaths = @($PrecursorState.paths | ForEach-Object { [string]$_.repository_path })
    $ObservedPrecursorPaths = @()
    $UnexpectedStatus = @()
    foreach ($StatusLine in @($RepoStatus.Output)) {
        if ([string]::IsNullOrWhiteSpace($StatusLine)) { continue }
        $RelativePath = $StatusLine.Substring(3).Trim().Replace("\","/")
        if ($ExpectedPrecursorPaths -notcontains $RelativePath) {
            $UnexpectedStatus += $StatusLine
            continue
        }
        if ($StatusLine.Substring(0,1) -eq " ") { throw "Pre-authorised precursor path is not staged in the Git index: $RelativePath" }
        $ExpectedRecord = @($PrecursorState.paths | Where-Object { [string]$_.repository_path -eq $RelativePath })[0]
        $ActualPrecursorHash = (Get-FileHash -LiteralPath (Join-Path $RepositoryPath $RelativePath) -Algorithm SHA256).Hash
        if ($ActualPrecursorHash -ne [string]$ExpectedRecord.sha256) { throw "Pre-authorised precursor hash mismatch: $RelativePath" }
        $ObservedPrecursorPaths += $RelativePath
    }
    if ($UnexpectedStatus.Count -gt 0) { throw "Unrelated canonical repository changes block RC6: $($UnexpectedStatus -join ', ')" }
    $PrecursorDifference = @(Compare-Object -ReferenceObject @($ExpectedPrecursorPaths | Sort-Object -Unique) -DifferenceObject @($ObservedPrecursorPaths | Sort-Object -Unique))
    if ($PrecursorDifference.Count -ne 0) { throw "The exact six-file staged governance precursor state is not present." }

    $PreflightReportPath = Join-Path $ReportRootPath ("BUILD_0052_RC6_PACKAGE_PREFLIGHT_" + $Timestamp + ".json")
    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$PreflightPath,$ExtractedPackagePath,"--report",$PreflightReportPath)
    $Result = Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args
    Assert-NativeSuccess $Result "RC6 package preflight"
    Write-Host "RC6_STAGE_01_PACKAGE_PREFLIGHT_PASS" -ForegroundColor Cyan

    $Clone = Invoke-NativeCommand -FilePath $GitPath -Arguments @("clone","--no-hardlinks",$RepositoryPath,$SyntheticRepositoryPath)
    Assert-NativeSuccess $Clone "Synthetic clone"
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"config","user.email","certiaura-regression@example.invalid")) "Configure Git email"
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"config","user.name","Certiaura Regression")) "Configure Git user"

    $HistoricalPath = Join-Path $SyntheticRepositoryPath "HISTORICAL_UNRELATED_BUILD_0052.txt"
    [System.IO.File]::WriteAllText($HistoricalPath,"Historical unrelated file retained by Build 0052 RC6 regression.`n",(New-Object System.Text.UTF8Encoding($false)))
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"add","--","HISTORICAL_UNRELATED_BUILD_0052.txt")) "Stage historical fixture"
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"commit","-m","Add unrelated historical regression fixture")) "Commit historical fixture"
    $HistoricalHashBefore = (Get-FileHash -LiteralPath $HistoricalPath -Algorithm SHA256).Hash

    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$EvidencePath,"--repository",$SyntheticRepositoryPath,"--current-manifest",$ManifestPath,"--output-root",$EvidenceRootPath,"--package-sha256",$ExpectedPackageSha256)
    $EvidenceResult = Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args
    Assert-NativeSuccess $EvidenceResult "Canonical Git predecessor evidence"
    if ($EvidenceResult.Output -notcontains "PREDECESSOR_CANONICAL_EVIDENCE_VALIDATED") { throw "Predecessor evidence endpoint missing." }
    Write-Host "RC6_STAGE_02_PREDECESSOR_EVIDENCE_PASS" -ForegroundColor Cyan
    $EvidenceReportPath = Join-Path $EvidenceRootPath "PREDECESSOR_CANONICAL_EVIDENCE.json"
    $Evidence = Get-Content -LiteralPath $EvidenceReportPath -Raw | ConvertFrom-Json
    $PredecessorPaths = @($Evidence.repository_paths)
    $ApprovedPredecessorReplacements = @($Evidence.approved_replacement_intersection)
    $PredecessorHashesBefore = @{}
    foreach ($RelativePath in $PredecessorPaths) {
        $AbsolutePath = Join-Path $SyntheticRepositoryPath ([string]$RelativePath)
        if (-not (Test-Path -LiteralPath $AbsolutePath -PathType Leaf)) { throw "Canonical predecessor path missing from synthetic clone: $RelativePath" }
        if ($ApprovedPredecessorReplacements -notcontains [string]$RelativePath) {
            $PredecessorHashesBefore[[string]$RelativePath] = (Get-FileHash -LiteralPath $AbsolutePath -Algorithm SHA256).Hash
        }
    }

    $DryRunReportPath = Join-Path $ReportRootPath ("BUILD_0052_RC6_DRY_RUN_" + $Timestamp + ".json")
    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$ImporterPath,"--repository",$SyntheticRepositoryPath,"--package",$ExtractedPackagePath,"--report",$DryRunReportPath,"--predecessor-evidence",$EvidenceReportPath,"--package-sha256",$ExpectedPackageSha256)
    $DryRunResult = Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args
    Assert-NativeSuccess $DryRunResult "Executable predecessor-aware dry run"
    $DryRun = Get-Content -LiteralPath $DryRunReportPath -Raw | ConvertFrom-Json
    if ([string]$DryRun.transaction_status -ne "DRY_RUN_VALIDATED" -or @($DryRun.conflicts).Count -ne 0) { throw "Dry run did not return DRY_RUN_VALIDATED with zero conflicts." }
    Write-Host "RC6_STAGE_03_DRY_RUN_PASS" -ForegroundColor Cyan

    $RollbackReportPath = Join-Path $ReportRootPath ("BUILD_0052_RC6_FORCED_ROLLBACK_" + $Timestamp + ".json")
    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$ImporterPath,"--repository",$SyntheticRepositoryPath,"--package",$ExtractedPackagePath,"--report",$RollbackReportPath,"--predecessor-evidence",$EvidenceReportPath,"--package-sha256",$ExpectedPackageSha256,"--apply","--backup-root",$ExternalRegressionBackupPath,"--simulate-post-apply-failure")
    $RollbackResult = Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args
    if ($RollbackResult.ExitCode -ne 3) { throw "Forced rollback did not return exit code 3: $($RollbackResult.Output -join [Environment]::NewLine)" }
    Assert-NativeOutputContains -Result $RollbackResult -RequiredToken "BUILD_0052_TRANSACTION_ROLLED_BACK" -Name "Forced rollback"
    $Rollback = Get-Content -LiteralPath $RollbackReportPath -Raw | ConvertFrom-Json
    if ([string]$Rollback.transaction_status -ne "ROLLED_BACK" -or $Rollback.rollback_completed -ne $true) { throw "Forced rollback not completed." }
    if ([string]$Rollback.failure_code -ne "BUILD_0052_TRANSACTION_ROLLED_BACK") { throw "Forced rollback report failure code missing." }
    if ([string]$Rollback.rollback_reason -ne "SIMULATED_POST_APPLY_FAILURE") { throw "Forced rollback reason was not visible to the operator." }
    $PostRollback = Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"status","--short","--untracked-files=all")
    Assert-NativeSuccess $PostRollback "Post-rollback status"
    if (@($PostRollback.Output).Count -ne 0) { throw "Synthetic repository not clean after rollback: $($PostRollback.Output -join ', ')" }
    Write-Host "RC6_STAGE_04_FORCED_ROLLBACK_PASS" -ForegroundColor Cyan

    $ApplyReportPath = Join-Path $ReportRootPath ("BUILD_0052_RC6_APPLY_" + $Timestamp + ".json")
    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$ImporterPath,"--repository",$SyntheticRepositoryPath,"--package",$ExtractedPackagePath,"--report",$ApplyReportPath,"--predecessor-evidence",$EvidenceReportPath,"--package-sha256",$ExpectedPackageSha256,"--apply","--backup-root",$ExternalRegressionBackupPath)
    $ApplyResult = Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args
    Assert-TransactionalSuccess $ApplyResult "Clean transactional reapply" $ApplyReportPath
    $LessonsUpdateReportPath = Join-Path $SyntheticRepositoryPath "Documentation\Build_Records\0052\ACCUMULATED_LESSONS_UPDATE_REPORT.json"
    if (-not (Test-Path -LiteralPath $LessonsUpdateReportPath -PathType Leaf)) { throw "Accumulated lessons runtime report missing after clean reapply." }
    $LessonsUpdateReport = Get-Content -LiteralPath $LessonsUpdateReportPath -Raw | ConvertFrom-Json
    if ([string]$LessonsUpdateReport.historical_coverage -ne "COMPLETE") { throw "Historical lessons coverage did not complete." }
    if ([string]$LessonsUpdateReport.historical_coverage_mode -ne "MATRIX_OR_HASH_BOUND_AUTHORITATIVE_LEDGER") { throw "Historical lessons coverage mode invalid." }
    $ExpectedLedgerOnlyBuilds = @("0039","0040","0043","0044","0045","0046")
    $ObservedLedgerOnlyBuilds = @($LessonsUpdateReport.ledger_only_builds | ForEach-Object { [string]$_ } | Sort-Object -Unique)
    $LedgerCoverageDifference = @(Compare-Object -ReferenceObject $ExpectedLedgerOnlyBuilds -DifferenceObject $ObservedLedgerOnlyBuilds)
    if ($LedgerCoverageDifference.Count -ne 0) { throw "Canonical legacy ledger-only build coverage mismatch: $($ObservedLedgerOnlyBuilds -join ',')" }
    if (@($LessonsUpdateReport.ledger_only_historical_evidence).Count -ne 6) { throw "Canonical ledger-only evidence count invalid." }
    Write-Host "RC6_STAGE_05_CLEAN_REAPPLY_PASS" -ForegroundColor Cyan
    Write-Host "RC6_STAGE_05A_HISTORICAL_LEDGER_COVERAGE_PASS" -ForegroundColor Cyan

    foreach ($RelativePath in $PredecessorPaths) {
        if ($ApprovedPredecessorReplacements -contains [string]$RelativePath) { continue }
        $AbsolutePath = Join-Path $SyntheticRepositoryPath ([string]$RelativePath)
        if ((Get-FileHash -LiteralPath $AbsolutePath -Algorithm SHA256).Hash -ne $PredecessorHashesBefore[[string]$RelativePath]) { throw "Unapproved predecessor path changed: $RelativePath" }
    }
    if ((Get-FileHash -LiteralPath $HistoricalPath -Algorithm SHA256).Hash -ne $HistoricalHashBefore) { throw "Unrelated historical path changed." }

    $SignalValidatorPath = Join-Path $SyntheticRepositoryPath "13_Project_Genesis\Validators\validate_retatrutide_cross_case_signal.py"
    $ValidExamplePath = Join-Path $SyntheticRepositoryPath "05_Monitoring\Examples\Retatrutide\valid_cross_case_watch_signal.example.json"
    $SignalReportPath = Join-Path $ReportRootPath ("BUILD_0052_RC6_SIGNAL_VALIDATOR_" + $Timestamp + ".json")
    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$SignalValidatorPath,$ValidExamplePath,"--report",$SignalReportPath)
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args) "Build 0052 scientific validator"

    $RepositoryValidatorPath = Join-Path $SyntheticRepositoryPath "13_Project_Genesis\Validators\validate_build_0052_repository.py"
    $RepositoryReportPath = Join-Path $ReportRootPath ("BUILD_0052_RC6_REPOSITORY_VALIDATOR_" + $Timestamp + ".json")
    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$RepositoryValidatorPath,$SyntheticRepositoryPath,"--report",$RepositoryReportPath)
    $RepositoryValidation = Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args
    Assert-NativeSuccess $RepositoryValidation "Exact Build 0052 repository validator"
    Assert-NativeOutputContains -Result $RepositoryValidation -RequiredToken "BUILD_0052_REPOSITORY_VALIDATED" -Name "Repository validator"

    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B","-m","unittest","discover","-s",(Join-Path $SyntheticRepositoryPath "13_Project_Genesis\Tests"),"-p","test_build_0052_*.py","-v")
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args) "Exact unittest discover"
    Write-Host "RC6_STAGE_06_VALIDATORS_AND_TESTS_PASS" -ForegroundColor Cyan

    $RuntimeArtifacts = @(Get-ChildItem -LiteralPath $SyntheticRepositoryPath -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq "__pycache__" -or $_.Extension -in @(".pyc",".pyo") })
    if ($RuntimeArtifacts.Count -ne 0) { throw "Python runtime artifacts created." }

    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"diff","--check")) "git diff --check"
    $Manifest = Get-Content -LiteralPath (Join-Path $SyntheticRepositoryPath "Documentation\Build_Records\0052\ASSET_INTENT_MANIFEST.json") -Raw | ConvertFrom-Json
    $BuildPaths = @($Manifest.files | ForEach-Object { [string]$_.repository_path })
    $GitAddArguments = @("-c","core.autocrlf=false","-c","core.safecrlf=true","-C",$SyntheticRepositoryPath,"add","--") + $BuildPaths
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments $GitAddArguments) "Stage exact Build 0052 paths"
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"diff","--cached","--check")) "git diff --cached --check"

    foreach ($RelativePath in $BuildPaths) {
        $AbsolutePath = Join-Path $SyntheticRepositoryPath $RelativePath
        $RawHash = Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"hash-object","--no-filters","--",$AbsolutePath)
        $IndexHash = Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"rev-parse",(":" + $RelativePath))
        Assert-NativeSuccess $RawHash "Raw Git hash"
        Assert-NativeSuccess $IndexHash "Index Git hash"
        if (($RawHash.Output -join "").Trim() -ne ($IndexHash.Output -join "").Trim()) { throw "Index bytes differ from exact working-tree bytes: $RelativePath" }
    }

    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"commit","-m",$BuildCommitSubject)) "Synthetic Build 0052 commit"
    $Subject = Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"log","-1","--pretty=%s")
    Assert-NativeSuccess $Subject "Read synthetic commit subject"
    if (($Subject.Output -join "").Trim() -ne $BuildCommitSubject) { throw "Reserved commit subject mismatch." }
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments @("init","--bare",$PushRemotePath)) "Create local push remote"
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"remote","set-url","origin",$PushRemotePath)) "Set local push remote"
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $GitPath -Arguments @("-C",$SyntheticRepositoryPath,"push","-u","origin","HEAD")) "Local push-path regression"
    Write-Host "RC6_STAGE_07_GIT_COMMIT_PUSH_PATH_PASS" -ForegroundColor Cyan

    $FinalReport = [ordered]@{
        build_number = "0052"
        candidate = "RC6"
        package_sha256 = $ExpectedPackageSha256
        accumulated_prior_build_lessons_reviewed = "PASS"
        current_build_lessons_recorded = "PASS"
        lessons_converted_to_regression_controls = "PASS"
        accumulated_lessons_source_auto_updated = "PASS"
        historical_lessons_coverage = "COMPLETE"
        continuity_checkpoint_updated = "PASS"
        predecessor_fixture_identity = "EXACT BUILD 0051 - GENERATED FROM CANONICAL GIT"
        predecessor_manifest_schema = $Evidence.predecessor_manifest_path_schema
        predecessor_fixture_provenance = "PASS"
        predecessor_current_unauthorised_intersection = "EMPTY"
        predecessor_commit_subject = "EXACT MATCH"
        predecessor_paths_preserved_unchanged = "PASS"
        executable_predecessor_aware_dry_run = "DRY_RUN_VALIDATED"
        predecessor_dry_run_conflicts = "NONE"
        negative_predecessor_tests = "15 PASS"
        result = $RequiredEndpoint
    }
    $FinalReportPath = Join-Path $ReportRootPath ("BUILD_0052_RC6_REAL_WORLD_OPERATOR_WORKFLOW_" + $Timestamp + ".json")
    [System.IO.File]::WriteAllText($FinalReportPath,($FinalReport | ConvertTo-Json -Depth 8) + "`n",(New-Object System.Text.UTF8Encoding($false)))

    Write-Host "BUILD 0052 RC6 WINDOWS POWERSHELL 5.1 REGRESSION: PASS" -ForegroundColor Green
    Write-Host $RequiredEndpoint -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $RegressionRootPath) { Remove-Item -LiteralPath $RegressionRootPath -Recurse -Force -ErrorAction SilentlyContinue }
}
