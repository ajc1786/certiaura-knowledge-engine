[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackagePath,
    [Parameter(Mandatory = $true)][string]$ExpectedPackageSha256,
    [string]$Repository = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
    [string]$BackupRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Backups",
    [string]$ReportRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0053"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ExpectedHead = "890df218b4f4dea92f4ccfa36b8106de59eca1b1"
$ExpectedCommit = "Add Certiaura Build 0053 retatrutide governed knowledge change implementation, cross-asset impact control, controlled publication and post-change effectiveness surveillance baseline"

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
    throw "Build 0053 package SHA-256 mismatch. Expected $ExpectedPackageSha256; observed $Hash."
}

$InitialStatus = @(git -C $Repository status --porcelain)
Assert-Exit "read initial repository status"
if ($InitialStatus.Count -gt 0) {
    throw "Repository must be clean before Build 0053."
}

git -C $Repository fetch --all --prune
Assert-Exit "git fetch"
git -C $Repository pull --ff-only
Assert-Exit "git pull --ff-only"

$Head = (git -C $Repository rev-parse HEAD).Trim()
Assert-Exit "read repository HEAD"
if ($Head -ne $ExpectedHead) {
    throw "Repository HEAD $Head does not equal closed Build 0052 commit $ExpectedHead."
}

$Temp = Join-Path $env:TEMP ("CERTIAURA_0053_" + [guid]::NewGuid().ToString("N"))
$Extract = Join-Path $Temp "payload"
$OneDriveWasRunning = $false
$OneDriveExecutable = Resolve-OneDriveExecutable
$CanonicalApplied = $false
$CanonicalBackup = $null
$CanonicalImportReport = Join-Path $ReportRoot "BUILD_0053_CANONICAL_IMPORT.json"
$AutomaticRollbackReport = Join-Path $ReportRoot "BUILD_0053_AUTOMATIC_ROLLBACK.json"

try {
    New-Item -ItemType Directory -Path $Extract -Force | Out-Null
    Expand-Archive -LiteralPath $PackagePath -DestinationPath $Extract -Force

    $Preflight = Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0053_Preflight.ps1"
    $Regression = Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0053_Windows_PS51_Regression.ps1"
    $Importer = Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0053_Import.ps1"

    & $Preflight `
        -PackagePath $PackagePath `
        -ReportPath (Join-Path $ReportRoot "BUILD_0053_PREFLIGHT.json")

    & $Importer `
        -PackagePath $PackagePath `
        -Repository $Repository `
        -BackupRoot $BackupRoot `
        -ReportPath (Join-Path $ReportRoot "BUILD_0053_CANONICAL_DRY_RUN.json")

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
    $Validator = Join-Path $Repository "13_Project_Genesis\Validators\validate_build_0053_repository.py"
    $ManifestPath = Join-Path $Repository "Documentation\Build_Records\0053\ASSET_INTENT_MANIFEST.json"
    $RepositoryReport = Join-Path $Repository "Documentation\Build_Records\0053\POST_IMPORT_REPOSITORY_VALIDATION.json"

    $ValidationArguments = @($Python.Prefix) + @(
        "-B",
        $Validator,
        $Repository,
        "--report",
        $RepositoryReport
    )
    & $Python.Path @ValidationArguments
    Assert-Exit "Build 0053 repository validation"

    $TestArguments = @($Python.Prefix) + @(
        "-B",
        "-m",
        "unittest",
        "discover",
        "-s",
        (Join-Path $Repository "13_Project_Genesis\Tests"),
        "-p",
        "test_build_0053_*.py",
        "-v"
    )
    & $Python.Path @TestArguments
    Assert-Exit "Build 0053 tests"

    $Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $Owned = @(
        @($Manifest.files | ForEach-Object { [string]$_.repository_path }) +
        @($Manifest.generated_files | ForEach-Object { [string]$_.repository_path }) |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
    )

    git -C $Repository add --all -- @Owned
    Assert-Exit "stage Build 0053 owned paths"

    $Observed = @(
        git -C $Repository diff --cached --name-only -- |
        ForEach-Object { $_.Trim().Replace("\", "/") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique
    )
    Assert-Exit "read staged Build 0053 paths"

    $Difference = @(Compare-Object -ReferenceObject $Owned -DifferenceObject $Observed)
    if ($Difference.Count -ne 0) {
        throw "Final staged path ownership does not exactly equal Build 0053 Asset Intent Manifest ownership."
    }

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
        (Join-Path $ReportRoot "BUILD_0053_STAGED_BYTE_EQUALITY.json")
    )
    & $Python.Path @ByteArguments
    Assert-Exit "raw staged byte equality"

    $CommitFile = Join-Path $Repository "Documentation\Build_Records\0053\COMMIT_MESSAGE.txt"
    if ((Get-Content -LiteralPath $CommitFile -Raw).Trim() -ne $ExpectedCommit) {
        throw "Reserved commit subject mismatch."
    }

    Write-Host ""
    Write-Host "BUILD_0053_CANONICAL_VALIDATED_AND_STAGED" -ForegroundColor Green
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
            Write-Host "BUILD_0053_AUTOMATIC_ROLLBACK_STATE_EXACT" -ForegroundColor Yellow
        }
        catch {
            throw (
                "Build 0053 post-import gate failed and automatic rollback also failed. " +
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
