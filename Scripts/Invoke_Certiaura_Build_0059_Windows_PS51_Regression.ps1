[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackagePath,
    [Parameter(Mandatory = $true)][string]$Repository,
    [Parameter(Mandatory = $true)][string]$ReportRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ExpectedCommit = "Add Certiaura Build 0059 tesamorelin governed review-board approvals, evidence-pack version control, challenge and appeal resolution, suspension recovery, periodic reassessment and reusable peptide-review operating model baseline"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TempRoot = Join-Path `
    $env:TEMP `
    ("CERTIAURA_0059_PS51_" + [guid]::NewGuid().ToString("N"))
$Clone = Join-Path $TempRoot "repo"
$Backups = Join-Path $TempRoot "backups"
$Extract = Join-Path $TempRoot "payload"
$BareRemote = Join-Path $TempRoot "remote.git"

function Test-ApprovedPredecessorUpdate {
    param([Parameter(Mandatory = $true)]$Item)

    $ActionProperty = $Item.PSObject.Properties["intended_action"]
    $OverlapProperty = $Item.PSObject.Properties["approved_predecessor_overlap"]

    if ($null -eq $ActionProperty -or $null -eq $OverlapProperty) {
        return $false
    }

    return (
        [string]$ActionProperty.Value -eq "UPDATE" -and
        [bool]$OverlapProperty.Value
    )
}

function Assert-OptionalManifestPropertyHandling {
    $Probe = @(
        [pscustomobject]@{
            repository_path = "probe/create"
            intended_action = "CREATE"
        },
        [pscustomobject]@{
            repository_path = "probe/update"
            intended_action = "UPDATE"
            approved_predecessor_overlap = $true
        }
    )

    $AllowedProbe = @(
        $Probe |
            Where-Object { Test-ApprovedPredecessorUpdate -Item $_ }
    )

    if (
        $AllowedProbe.Count -ne 1 -or
        [string]$AllowedProbe[0].repository_path -ne "probe/update"
    ) {
        throw "StrictMode optional manifest property handling failed."
    }

    Write-Host "BUILD_0059_OPTIONAL_PROPERTY_STRICTMODE_VALIDATED" -ForegroundColor Green
}

function Resolve-PythonCommand {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $Python) {
        return [pscustomobject]@{ Path = $Python.Source; Prefix = @() }
    }
    $Launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $Launcher) {
        return [pscustomobject]@{ Path = $Launcher.Source; Prefix = @("-3") }
    }
    throw "Python was not found on PATH."
}

New-Item -ItemType Directory -Path $TempRoot, $Backups, $Extract -Force | Out-Null

try {
    & git clone --no-hardlinks $Repository $Clone
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary regression clone failed."
    }

    Expand-Archive -LiteralPath $PackagePath -DestinationPath $Extract -Force
    $Importer = Join-Path `
        $Extract `
        "Scripts\Invoke_Certiaura_Build_0059_Import.ps1"

    $ForcedReport = Join-Path `
        $ReportRoot `
        ("BUILD_0059_FORCED_ROLLBACK_" + $Timestamp + ".json")

    & $Importer `
        -PackagePath $PackagePath `
        -Repository $Clone `
        -BackupRoot $Backups `
        -ReportPath $ForcedReport `
        -Apply `
        -ForceFailureAfterApply

    $Forced = Get-Content -LiteralPath $ForcedReport -Raw | ConvertFrom-Json
    if ([string]$Forced.result -ne "ROLLBACK_STATE_EXACT") {
        throw "Forced-failure import did not return ROLLBACK_STATE_EXACT."
    }

    $DirtyAfterRollback = @(
        & git -C $Clone status --porcelain --untracked-files=all
    )
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone status check failed after rollback."
    }
    if ($DirtyAfterRollback.Count -gt 0) {
        throw "Temporary clone was not restored exactly after forced failure."
    }

    $CleanReport = Join-Path `
        $ReportRoot `
        ("BUILD_0059_CLEAN_REAPPLY_" + $Timestamp + ".json")

    & $Importer `
        -PackagePath $PackagePath `
        -Repository $Clone `
        -BackupRoot $Backups `
        -ReportPath $CleanReport `
        -Apply

    $Clean = Get-Content -LiteralPath $CleanReport -Raw | ConvertFrom-Json
    if ([string]$Clean.result -ne "CLEAN_REAPPLY_VALIDATED") {
        throw "Clean synthetic reapply did not validate."
    }

    $Python = Resolve-PythonCommand
    $RepositoryValidator = Join-Path `
        $Clone `
        "13_Project_Genesis\Validators\validate_build_0059_repository.py"
    $RepositoryReport = Join-Path `
        $Clone `
        "Documentation\Build_Records\0059\POST_IMPORT_REPOSITORY_VALIDATION.json"
    $ValidationArguments = @($Python.Prefix) + @(
        "-B",
        $RepositoryValidator,
        $Clone,
        "--report",
        $RepositoryReport
    )
    & $Python.Path @ValidationArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone Build 0059 repository validation failed."
    }

    $TestArguments = @($Python.Prefix) + @(
        "-B",
        "-m",
        "unittest",
        "discover",
        "-s",
        (Join-Path $Clone "13_Project_Genesis\Tests"),
        "-p",
        "test_build_0059_*.py",
        "-v"
    )
    & $Python.Path @TestArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone full Build 0059 test suite failed before canonical apply."
    }

    Write-Host "BUILD_0059_PRE_CANONICAL_FULL_SUITE_VALIDATED" -ForegroundColor Green

    $ManifestPath = Join-Path `
        $Clone `
        "Documentation\Build_Records\0059\ASSET_INTENT_MANIFEST.json"
    $Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $Owned = @(
        @($Manifest.files | ForEach-Object { [string]$_.repository_path }) +
        @($Manifest.generated_files | ForEach-Object { [string]$_.repository_path }) |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
    )

    & git -C $Clone add --all -- @Owned
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone staging failed."
    }

    $Staged = @(
        & git -C $Clone diff --cached --name-only -- |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
    )
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone staged path read failed."
    }

    $ActualChanged = @(
        & git -C $Clone diff HEAD --name-only -- |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
    )
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone actual change-set read failed."
    }

    $Untracked = @(
        & git -C $Clone ls-files --others --exclude-standard |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
    )
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone untracked path read failed."
    }

    $ActualChanged = @(
        @($ActualChanged) + @($Untracked) |
        Sort-Object -Unique
    )

    Assert-OptionalManifestPropertyHandling

    $AllowedNoOp = @(
        @($Manifest.files) + @($Manifest.generated_files) |
        Where-Object {
            Test-ApprovedPredecessorUpdate -Item $_
        } |
        ForEach-Object { [string]$_.repository_path } |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Sort-Object -Unique
    )

    $OutsideOwned = @(
        $ActualChanged |
        Where-Object { $Owned -notcontains $_ }
    )
    if ($OutsideOwned.Count -ne 0) {
        throw (
            "Temporary clone contains changes outside Build 0059 ownership: " +
            ($OutsideOwned -join ", ")
        )
    }

    $NoOpOwned = @(
        $Owned |
        Where-Object { $ActualChanged -notcontains $_ }
    )
    $UnexpectedNoOp = @(
        $NoOpOwned |
        Where-Object { $AllowedNoOp -notcontains $_ }
    )
    if ($UnexpectedNoOp.Count -ne 0) {
        throw (
            "Temporary clone contains unexpected no-op owned paths: " +
            ($UnexpectedNoOp -join ", ")
        )
    }

    if (@(Compare-Object -ReferenceObject $ActualChanged -DifferenceObject $Staged).Count -ne 0) {
        throw "Temporary clone staged change-set was not exact."
    }

    Write-Host (
        "BUILD_0059_STAGED_CHANGESET_VALIDATED owned=" +
        $Owned.Count +
        " staged=" +
        $Staged.Count +
        " approved_no_op=" +
        $NoOpOwned.Count
    ) -ForegroundColor Green

    & git -C $Clone diff --check
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone git diff --check failed."
    }

    & git -C $Clone diff --cached --check
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone git diff --cached --check failed."
    }

    $ByteValidator = Join-Path `
        $Clone `
        "13_Project_Genesis\Validators\verify_staged_byte_equality.py"
    $ByteArguments = @($Python.Prefix) + @(
        "-B",
        $ByteValidator,
        $Clone,
        $ManifestPath,
        "--report",
        (Join-Path $ReportRoot ("BUILD_0059_PS51_BYTE_EQUALITY_" + $Timestamp + ".json"))
    )
    & $Python.Path @ByteArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone raw staged-byte equality failed."
    }

    & git -C $Clone config user.email "certiaura-regression@example.invalid"
    & git -C $Clone config user.name "Certiaura Regression"
    $Guard = Join-Path $Clone "Scripts\Invoke_Certiaura_Git_NonInteractive_Guard.ps1"
    . $Guard
    & git -C $Clone config --local gc.auto 1
    & git -C $Clone config --local maintenance.auto true
    $PriorGcAuto = (& git -C $Clone config --local --get gc.auto).Trim()
    Invoke-CertiauraGitNonInteractiveGuard -Repository $Clone -ScriptBlock {
        & git -C $Clone commit -m $ExpectedCommit
        if ($LASTEXITCODE -ne 0) { throw "Temporary exact commit regression failed." }
    }
    $RestoredGcAuto = (& git -C $Clone config --local --get gc.auto).Trim()
    if ($PriorGcAuto -ne $RestoredGcAuto) { throw "Git guard did not restore gc.auto." }
    Write-Host "BUILD_0059_GIT_NONINTERACTIVE_GUARD_VALIDATED" -ForegroundColor Green
    Write-Host "NO_MANUAL_GIT_OBJECT_CLEANUP_PROMPTS" -ForegroundColor Green

    $ObservedSubject = (& git -C $Clone log -1 --pretty=%s).Trim()
    if ($ObservedSubject -ne $ExpectedCommit) {
        throw "Temporary committed subject was not exact."
    }

    & git init --bare $BareRemote
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary bare remote creation failed."
    }
    & git -C $Clone remote add build0059_regression $BareRemote
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary remote configuration failed."
    }
    Invoke-CertiauraGitNonInteractiveGuard -Repository $Clone -ScriptBlock {
        & git -C $Clone push build0059_regression HEAD:refs/heads/build0059-regression
        if ($LASTEXITCODE -ne 0) { throw "Temporary push-path regression failed." }
    }

    Write-Host "BUILD_0059_WINDOWS_PS51_REGRESSION_PASS" -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item `
            -LiteralPath $TempRoot `
            -Recurse `
            -Force `
            -ErrorAction SilentlyContinue
    }
}
