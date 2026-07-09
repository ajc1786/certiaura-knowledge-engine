param(
    [Parameter(Mandatory=$true)]
    [string]$BuildPackPath,

    [Parameter(Mandatory=$true)]
    [string]$CommitMessage
)

$ErrorActionPreference = "Stop"

Write-Host "CERTIAURA PROJECT GENESIS v0.1" -ForegroundColor Cyan
Write-Host "Repository Automation Started" -ForegroundColor Cyan

# Resolve repository root as the parent of this script location if run from inside repo
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptPath "..\..")

Write-Host "Repository root: $RepoRoot"

if (!(Test-Path $BuildPackPath)) {
    throw "Build pack path does not exist: $BuildPackPath"
}

# Copy files into repository root
Write-Host "Copying build pack into repository..."
Copy-Item -Path (Join-Path $BuildPackPath "*") -Destination $RepoRoot -Recurse -Force

# Move to repo root
Set-Location $RepoRoot

# Confirm git exists
git --version | Out-Null

Write-Host "Checking repository status..."
git status --short

# Add, commit and push
Write-Host "Adding files..."
git add .

$changes = git status --short
if ([string]::IsNullOrWhiteSpace($changes)) {
    Write-Host "No changes detected. Nothing to commit." -ForegroundColor Yellow
    exit 0
}

Write-Host "Committing changes..."
git commit -m "$CommitMessage"

Write-Host "Pushing to GitHub..."
git push origin main

Write-Host "DONE: Build pack committed and pushed." -ForegroundColor Green
