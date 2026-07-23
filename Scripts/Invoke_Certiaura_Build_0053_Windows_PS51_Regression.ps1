[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackagePath,
    [Parameter(Mandatory = $true)][string]$Repository,
    [Parameter(Mandatory = $true)][string]$ReportRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ExpectedCommit = "Add Certiaura Build 0053 retatrutide governed knowledge change implementation, cross-asset impact control, controlled publication and post-change effectiveness surveillance baseline"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TempRoot = Join-Path `
    $env:TEMP `
    ("CERTIAURA_0053_PS51_" + [guid]::NewGuid().ToString("N"))
$Clone = Join-Path $TempRoot "repo"
$Backups = Join-Path $TempRoot "backups"
$Extract = Join-Path $TempRoot "payload"
$BareRemote = Join-Path $TempRoot "remote.git"

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
        "Scripts\Invoke_Certiaura_Build_0053_Import.ps1"

    $ForcedReport = Join-Path `
        $ReportRoot `
        ("BUILD_0053_FORCED_ROLLBACK_" + $Timestamp + ".json")

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
        ("BUILD_0053_CLEAN_REAPPLY_" + $Timestamp + ".json")

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
        "13_Project_Genesis\Validators\validate_build_0053_repository.py"
    $RepositoryReport = Join-Path `
        $Clone `
        "Documentation\Build_Records\0053\POST_IMPORT_REPOSITORY_VALIDATION.json"
    $ValidationArguments = @($Python.Prefix) + @(
        "-B",
        $RepositoryValidator,
        $Clone,
        "--report",
        $RepositoryReport
    )
    & $Python.Path @ValidationArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone Build 0053 repository validation failed."
    }

    $TestArguments = @($Python.Prefix) + @(
        "-B",
        "-m",
        "unittest",
        "discover",
        "-s",
        (Join-Path $Clone "13_Project_Genesis\Tests"),
        "-p",
        "test_build_0053_*.py",
        "-v"
    )
    & $Python.Path @TestArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone full Build 0053 test suite failed before canonical apply."
    }

    Write-Host "BUILD_0053_PRE_CANONICAL_FULL_SUITE_VALIDATED" -ForegroundColor Green

    $ManifestPath = Join-Path `
        $Clone `
        "Documentation\Build_Records\0053\ASSET_INTENT_MANIFEST.json"
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
    if (@(Compare-Object -ReferenceObject $Owned -DifferenceObject $Staged).Count -ne 0) {
        throw "Temporary clone staged ownership was not exact."
    }

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
        (Join-Path $ReportRoot ("BUILD_0053_PS51_BYTE_EQUALITY_" + $Timestamp + ".json"))
    )
    & $Python.Path @ByteArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary clone raw staged-byte equality failed."
    }

    & git -C $Clone config user.email "certiaura-regression@example.invalid"
    & git -C $Clone config user.name "Certiaura Regression"
    & git -C $Clone commit -m $ExpectedCommit
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary exact commit regression failed."
    }

    $ObservedSubject = (& git -C $Clone log -1 --pretty=%s).Trim()
    if ($ObservedSubject -ne $ExpectedCommit) {
        throw "Temporary committed subject was not exact."
    }

    & git init --bare $BareRemote
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary bare remote creation failed."
    }
    & git -C $Clone remote add build0053_regression $BareRemote
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary remote configuration failed."
    }
    & git -C $Clone push build0053_regression HEAD:refs/heads/build0053-regression
    if ($LASTEXITCODE -ne 0) {
        throw "Temporary push-path regression failed."
    }

    Write-Host "BUILD_0053_WINDOWS_PS51_REGRESSION_PASS" -ForegroundColor Green
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
