[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Package,[Parameter(Mandatory=$true)][string]$ReportRoot)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -lt 1) { throw "This release regression must run on Windows PowerShell 5.1." }
$Python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue }
if ($null -eq $Python) { throw "Python was not found on PATH." }
New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
$Root = Join-Path $env:TEMP ("Certiaura_0043_PS51_" + [guid]::NewGuid().ToString("N"))
$Repo = Join-Path $Root "synthetic_repo"
$Backup = Join-Path $Root "backups"
$Extract = Join-Path $Root "package"
try {
 New-Item -ItemType Directory -Path $Repo -Force | Out-Null
 git -C $Repo init | Out-Null
 git -C $Repo config user.email "regression@certiaura.local"
 git -C $Repo config user.name "Certiaura Regression"
 git -C $Repo config core.autocrlf true
 git -C $Repo config core.safecrlf false
 New-Item -ItemType Directory -Path (Join-Path $Repo "Documentation") -Force | Out-Null
 "Unrelated historical file`n" | Set-Content -LiteralPath (Join-Path $Repo "HISTORICAL_UNRELATED.txt") -Encoding ASCII
 $Cols = "Universal Asset Identifier,Asset Name,Knowledge System,Asset Type,Status,Owner,Parent Assets,Last Review,Notes,Repository Path,Supporting Files,Version,Completion Percentage,Child Assets,Relationship List,Evidence Links,Report Links,Marketplace Links,Next Review,Change History,Build Provenance,Source Builds,Registration Basis,File SHA256,Last Updated"
 $Cols | Set-Content -LiteralPath (Join-Path $Repo "Documentation\Master_Asset_Register.csv") -Encoding ASCII
 New-Item -ItemType Directory -Path (Join-Path $Repo "06_Evidence\Retatrutide") -Force | Out-Null
 "# Retatrutide reviewed evidence baseline`nStatus: REVIEWED`nClaim: Synthetic regression evidence only.`n" | Set-Content -LiteralPath (Join-Path $Repo "06_Evidence\Retatrutide\CERT-EKS-999998_Synthetic.md") -Encoding ASCII
 New-Item -ItemType Directory -Path (Join-Path $Repo "05_Monitoring\Retatrutide") -Force | Out-Null
 "# Retatrutide monitoring baseline`nStatus: REVIEWED`nMonitoring: Synthetic regression source only.`n" | Set-Content -LiteralPath (Join-Path $Repo "05_Monitoring\Retatrutide\CERT-MKS-999998_Synthetic.md") -Encoding ASCII
 git -C $Repo add -A; git -C $Repo commit -m "Synthetic history" | Out-Null
 Expand-Archive -LiteralPath $Package -DestinationPath $Extract -Force
 $ParserFailures = New-Object System.Collections.Generic.List[string]
 Get-ChildItem -LiteralPath $Extract -Recurse -Filter "*.ps1" -File | ForEach-Object {
  $NonAsciiBytes = @([System.IO.File]::ReadAllBytes($_.FullName) | Where-Object { $_ -gt 127 })
  if ($NonAsciiBytes.Count -gt 0) { $ParserFailures.Add(($_.FullName + ": non-ASCII bytes are prohibited in Windows PowerShell 5.1 release scripts")) }
  $Tokens = $null
  $ParseErrors = $null
  [System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$Tokens,[ref]$ParseErrors) | Out-Null
  if (@($ParseErrors).Count -gt 0) {
   foreach ($ParseError in @($ParseErrors)) { $ParserFailures.Add(($_.FullName + ": " + $ParseError.Message)) }
  }
 }
 if ($ParserFailures.Count -gt 0) { $ParserFailures | ForEach-Object { Write-Host $_ -ForegroundColor Red }; throw "Windows PowerShell 5.1 parser precheck failed." }
 $Preflight = Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0043_Preflight.ps1"
 $Importer = Join-Path $Extract "Scripts\Invoke_Certiaura_Build_0043_Import.ps1"
 $Dry = Join-Path $ReportRoot "BUILD_0043_PS51_DRY_RUN.json"
 $Apply = Join-Path $ReportRoot "BUILD_0043_PS51_APPLY.json"
 & $Preflight -Package $Package -Report (Join-Path $ReportRoot "BUILD_0043_PS51_PREFLIGHT.json")
 & $Importer -Package $Package -Repository $Repo -Report $Dry
 $DryObj = Get-Content -LiteralPath $Dry -Raw | ConvertFrom-Json
 if ($DryObj.valid -ne $true -or $DryObj.transaction_status -ne "DRY_RUN_VALIDATED") { throw "Synthetic dry-run failed." }
 & $Importer -Package $Package -Repository $Repo -Report $Apply -BackupRoot $Backup -Apply
 $ApplyObj = Get-Content -LiteralPath $Apply -Raw | ConvertFrom-Json
 if ($ApplyObj.valid -ne $true -or $ApplyObj.applied -ne $true) { throw "Synthetic apply failed." }
 & $Python.Source -B (Join-Path $Repo "13_Project_Genesis\Validators\validate_build_0043_retatrutide_patient_journey_ai.py") $Repo --report (Join-Path $ReportRoot "BUILD_0043_PS51_VALIDATOR.json")
 if ($LASTEXITCODE -ne 0) { throw "Validator failed." }
 & $Python.Source -B -m unittest discover -s (Join-Path $Repo "13_Project_Genesis\Tests") -p "test_build_0043_retatrutide_patient_journey_ai.py"
 if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
 $OutputRoot = Join-Path $Root "outputs"
 New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
 & $Python.Source -B (Join-Path $Repo "Scripts\generate_retatrutide_patient_journey_report.py") (Join-Path $Repo "12_Reports\Retatrutide\Examples\valid_patient_profile.example.json") --repository $Repo --output-json (Join-Path $OutputRoot "report.json") --output-md (Join-Path $OutputRoot "report.md")
 if ($LASTEXITCODE -ne 0) { throw "Report generation failed." }
 & $Python.Source -B (Join-Path $Repo "Scripts\query_retatrutide_knowledge.py") (Join-Path $Repo "13_Project_Genesis\AI\Examples\valid_evidence_query.example.json") --repository $Repo --output (Join-Path $OutputRoot "query.json")
 if ($LASTEXITCODE -ne 0) { throw "AI query integration failed." }
 git -C $Repo add -A
 git -C $Repo diff --check
 if ($LASTEXITCODE -ne 0) { throw "git diff --check failed." }
 git -C $Repo diff --cached --check
 if ($LASTEXITCODE -ne 0) { throw "git diff --cached --check failed." }
 $Artefacts = @(Get-ChildItem -LiteralPath $Repo -Recurse -Force | Where-Object { $_.Name -eq "__pycache__" -or $_.Extension -eq ".pyc" -or $_.Extension -eq ".pyo" })
 if ($Artefacts.Count -gt 0) { throw "Runtime artefacts detected in synthetic repository." }
 $Result = [ordered]@{ valid=$true; powershell_version=$PSVersionTable.PSVersion.ToString(); parser_precheck="PASS"; dry_run="PASS"; apply="PASS"; validator="PASS"; tests="PASS"; report_generation="PASS"; ai_query="PASS"; git_checks="PASS"; unrelated_history_preserved=(Test-Path -LiteralPath (Join-Path $Repo "HISTORICAL_UNRELATED.txt")); backup_created=(Test-Path -LiteralPath $ApplyObj.backup_path) }
 $Result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $ReportRoot "BUILD_0043_WINDOWS_PS51_REGRESSION.json") -Encoding UTF8
 Write-Host "BUILD 0043 WINDOWS POWERSHELL 5.1 REGRESSION: PASS" -ForegroundColor Green
}
finally { if (Test-Path -LiteralPath $Root) { Remove-Item -LiteralPath $Root -Recurse -Force -ErrorAction SilentlyContinue } }
