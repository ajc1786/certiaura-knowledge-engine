CERTIAURA BUILD 0038 — LOCAL REISSUE TOOL v2

Purpose
-------
This tool creates the corrected Build 0038 ZIP from the files already present
in the local Certiaura repository.

It is deliberately fail-closed. It will not create a ZIP when:
- FILE_INVENTORY.csv is missing or empty;
- an inventory file is missing;
- an unauthorised repository root is detected;
- a build-named wrapper folder is detected;
- JSON parsing fails;
- Python is unavailable or Python syntax validation fails;
- the generated ZIP is empty or structurally invalid.

How to run
----------
1. Extract this tool ZIP outside the Certiaura repository.
2. Right-click PowerShell and open normally.
3. Run:

   Set-ExecutionPolicy -Scope Process Bypass
   .\Reissue_Certiaura_Build_0038.ps1

Default repository:
C:\Users\enqui\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine

Default output:
C:\Users\enqui\Downloads\Certiaura_Build_0038_Asset_Register_Conflict_Fix.zip

Custom paths:
.\Reissue_Certiaura_Build_0038.ps1 `
  -RepositoryPath "C:\path\to\certiaura-knowledge-engine" `
  -OutputDirectory "C:\Users\enqui\Downloads"

After creation
--------------
Import the generated ZIP through Project Genesis and run DRY RUN only.
Proceed to Apply only when DRY_RUN_REPORT.json shows:
- valid: true
- applied: false
- total_conflicts: 0
- register_path: Documentation/Master_Asset_Register.csv

Exact commit message
--------------------
Add Certiaura Build 0038 repository restoration canonical routing and complete historical Master Asset Register reconciliation


v2 correction
-------------
Recognises the current FILE_INVENTORY.csv field `canonical_path` and future equivalent path-column variants.
