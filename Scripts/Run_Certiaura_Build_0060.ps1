[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackagePath,
    [Parameter(Mandatory = $true)][string]$ExpectedPackageSha256,
    [string]$Repository = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
    [string]$BackupRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Backups",
    [string]$ReportRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0060"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ExpectedHead = "594152fcfba3b1612b71d7b6e5c23759c906e464"
$ExpectedCommit = "Add Certiaura Build 0060 BPC-157 governed evidence reconstruction, regulatory and sport boundary assessment, human-evidence gap control, review-board transition, appeal resolution and repeatable multi-peptide onboarding baseline"

function Assert-Exit([string]$Name) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE."
    }
}


function Resolve-OneDriveExecutable {
    $Candidates = @(
        (Join-Path $env:LOCALAPPDATA "Microsoft\OneDrive\OneDrive.exe"),
        (Join-Path $env:ProgramFiles "Microsoft OneDrive\OneDrive.exe"),
        (Join-Path ${env:ProgramFiles(x86)} "Microsoft OneDrive\OneDrive.exe")
    )
    foreach ($Candidate in $Candidates) {
        if (
            -not [string]::IsNullOrWhiteSpace($Candidate) -and
            (Test-Path -LiteralPath $Candidate -PathType Leaf)
        ) {
            return $Candidate
        }
    }
    return $null
}

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

    Write-Host "BUILD_0060_OPTIONAL_PROPERTY_STRICTMODE_VALIDATED" -ForegroundColor Green
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

if (-not (Test-Path -LiteralPath $Repository -PathType Container)) {
    throw "Repository not found: $Repository"
}
if (-not (Test-Path -LiteralPath $PackagePath -PathType Leaf)) {
    throw "Package not found: $PackagePath"
}

New-Item -ItemType Directory -Path $BackupRoot, $ReportRoot -Force | Out-Null

$Hash = (Get-FileHash -LiteralPath $PackagePath -Algorithm SHA256).Hash
if ($Hash -ne $ExpectedPackageSha256) {
    throw "Build 0060 package SHA-256 mismatch. Expected $ExpectedPackageSha256; observed $Hash."
}

$InitialStatus = @(git -C $Repository status --porcelain)
Assert-Exit "read initial repository status"
if ($InitialStatus.Count -gt 0) {
    throw "Repository must be clean before Build 0060."
}

git -C $Repository fetch --all --prune
Assert-Exit "git fetch"
git -C $Repository pull --ff-only
Assert-Exit "git pull --ff-only"

$Head = (git -C $Repository rev-parse HEAD).Trim()
Assert-Exit "read repository HEAD"
if ($Head -ne $ExpectedHead) {
    throw "Repository HEAD $Head does not equal closed Build 0059 commit $ExpectedHead."
}

$Temp = Join-Path $env:TEMP ("CERTIAURA_0060_" + [guid]::NewGuid().ToString("N"))
$Extract = Join-Path $Temp "payload"
$OneDriveWasRunning = $false
$OneDriveExecutable = Resolve-OneDriveExecutable
$CanonicalApplied = $false
$CanonicalBackup = $null
$CanonicalImportReport = Join-Path $ReportRoot "BUILD_0060_CANONICAL_IMPORT.json"
$AutomaticRollbackReport = Join-Path $ReportRoot "BUILD_0060_AUTOMATIC_ROLLBACK.json"

try {
    New-Item -ItemType Directory -Path $Extract -Force | Out-Null
    Expand-Archive -LiteralPath $PackagePath -DestinationPath $Extract -Force

    $Preflight = Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0060_Preflight.ps1"
    $Regression = Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0060_Windows_PS51_Regression.ps1"
    $Importer = Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0060_Import.ps1"

    & $Preflight `
        -PackagePath $PackagePath `
        -ReportPath (Join-Path $ReportRoot "BUILD_0060_PREFLIGHT.json")

    & $Importer `
        -PackagePath $PackagePath `
        -Repository $Repository `
        -BackupRoot $BackupRoot `
        -ReportPath (Join-Path $ReportRoot "BUILD_0060_CANONICAL_DRY_RUN.json")

    & $Regression `
        -PackagePath $PackagePath `
        -Repository $Repository `
        -ReportRoot $ReportRoot

    $OneDriveProcesses = @(Get-Process OneDrive -ErrorAction SilentlyContinue)
    if ($OneDriveProcesses.Count -gt 0) {
        $OneDriveWasRunning = $true
        $OneDriveProcesses | Stop-Process -Force
        Start-Sleep -Seconds 2
    }

    & $Importer `
        -PackagePath $PackagePath `
        -Repository $Repository `
        -BackupRoot $BackupRoot `
        -ReportPath $CanonicalImportReport `
        -Apply

    $CanonicalResult = Get-Content `
        -LiteralPath $CanonicalImportReport `
        -Raw |
        ConvertFrom-Json
    if ([string]$CanonicalResult.result -ne "CLEAN_REAPPLY_VALIDATED") {
        throw "Canonical import did not return CLEAN_REAPPLY_VALIDATED."
    }
    $CanonicalBackup = [string]$CanonicalResult.backup_path
    if ([string]::IsNullOrWhiteSpace($CanonicalBackup)) {
        throw "Canonical import did not return a transaction backup path."
    }
    $CanonicalApplied = $true

    $Python = Resolve-PythonCommand
    $Validator = Join-Path $Repository "13_Project_Genesis\Validators\validate_build_0060_repository.py"
    $ManifestPath = Join-Path $Repository "Documentation\Build_Records\0060\ASSET_INTENT_MANIFEST.json"
    $RepositoryReport = Join-Path $Repository "Documentation\Build_Records\0060\POST_IMPORT_REPOSITORY_VALIDATION.json"

    $ValidationArguments = @($Python.Prefix) + @(
        "-B",
        $Validator,
        $Repository,
        "--report",
        $RepositoryReport
    )
    & $Python.Path @ValidationArguments
    Assert-Exit "Build 0060 repository validation"

    $TestArguments = @($Python.Prefix) + @(
        "-B",
        "-m",
        "unittest",
        "discover",
        "-s",
        (Join-Path $Repository "13_Project_Genesis\Tests"),
        "-p",
        "test_build_0060_*.py",
        "-v"
    )
    & $Python.Path @TestArguments
    Assert-Exit "Build 0060 tests"

    $Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $Owned = @(
        @($Manifest.files | ForEach-Object { [string]$_.repository_path }) +
        @($Manifest.generated_files | ForEach-Object { [string]$_.repository_path }) |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
    )

    git -C $Repository add --all -- @Owned
    Assert-Exit "stage Build 0060 owned paths"

    $Observed = @(
        git -C $Repository diff --cached --name-only -- |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
    )
    Assert-Exit "read staged Build 0060 paths"

    $ActualChanged = @(
        git -C $Repository diff HEAD --name-only -- |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
    )
    Assert-Exit "read actual Build 0060 change-set"

    $Untracked = @(
        git -C $Repository ls-files --others --exclude-standard |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
    )
    Assert-Exit "read untracked paths after Build 0060 staging"

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
            "Changes exist outside Build 0060 Asset Intent Manifest ownership: " +
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
            "Unexpected no-op Build 0060 owned paths: " +
            ($UnexpectedNoOp -join ", ")
        )
    }

    $Difference = @(
        Compare-Object `
            -ReferenceObject $ActualChanged `
            -DifferenceObject $Observed
    )
    if ($Difference.Count -ne 0) {
        throw "Final staged change-set does not exactly equal the actual Build 0060 Git change-set."
    }

    Write-Host (
        "BUILD_0060_STAGED_CHANGESET_VALIDATED owned=" +
        $Owned.Count +
        " staged=" +
        $Observed.Count +
        " approved_no_op=" +
        $NoOpOwned.Count
    ) -ForegroundColor Green

    git -C $Repository diff --check
    Assert-Exit "git diff --check"
    git -C $Repository diff --cached --check
    Assert-Exit "git diff --cached --check"

    $ByteValidator = Join-Path $Repository "13_Project_Genesis\Validators\verify_staged_byte_equality.py"
    $ByteArguments = @($Python.Prefix) + @(
        "-B",
        $ByteValidator,
        $Repository,
        $ManifestPath,
        "--report",
        (Join-Path $ReportRoot "BUILD_0060_STAGED_BYTE_EQUALITY.json")
    )
    & $Python.Path @ByteArguments
    Assert-Exit "raw staged byte equality"

    $CommitFile = Join-Path $Repository "Documentation\Build_Records\0060\COMMIT_MESSAGE.txt"
    if ((Get-Content -LiteralPath $CommitFile -Raw).Trim() -ne $ExpectedCommit) {
        throw "Reserved commit subject mismatch."
    }

    Write-Host ""
    Write-Host "BUILD_0060_CANONICAL_VALIDATED_AND_STAGED" -ForegroundColor Green
    Write-Host "Reserved commit message:"
    Write-Host $ExpectedCommit
}
catch {
    $OriginalFailure = $_
    if ($CanonicalApplied) {
        try {
            & $Importer `
                -PackagePath $PackagePath `
                -Repository $Repository `
                -BackupRoot $BackupRoot `
                -ReportPath $AutomaticRollbackReport `
                -RollbackBackup $CanonicalBackup

            $RollbackResult = Get-Content `
                -LiteralPath $AutomaticRollbackReport `
                -Raw |
                ConvertFrom-Json
            if ([string]$RollbackResult.result -ne "ROLLBACK_STATE_EXACT") {
                throw "Automatic rollback did not return ROLLBACK_STATE_EXACT."
            }
            Write-Host "BUILD_0060_AUTOMATIC_ROLLBACK_STATE_EXACT" -ForegroundColor Yellow
        }
        catch {
            throw (
                "Build 0060 post-import gate failed and automatic rollback also failed. " +
                "Original failure: " + $OriginalFailure.Exception.Message +
                " Rollback failure: " + $_.Exception.Message
            )
        }
    }
    throw $OriginalFailure
}
finally {
    if (
        $OneDriveWasRunning -and
        -not [string]::IsNullOrWhiteSpace($OneDriveExecutable) -and
        (Test-Path -LiteralPath $OneDriveExecutable -PathType Leaf)
    ) {
        Start-Process -FilePath $OneDriveExecutable -ErrorAction SilentlyContinue
    }
    if (Test-Path -LiteralPath $Temp) {
        Remove-Item -LiteralPath $Temp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
