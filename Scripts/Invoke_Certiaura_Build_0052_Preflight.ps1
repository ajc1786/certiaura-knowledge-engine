[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PackagePath,
    [Parameter(Mandatory = $true)][string]$ExpectedPackageSha256,
    [Parameter(Mandatory = $true)][string]$ReportPath
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

function Assert-NativeSuccess {
    param([Parameter(Mandatory = $true)]$Result,[Parameter(Mandatory = $true)][string]$Name)
    if ($Result.ExitCode -ne 0) {
        throw "$Name failed with exit code $($Result.ExitCode): $($Result.Output -join [Environment]::NewLine)"
    }
}

$Actual = (Get-FileHash -LiteralPath $PackagePath -Algorithm SHA256).Hash
if ($Actual -ne $ExpectedPackageSha256.ToUpperInvariant()) { throw "Package SHA mismatch." }
$PythonCommand = Resolve-PythonCommand
$Temporary = Join-Path $env:TEMP ("Certiaura_0052_RC6_Preflight_" + [guid]::NewGuid().ToString("N"))
try {
    Expand-Archive -LiteralPath $PackagePath -DestinationPath $Temporary -Force
    $PreflightPath = Join-Path $Temporary "13_Project_Genesis\Release\run_build_0052_preflight.py"
    $Arguments = @(); $Arguments += @($PythonCommand.Prefix); $Arguments += @("-B",$PreflightPath,$Temporary,"--report",$ReportPath)
    $Result = Invoke-NativeCommand -FilePath $PythonCommand.Path -Arguments $Arguments
    Assert-NativeSuccess $Result "Build 0052 RC6 preflight"
    Write-Host "BUILD_0052_RC6_PACKAGE_PREFLIGHT_VALIDATED" -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $Temporary) { Remove-Item -LiteralPath $Temporary -Recurse -Force -ErrorAction SilentlyContinue }
}
