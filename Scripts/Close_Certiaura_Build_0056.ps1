[CmdletBinding()]
param(
    [string]$Repository = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
    [string]$Owner = "ajc1786",
    [string]$RepositoryName = "certiaura-knowledge-engine",
    [string]$ReportRoot = "$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0056"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ExpectedSubject = "Add Certiaura Build 0056 tesamorelin evidence corpus mapping, biological and safety boundary definition, target-specific data contracts, monitoring model and controlled pilot acceptance baseline"
$WorkflowName = "Certiaura Repository Validation"

function Assert-Exit {
    param([Parameter(Mandatory = $true)][string]$Name)
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE."
    }
}

$Head = (git -C $Repository rev-parse HEAD).Trim()
Assert-Exit "read HEAD"
$Subject = (git -C $Repository log -1 --format=%s).Trim()
Assert-Exit "read subject"
if ($Subject -ne $ExpectedSubject) {
    throw "Build 0056 commit subject mismatch."
}

git -C $Repository fetch origin main --quiet
Assert-Exit "fetch origin/main"
$Remote = (git -C $Repository rev-parse origin/main).Trim()
Assert-Exit "read origin/main"
if ($Head -ne $Remote) {
    throw "Local HEAD does not equal origin/main."
}

$Dirty = @(git -C $Repository status --porcelain --untracked-files=all)
Assert-Exit "read status"
if ($Dirty.Count -ne 0) {
    throw "Repository is not clean."
}

$Headers = @{
    Accept = "application/vnd.github+json"
    "User-Agent" = "Certiaura-Build-Closure"
    "X-GitHub-Api-Version" = "2022-11-28"
}
$Uri = (
    "https://api.github.com/repos/{0}/{1}/actions/runs" +
    "?head_sha={2}&per_page=100"
) -f $Owner, $RepositoryName, $Head

$Run = $null
for ($LookupAttempt = 1; $LookupAttempt -le 30; $LookupAttempt++) {
    $Response = Invoke-RestMethod -Uri $Uri -Headers $Headers -Method Get
    $MatchingRuns = @(
        $Response.workflow_runs |
            Where-Object {
                $_.head_sha -eq $Head -and
                $_.head_branch -eq "main" -and
                $_.event -eq "push" -and
                $_.name -eq $WorkflowName
            } |
            Sort-Object created_at -Descending
    )
    if ($MatchingRuns.Count -gt 0) {
        $Run = $MatchingRuns[0]
        if ($Run.status -eq "completed") {
            break
        }
    }
    Start-Sleep -Seconds 5
}

if ($null -eq $Run) {
    throw "No exact GitHub Actions run found for canonical Build 0056 commit."
}
if ($Run.status -ne "completed") {
    throw "GitHub Actions run did not complete during verification."
}
if ($Run.conclusion -ne "success") {
    throw "GitHub Actions run did not conclude successfully."
}
if (-not $Run.id) {
    throw "GitHub Actions run ID is missing."
}
if ($Run.head_sha -ne $Head) {
    throw "GitHub Actions run SHA does not match canonical Build 0056 commit."
}

New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
$Evidence = [ordered]@{
    build_number = "0056"
    canonical_commit = $Head
    commit_subject = $Subject
    run_id = [string]$Run.id
    workflow_name = [string]$Run.name
    status = [string]$Run.status
    conclusion = [string]$Run.conclusion
    run_attempt = [int]$Run.run_attempt
    branch = [string]$Run.head_branch
    event = [string]$Run.event
    created_at = [string]$Run.created_at
    updated_at = [string]$Run.updated_at
    local_head = $Head
    origin_main = $Remote
    repository_clean = $true
    founder_phrase_required = "GREEN"
}
$Path = Join-Path $ReportRoot "BUILD_0056_GITHUB_ACTIONS_GREEN.json"
$Evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Path -Encoding UTF8

Write-Host ""
Write-Host "BUILD_0056_GITHUB_ACTIONS_GREEN" -ForegroundColor Green
Write-Host "Run ID:"
Write-Host $Run.id
Write-Host "Canonical commit:"
Write-Host $Head
Write-Host "Workflow:"
Write-Host $Run.name
Write-Host "Status / conclusion:"
Write-Host ($Run.status + " / " + $Run.conclusion)
Write-Host "Run attempt:"
Write-Host $Run.run_attempt
Write-Host "Evidence report:"
Write-Host $Path
