Set-StrictMode -Version Latest
function Get-CertiauraGitLocalConfigState {
    param([Parameter(Mandatory=$true)][string]$Repository,[Parameter(Mandatory=$true)][string]$Key)
    $Values = @(& git -C $Repository config --local --get-all $Key 2>$null)
    $Code = $LASTEXITCODE
    if ($Code -ne 0 -and $Code -ne 1) { throw "Unable to read local Git config: $Key" }
    return [pscustomobject]@{ Key=$Key; Existed=($Code -eq 0); Values=@($Values) }
}
function Restore-CertiauraGitLocalConfigState {
    param([Parameter(Mandatory=$true)][string]$Repository,[Parameter(Mandatory=$true)]$State)
    & git -C $Repository config --local --unset-all ([string]$State.Key) 2>$null
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne 5) { throw "Unable to clear local Git config: $($State.Key)" }
    if ([bool]$State.Existed) {
        foreach ($Value in @($State.Values)) {
            & git -C $Repository config --local --add ([string]$State.Key) ([string]$Value)
            if ($LASTEXITCODE -ne 0) { throw "Unable to restore local Git config: $($State.Key)" }
        }
    }
}
function Invoke-CertiauraGitNonInteractiveGuard {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][string]$Repository,[Parameter(Mandatory=$true)][scriptblock]$ScriptBlock)
    $Keys=@("gc.auto","maintenance.auto","gc.autoDetach")
    $States=@(); $PriorPrompt=$env:GIT_TERMINAL_PROMPT
    try {
        foreach($Key in $Keys){ $States += Get-CertiauraGitLocalConfigState -Repository $Repository -Key $Key }
        & git -C $Repository config --local gc.auto 0; if($LASTEXITCODE -ne 0){throw "Unable to disable gc.auto"}
        & git -C $Repository config --local maintenance.auto false; if($LASTEXITCODE -ne 0){throw "Unable to disable maintenance.auto"}
        & git -C $Repository config --local gc.autoDetach false; if($LASTEXITCODE -ne 0){throw "Unable to disable gc.autoDetach"}
        $env:GIT_TERMINAL_PROMPT="0"
        & $ScriptBlock
    }
    finally {
        $RestoreErrors=@()
        foreach($State in @($States)) { try { Restore-CertiauraGitLocalConfigState -Repository $Repository -State $State } catch { $RestoreErrors += $_.Exception.Message } }
        if($null -eq $PriorPrompt){Remove-Item Env:GIT_TERMINAL_PROMPT -ErrorAction SilentlyContinue}else{$env:GIT_TERMINAL_PROMPT=$PriorPrompt}
        if($RestoreErrors.Count -gt 0){throw ("Git guard restoration failed: "+($RestoreErrors -join "; "))}
    }
}
