# How to Use Project Genesis v0.1

## One-time setup

Copy the `13_Project_Genesis` folder into your repository:

```text
C:\Users\enqui\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine
```

Commit and push it once using GitHub Desktop.

## Normal use for future Build Packs

1. Download the next Build Pack ZIP from ChatGPT.
2. Extract it to a temporary folder, for example:

```text
C:\Users\enqui\Downloads\Certiaura_Build_0002
```

3. Open PowerShell.
4. Run this command, adjusting the build pack path if needed:

```powershell
Set-Location "C:\Users\enqui\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine\13_Project_Genesis\tools"

.\stage-build-pack.ps1 -BuildPackPath "C:\Users\enqui\Downloads\Certiaura_Build_0002" -CommitMessage "Build 0002 Retatrutide expansion"
```

## If PowerShell blocks the script

Run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then run the script again.

## Safety rule
Do not run the script on a build pack unless you are happy for it to be committed and pushed to GitHub.
