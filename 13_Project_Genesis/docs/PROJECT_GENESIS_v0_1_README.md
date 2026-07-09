# Project Genesis v0.1 — Repository Automation

## Purpose
This is the first Certiaura automation layer.

It reduces the manual process from:

1. Download ZIP
2. Extract ZIP
3. Copy files
4. Open GitHub Desktop
5. Commit
6. Push

to:

1. Download and extract ZIP
2. Run one PowerShell command

## Tool included

`13_Project_Genesis/tools/stage-build-pack.ps1`

## What it does
- Copies a build pack into the repository
- Runs `git add .`
- Runs `git commit`
- Runs `git push origin main`

## Important
Use this only after reviewing that the build pack contents are correct.
