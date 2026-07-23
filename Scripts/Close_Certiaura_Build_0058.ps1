[CmdletBinding()]
param(
 [string]$Repository="$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",
 [string]$Owner="ajc1786",[string]$RepositoryName="certiaura-knowledge-engine",
 [string]$ReportRoot="$env:USERPROFILE\OneDrive\Documents\CERTIAURA\Build_Reports\0058"
)
Set-StrictMode -Version Latest; $ErrorActionPreference="Stop"
$ExpectedPredecessor="2bf6c2f9fcaacfc0d0942045178269a1241253ee"; $ExpectedSubject="Add Certiaura Build 0058 tesamorelin multi-source evidence quality assessment, conflicting-evidence adjudication, longitudinal signal recurrence, controlled amendment and pilot continuation governance baseline"; $WorkflowName="Certiaura Repository Validation"
$Guard=Join-Path $PSScriptRoot "Invoke_Certiaura_Git_NonInteractive_Guard.ps1"; . $Guard
function Assert-Exit([string]$Name){if($LASTEXITCODE -ne 0){throw "$Name failed with exit code $LASTEXITCODE."}}
Invoke-CertiauraGitNonInteractiveGuard -Repository $Repository -ScriptBlock {
 $Branch=(& git -C $Repository branch --show-current).Trim(); Assert-Exit "read branch"; if($Branch -ne "main"){throw "Expected main branch."}
 & git -C $Repository fetch origin main --quiet; Assert-Exit "fetch origin/main"
 $Head=(& git -C $Repository rev-parse HEAD).Trim(); Assert-Exit "read HEAD"; $Subject=(& git -C $Repository log -1 --format=%s).Trim(); Assert-Exit "read subject"
 if($Head -eq $ExpectedPredecessor){
  $Dirty=@(& git -C $Repository diff --name-only); Assert-Exit "read unstaged"; if($Dirty.Count -ne 0){throw "Unstaged changes exist."}
  $Untracked=@(& git -C $Repository ls-files --others --exclude-standard); Assert-Exit "read untracked"; if($Untracked.Count -ne 0){throw "Untracked files exist."}
  $Staged=@(& git -C $Repository diff --cached --name-only | ForEach-Object { $_.Trim().Replace("\", "/") } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique); Assert-Exit "read staged"
  $ManifestPath=Join-Path $Repository "Documentation\Build_Records\0058\ASSET_INTENT_MANIFEST.json"; $Manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
  $Owned=@(@($Manifest.files|ForEach-Object{[string]$_.repository_path})+@($Manifest.generated_files|ForEach-Object{[string]$_.repository_path})|ForEach-Object{$_.Trim().Replace("\", "/")}|Where-Object{-not [string]::IsNullOrWhiteSpace($_)}|Sort-Object -Unique)
  if($Owned.Count -ne 94){throw "Build 0058 manifest must own exactly 94 paths."}
  if(@(Compare-Object -ReferenceObject $Owned -DifferenceObject $Staged).Count -ne 0){throw "Staged Build 0058 path set is not exact."}
  & git -C $Repository diff --check; Assert-Exit "git diff --check"; & git -C $Repository diff --cached --check; Assert-Exit "git diff --cached --check"
  & git -C $Repository commit -m $ExpectedSubject; Assert-Exit "commit Build 0058"
 } elseif($Subject -ne $ExpectedSubject){throw "Repository is neither the Build 0057 predecessor nor an existing Build 0058 commit."}
 $Head=(& git -C $Repository rev-parse HEAD).Trim(); $Subject=(& git -C $Repository log -1 --format=%s).Trim(); if($Subject -ne $ExpectedSubject){throw "Build 0058 subject mismatch."}
 & git -C $Repository push origin main; Assert-Exit "push origin/main"; & git -C $Repository fetch origin main --quiet; Assert-Exit "fetch after push"
 $Remote=(& git -C $Repository rev-parse origin/main).Trim(); if($Head -ne $Remote){throw "Local and origin/main differ."}
 $Status=@(& git -C $Repository status --porcelain --untracked-files=all); Assert-Exit "status"; if($Status.Count -ne 0){throw "Repository is not clean."}
 Write-Host "BUILD_0058_GIT_NONINTERACTIVE_GUARD_VALIDATED" -ForegroundColor Green
Write-Host "NO_MANUAL_GIT_OBJECT_CLEANUP_PROMPTS" -ForegroundColor Green
Write-Host "BUILD_0058_COMMITTED_PUSHED" -ForegroundColor Green; Write-Host "Canonical commit:"; Write-Host $Head
 $Headers=@{Accept="application/vnd.github+json";"User-Agent"="Certiaura-Build-Closure";"X-GitHub-Api-Version"="2022-11-28"}
 $Uri=("https://api.github.com/repos/{0}/{1}/actions/runs?head_sha={2}&per_page=100") -f $Owner,$RepositoryName,$Head; $Run=$null
 for($Attempt=1;$Attempt -le 30;$Attempt++){ $Response=Invoke-RestMethod -Uri $Uri -Headers $Headers -Method Get; $Matches=@($Response.workflow_runs|Where-Object{$_.head_sha -eq $Head -and $_.head_branch -eq "main" -and $_.event -eq "push" -and $_.name -eq $WorkflowName}|Sort-Object created_at -Descending); if($Matches.Count -gt 0){$Run=$Matches[0];if($Run.status -eq "completed"){break}}; Start-Sleep -Seconds 5 }
 if($null -eq $Run){throw "No exact Actions run found."}; if($Run.status -ne "completed" -or $Run.conclusion -ne "success"){throw "Actions did not complete successfully."}; if(-not $Run.id){throw "Actions run ID missing."}
 New-Item -ItemType Directory -Path $ReportRoot -Force|Out-Null; $Evidence=[ordered]@{build_number="0058";canonical_commit=$Head;commit_subject=$Subject;run_id=[string]$Run.id;workflow_name=[string]$Run.name;status=[string]$Run.status;conclusion=[string]$Run.conclusion;run_attempt=[int]$Run.run_attempt;branch=[string]$Run.head_branch;event=[string]$Run.event;created_at=[string]$Run.created_at;updated_at=[string]$Run.updated_at;repository_clean=$true;git_noninteractive_guard=$true;founder_phrase_required="GREEN"}
 $Evidence|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $ReportRoot "BUILD_0058_GITHUB_ACTIONS_GREEN.json") -Encoding UTF8
 Write-Host "BUILD_0058_GITHUB_ACTIONS_GREEN" -ForegroundColor Green; Write-Host "Run ID:"; Write-Host $Run.id; Write-Host "Canonical commit:"; Write-Host $Head
}
