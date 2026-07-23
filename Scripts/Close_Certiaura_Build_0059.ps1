[CmdletBinding()]
param(
    [string]$Repository = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
    [string]$Owner = "ajc1786",
    [string]$RepositoryName = "certiaura-knowledge-engine",
    [string]$ReportRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0059"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$BuildNumber = "0059"
$Candidate = "RC1"
$Title = "tesamorelin governed review-board approvals, evidence-pack version control, challenge and appeal resolution, suspension recovery, periodic reassessment and reusable peptide-review operating model baseline"
$ExpectedPredecessor = "011f5a47d756d638b4c0c8b2e122628ff5a6d35a"
$ExpectedSubject = "Add Certiaura Build 0059 tesamorelin governed review-board approvals, evidence-pack version control, challenge and appeal resolution, suspension recovery, periodic reassessment and reusable peptide-review operating model baseline"
$WorkflowName = "Certiaura Repository Validation"
$Guard = Join-Path $PSScriptRoot "Invoke_Certiaura_Git_NonInteractive_Guard.ps1"
. $Guard

function Assert-Exit([string]$Name) {
    if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit code $LASTEXITCODE." }
}

Invoke-CertiauraGitNonInteractiveGuard -Repository $Repository -ScriptBlock {
    $Branch = (& git -C $Repository branch --show-current).Trim()
    Assert-Exit "read branch"
    if ($Branch -ne "main") { throw "Expected main branch." }

    & git -C $Repository fetch origin main --quiet
    Assert-Exit "fetch origin/main"

    $Head = (& git -C $Repository rev-parse HEAD).Trim()
    Assert-Exit "read HEAD"
    $Subject = (& git -C $Repository log -1 --format=%s).Trim()
    Assert-Exit "read subject"

    if ($Head -eq $ExpectedPredecessor) {
        $Dirty = @(& git -C $Repository diff --name-only)
        Assert-Exit "read unstaged"
        if ($Dirty.Count -ne 0) { throw "Unstaged changes exist." }

        $Untracked = @(& git -C $Repository ls-files --others --exclude-standard)
        Assert-Exit "read untracked"
        if ($Untracked.Count -ne 0) { throw "Untracked files exist." }

        $Staged = @(
            & git -C $Repository diff --cached --name-only |
                ForEach-Object { $_.Trim().Replace("\", "/") } |
                Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
                Sort-Object -Unique
        )
        Assert-Exit "read staged"

        $ManifestPath = Join-Path $Repository "Documentation\Build_Records\0059\ASSET_INTENT_MANIFEST.json"
        $Manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
        $Owned = @(
            @($Manifest.files | ForEach-Object { [string]$_.repository_path }) +
            @($Manifest.generated_files | ForEach-Object { [string]$_.repository_path }) |
                ForEach-Object { $_.Trim().Replace("\", "/") } |
                Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
                Sort-Object -Unique
        )
        if (@(Compare-Object -ReferenceObject $Owned -DifferenceObject $Staged).Count -ne 0) {
            throw "Staged Build 0059 path set is not exact."
        }

        & git -C $Repository diff --check
        Assert-Exit "git diff --check"
        & git -C $Repository diff --cached --check
        Assert-Exit "git diff --cached --check"

        & git -C $Repository commit -m $ExpectedSubject
        Assert-Exit "commit Build 0059"
    }
    elseif ($Subject -ne $ExpectedSubject) {
        throw "Repository is neither the Build 0058 predecessor nor an existing Build 0059 commit."
    }

    $Head = (& git -C $Repository rev-parse HEAD).Trim()
    Assert-Exit "read canonical HEAD"
    $Subject = (& git -C $Repository log -1 --format=%s).Trim()
    Assert-Exit "read canonical subject"
    if ($Subject -ne $ExpectedSubject) { throw "Build 0059 subject mismatch." }

    & git -C $Repository push origin main
    Assert-Exit "push origin/main"
    & git -C $Repository fetch origin main --quiet
    Assert-Exit "fetch after push"

    $Remote = (& git -C $Repository rev-parse origin/main).Trim()
    Assert-Exit "read origin/main"
    $Aligned = ($Head -eq $Remote)
    if (-not $Aligned) { throw "Local and origin/main differ." }

    $StatusBeforeEvidence = @(& git -C $Repository status --porcelain --untracked-files=all)
    Assert-Exit "status before evidence"
    if ($StatusBeforeEvidence.Count -ne 0) { throw "Repository is not clean after push." }

    Write-Host "BUILD_0059_GIT_NONINTERACTIVE_GUARD_VALIDATED"
    Write-Host "NO_MANUAL_GIT_OBJECT_CLEANUP_PROMPTS"
    Write-Host "BUILD_0059_COMMITTED_PUSHED"

    $Headers = @{
        Accept = "application/vnd.github+json"
        "User-Agent" = "Certiaura-Build-Closure"
        "X-GitHub-Api-Version" = "2022-11-28"
    }
    $Uri = ("https://api.github.com/repos/{0}/{1}/actions/runs?head_sha={2}&per_page=100") -f $Owner, $RepositoryName, $Head
    $Run = $null
    for ($Attempt = 1; $Attempt -le 60; $Attempt++) {
        $Response = Invoke-RestMethod -Uri $Uri -Headers $Headers -Method Get
        $Matches = @(
            $Response.workflow_runs |
                Where-Object {
                    $_.head_sha -eq $Head -and
                    $_.head_branch -eq "main" -and
                    $_.event -eq "push" -and
                    $_.name -eq $WorkflowName
                } |
                Sort-Object created_at -Descending
        )
        if ($Matches.Count -gt 0) {
            $Run = $Matches[0]
            if ($Run.status -eq "completed") { break }
        }
        Start-Sleep -Seconds 5
    }

    if ($null -eq $Run) { throw "No exact Actions run found." }
    if ($Run.status -ne "completed" -or $Run.conclusion -ne "success") {
        throw "Actions did not complete successfully."
    }
    if (-not $Run.id) { throw "Actions run ID missing." }
    if ([string]$Run.head_sha -ne $Head) { throw "Actions SHA does not match canonical commit." }

    $Evidence = [ordered]@{
        build_number = $BuildNumber
        candidate = $Candidate
        title = $Title
        canonical_commit = $Head
        commit_subject = $Subject
        run_id = [string]$Run.id
        workflow_name = [string]$Run.name
        run_attempt = [int]$Run.run_attempt
        branch = [string]$Run.head_branch
        event = [string]$Run.event
        status = [string]$Run.status
        conclusion = [string]$Run.conclusion
        created_at = [string]$Run.created_at
        updated_at = [string]$Run.updated_at
        actions_url = [string]$Run.html_url
        local_origin_aligned = $true
        repository_clean = $true
        git_noninteractive_guard = $true
        no_manual_cleanup_prompts = $true
        endpoint = "BUILD_0059_GITHUB_ACTIONS_GREEN"
        founder_ready_status = "BUILD_0059_READY_FOR_FOUNDER_GREEN"
    }

    New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
    $ExternalEvidence = Join-Path $ReportRoot "BUILD_0059_CLOSURE_EVIDENCE.json"
    $LocalEvidenceDirectory = Join-Path $Repository "Documentation\Build_Records\0059\Closure_Evidence"
    New-Item -ItemType Directory -Path $LocalEvidenceDirectory -Force | Out-Null
    $LocalEvidence = Join-Path $LocalEvidenceDirectory "BUILD_0059_CLOSURE_EVIDENCE.json"
    $Json = $Evidence | ConvertTo-Json -Depth 8
    $Json | Set-Content -LiteralPath $ExternalEvidence -Encoding UTF8
    $Json | Set-Content -LiteralPath $LocalEvidence -Encoding UTF8

    $ExternalCheck = Get-Content -LiteralPath $ExternalEvidence -Raw | ConvertFrom-Json
    $LocalCheck = Get-Content -LiteralPath $LocalEvidence -Raw | ConvertFrom-Json
    if ([string]$ExternalCheck.run_id -ne [string]$Run.id -or [string]$LocalCheck.run_id -ne [string]$Run.id) {
        throw "Persisted closure evidence run ID verification failed."
    }

    $StatusAfterEvidence = @(& git -C $Repository status --porcelain --untracked-files=all)
    Assert-Exit "status after evidence"
    if ($StatusAfterEvidence.Count -ne 0) {
        throw "Repository is not clean after writing ignored local closure evidence."
    }

    Write-Host "===== CERTIAURA_BUILD_0059_CLOSURE_EVIDENCE_BEGIN ====="
    Write-Host "Build number: $BuildNumber"
    Write-Host "Candidate: $Candidate"
    Write-Host "Build title: $Title"
    Write-Host "Canonical commit: $Head"
    Write-Host "Commit subject: $Subject"
    Write-Host "GitHub Actions run ID: $($Run.id)"
    Write-Host "Workflow: $($Run.name)"
    Write-Host "Run attempt: $($Run.run_attempt)"
    Write-Host "Branch: $($Run.head_branch)"
    Write-Host "Event: $($Run.event)"
    Write-Host "Status: $($Run.status)"
    Write-Host "Conclusion: $($Run.conclusion)"
    Write-Host "Created: $($Run.created_at)"
    Write-Host "Updated: $($Run.updated_at)"
    Write-Host "Actions URL: $($Run.html_url)"
    Write-Host "Local and origin/main aligned: TRUE"
    Write-Host "Repository clean: TRUE"
    Write-Host "Git non-interactive guard: VALIDATED"
    Write-Host "No manual Git cleanup prompts: TRUE"
    Write-Host "External evidence JSON: $ExternalEvidence"
    Write-Host "Local evidence JSON: $LocalEvidence"
    Write-Host "BUILD_0059_GITHUB_ACTIONS_GREEN"
    Write-Host "BUILD_0059_READY_FOR_FOUNDER_GREEN"
    Write-Host "FOUNDER_CONFIRMATION_READY: Reply with exact phrase GREEN"
    Write-Host "===== CERTIAURA_BUILD_0059_CLOSURE_EVIDENCE_END ====="
}
