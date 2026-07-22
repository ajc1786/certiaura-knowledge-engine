[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RepositoryPath,
    [Parameter(Mandatory = $true)][string]$PackagePath,
    [Parameter(Mandatory = $true)][string]$ExpectedPackageSha256,
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
            foreach ($FieldName in @("transaction_status","rollback_completed","failure_code","rollback_reason","backup_path")) {
                $Details += $FieldName + "=" + (Get-ReportPropertyValue -Object $ReportObject -Name $FieldName)
            }
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

$PythonCommand = Resolve-PythonCommand
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Temporary = Join-Path $env:TEMP ("Certiaura_0052_RC6_Canonical_" + [guid]::NewGuid().ToString("N"))
try {
    Expand-Archive -LiteralPath $PackagePath -DestinationPath $Temporary -Force
    $ManifestPath = Join-Path $Temporary "Documentation\Build_Records\0052\ASSET_INTENT_MANIFEST.json"
    $EvidenceScript = Join-Path $Temporary "13_Project_Genesis\Release\derive_build_0051_predecessor_evidence.py"
    $ImporterPath = Join-Path $Temporary "13_Project_Genesis\Import\run_build_0052_import.py"
    $EvidenceRoot = Join-Path $ReportRootPath ("BUILD_0052_RC6_CANONICAL_EVIDENCE_" + $Timestamp)
    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$EvidenceScript,"--repository",$RepositoryPath,"--current-manifest",$ManifestPath,"--output-root",$EvidenceRoot,"--package-sha256",$ExpectedPackageSha256)
    $EvidenceResult = Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args
    Assert-NativeSuccess $EvidenceResult "Canonical predecessor evidence"
    $EvidenceReport = Join-Path $EvidenceRoot "PREDECESSOR_CANONICAL_EVIDENCE.json"
    $DryRunReport = Join-Path $ReportRootPath ("BUILD_0052_RC6_CANONICAL_DRY_RUN_" + $Timestamp + ".json")
    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$ImporterPath,"--repository",$RepositoryPath,"--package",$Temporary,"--report",$DryRunReport,"--predecessor-evidence",$EvidenceReport,"--package-sha256",$ExpectedPackageSha256)
    Assert-NativeSuccess (Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args) "Canonical dry run"
    $RollbackReport = Join-Path $ReportRootPath ("BUILD_0052_RC6_CANONICAL_ROLLBACK_" + $Timestamp + ".json")
    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$ImporterPath,"--repository",$RepositoryPath,"--package",$Temporary,"--report",$RollbackReport,"--predecessor-evidence",$EvidenceReport,"--package-sha256",$ExpectedPackageSha256,"--apply","--backup-root",$BackupRootPath,"--simulate-post-apply-failure")
    $Rollback = Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args
    if ($Rollback.ExitCode -ne 3) { throw "Canonical forced rollback failed: $($Rollback.Output -join [Environment]::NewLine)" }
    Assert-NativeOutputContains -Result $Rollback -RequiredToken "BUILD_0052_TRANSACTION_ROLLED_BACK" -Name "Canonical forced rollback"
    $ApplyReport = Join-Path $ReportRootPath ("BUILD_0052_RC6_CANONICAL_APPLY_" + $Timestamp + ".json")
    $Args = @(); $Args += @($PythonCommand.Prefix); $Args += @("-B",$ImporterPath,"--repository",$RepositoryPath,"--package",$Temporary,"--report",$ApplyReport,"--predecessor-evidence",$EvidenceReport,"--package-sha256",$ExpectedPackageSha256,"--apply","--backup-root",$BackupRootPath)
    $ApplyResult = Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Args
    Assert-TransactionalSuccess $ApplyResult "Canonical clean reapply" $ApplyReport
    Write-Host "BUILD_0052_RC6_CANONICAL_IMPORT_APPLIED" -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $Temporary) { Remove-Item -LiteralPath $Temporary -Recurse -Force -ErrorAction SilentlyContinue }
}
