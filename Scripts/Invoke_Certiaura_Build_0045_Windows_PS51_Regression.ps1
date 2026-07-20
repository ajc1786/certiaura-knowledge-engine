[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$Package,
 [Parameter(Mandatory=$true)][string]$ExpectedPackageSha256,
 [Parameter(Mandatory=$true)][string]$ReportRoot,
 [string]$SourceRepository
)
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
$TempRoot=$null
function Assert-Exit{param([string]$Operation);if($LASTEXITCODE -ne 0){throw "$Operation failed with exit code $LASTEXITCODE."}}
function Get-Python{$P=Get-Command python -ErrorAction SilentlyContinue;if($null -eq $P){$P=Get-Command py -ErrorAction SilentlyContinue};if($null -eq $P){throw "Python was not found on PATH."};return $P}
function Write-AsciiFile{param([string]$Path,[string]$Text);$Parent=Split-Path $Path -Parent;New-Item -ItemType Directory -Path $Parent -Force|Out-Null;[IO.File]::WriteAllText($Path,$Text,[Text.Encoding]::ASCII)}
function New-SyntheticRepository{
 param([string]$Path)
 New-Item -ItemType Directory -Path $Path -Force|Out-Null
 $Files=@{
  "02_Peptides/CERT-PKS-000001_Retatrutide.md"="# Retatrutide`n";
  "05_Monitoring/CERT-MKS-000001_Monitoring.md"="# Monitoring`n";
  "12_Reports/Retatrutide/Patient_Interface/CERT-RKS-000004_Retatrutide_Patient_Facing_Interface_Baseline.md"="# Build 0044 interface`n";
  "13_Project_Genesis/AI/CERT-SYS-000851_Retatrutide_Controlled_Conversation_Workflow_Baseline.md"="# Build 0044 conversation`n";
  "Scripts/generate_retatrutide_patient_journey_report.py"="print('dependency')`n";
  "Scripts/query_retatrutide_knowledge.py"="print('dependency')`n";
  "Scripts/render_retatrutide_branded_report.py"="print('dependency')`n";
  "Scripts/run_retatrutide_controlled_conversation.py"="print('dependency')`n";
  "HISTORICAL_UNRELATED.txt"="preserve`n"
 }
 foreach($Pair in $Files.GetEnumerator()){Write-AsciiFile -Path (Join-Path $Path $Pair.Key) -Text $Pair.Value}
 $Columns=@("Universal Asset Identifier","Asset Name","Knowledge System","Asset Type","Status","Owner","Parent Assets","Last Review","Notes","Repository Path","Supporting Files","Version","Completion Percentage","Child Assets","Relationship List","Evidence Links","Report Links","Marketplace Links","Next Review","Change History","Build Provenance","Source Builds","Registration Basis","File SHA256","Last Updated")
 $Rows=@(
  [pscustomobject]@{"Universal Asset Identifier"="CERT-PKS-000001";"Asset Name"="Retatrutide";"Knowledge System"="PKS";"Asset Type"="Peptide";Status="ACTIVE";Owner="Certiaura";"Repository Path"="02_Peptides/CERT-PKS-000001_Retatrutide.md";Version="1.0.0"},
  [pscustomobject]@{"Universal Asset Identifier"="CERT-MKS-000001";"Asset Name"="Monitoring";"Knowledge System"="MKS";"Asset Type"="Monitoring";Status="ACTIVE";Owner="Certiaura";"Repository Path"="05_Monitoring/CERT-MKS-000001_Monitoring.md";Version="1.0.0"},
  [pscustomobject]@{"Universal Asset Identifier"="CERT-RKS-000004";"Asset Name"="Interface";"Knowledge System"="RKS";"Asset Type"="Report";Status="BASELINE";Owner="Certiaura";"Repository Path"="12_Reports/Retatrutide/Patient_Interface/CERT-RKS-000004_Retatrutide_Patient_Facing_Interface_Baseline.md";Version="1.0.0";"Build Provenance"="CERT-BUILD-0044";"Source Builds"="0044"},
  [pscustomobject]@{"Universal Asset Identifier"="CERT-SYS-000851";"Asset Name"="Conversation";"Knowledge System"="SYS";"Asset Type"="Platform";Status="BASELINE";Owner="Certiaura";"Repository Path"="13_Project_Genesis/AI/CERT-SYS-000851_Retatrutide_Controlled_Conversation_Workflow_Baseline.md";Version="1.0.0";"Build Provenance"="CERT-BUILD-0044";"Source Builds"="0044"}
 )
 $Complete=@();foreach($Row in $Rows){$O=[ordered]@{};foreach($C in $Columns){$V=$Row.PSObject.Properties[$C];$O[$C]=if($null -eq $V){""}else{[string]$V.Value}};$Complete+=[pscustomobject]$O}
 $Register=Join-Path $Path "Documentation/Master_Asset_Register.csv";New-Item -ItemType Directory -Path (Split-Path $Register -Parent) -Force|Out-Null;$Complete|Export-Csv -LiteralPath $Register -NoTypeInformation -Encoding UTF8
 $Historical=Join-Path $Path "03_Biology/CERT-BKS-000045_Synthetic_Historical_Text.md";New-Item -ItemType Directory -Path (Split-Path $Historical -Parent) -Force|Out-Null;[IO.File]::WriteAllText($Historical,"historical line with trailing space `r`n",[Text.Encoding]::ASCII)
 git -C $Path init|Out-Null;git -C $Path config user.email "regression@certiaura.local";git -C $Path config user.name "Certiaura Regression";git -C $Path add -A;git -C $Path commit -m "Synthetic baseline"|Out-Null;Assert-Exit "Synthetic baseline commit"
}
try{
 if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -lt 1){throw "Windows PowerShell 5.1 is required."}
 if(-not(Test-Path -LiteralPath $Package -PathType Leaf)){throw "Package not found: $Package"}
 $Actual=(Get-FileHash -LiteralPath $Package -Algorithm SHA256).Hash;if($Actual -ne $ExpectedPackageSha256.ToUpperInvariant()){throw "Package SHA-256 mismatch."}
 New-Item -ItemType Directory -Path $ReportRoot -Force|Out-Null
 $TempRoot=Join-Path $env:TEMP ("Certiaura_0045_PS51_"+[guid]::NewGuid().ToString("N"));$PackageRoot=Join-Path $TempRoot "package";$Repository=Join-Path $TempRoot "repository";$BackupRoot=Join-Path $TempRoot "external_backups";$Outputs=Join-Path $TempRoot "outputs"
 Expand-Archive -LiteralPath $Package -DestinationPath $PackageRoot -Force
 $ParserFailures=@();$Scripts=@(Get-ChildItem -LiteralPath $PackageRoot -Recurse -Filter "*.ps1" -File)
 foreach($Script in $Scripts){$Bytes=[IO.File]::ReadAllBytes($Script.FullName);if(@($Bytes|Where-Object{$_ -gt 127}).Count -gt 0){$ParserFailures+="$($Script.Name): non-ASCII"};$Tokens=$null;$Errors=$null;[Management.Automation.Language.Parser]::ParseFile($Script.FullName,[ref]$Tokens,[ref]$Errors)|Out-Null;foreach($E in @($Errors)){$ParserFailures+="$($Script.Name): $($E.Message)"}}
 if($ParserFailures.Count -gt 0){$ParserFailures|ForEach-Object{Write-Host $_ -ForegroundColor Red};throw "Windows PowerShell 5.1 parser precheck failed."}
 New-SyntheticRepository -Path $Repository
 $Python=Get-Python
 & (Join-Path $PackageRoot "Scripts/Invoke_Certiaura_Build_0045_Preflight.ps1") -Package $Package -Report (Join-Path $ReportRoot "BUILD_0045_PREFLIGHT.json")
 $Internal=Join-Path $Repository ".certiaura_backups/build_legacy/Documentation";New-Item -ItemType Directory -Path $Internal -Force|Out-Null;Copy-Item (Join-Path $Repository "Documentation/Master_Asset_Register.csv") (Join-Path $Internal "Master_Asset_Register.csv")
 & $Python.Source -B (Join-Path $PackageRoot "Scripts/import_certiaura_build_0045.py") --package $Package --repository $Repository --report (Join-Path $ReportRoot "BUILD_0045_NEGATIVE_INTERNAL_BACKUP.json")
 if($LASTEXITCODE -eq 0){throw "Internal backup negative fixture did not block import."}
 Remove-Item (Join-Path $Repository ".certiaura_backups") -Recurse -Force
 & (Join-Path $PackageRoot "Scripts/Invoke_Certiaura_Build_0045_Import.ps1") -Package $Package -Repository $Repository -Report (Join-Path $ReportRoot "BUILD_0045_DRY_RUN.json")
 $Dry=Get-Content (Join-Path $ReportRoot "BUILD_0045_DRY_RUN.json") -Raw|ConvertFrom-Json;if($Dry.transaction_status -ne "DRY_RUN_VALIDATED" -or @($Dry.allocations).Count -ne 3){throw "Build 0045 synthetic dry-run invalid."}
 & (Join-Path $PackageRoot "Scripts/Invoke_Certiaura_Build_0045_Import.ps1") -Package $Package -Repository $Repository -Report (Join-Path $ReportRoot "BUILD_0045_APPLY.json") -BackupRoot $BackupRoot -Apply
 $Apply=Get-Content (Join-Path $ReportRoot "BUILD_0045_APPLY.json") -Raw|ConvertFrom-Json;if($Apply.transaction_status -ne "APPLIED_VALIDATED"){throw "Build 0045 synthetic apply invalid."};if(([IO.Path]::GetFullPath($Apply.backup_path)).StartsWith([IO.Path]::GetFullPath($Repository),[StringComparison]::OrdinalIgnoreCase)){throw "Backup was created inside repository."}
 & $Python.Source -B (Join-Path $Repository "13_Project_Genesis/Validators/validate_build_0045_retatrutide_longitudinal_review_handoff.py") $Repository --report (Join-Path $ReportRoot "BUILD_0045_VALIDATOR.json");Assert-Exit "Build 0045 validator"
 & $Python.Source -B -m unittest discover -s (Join-Path $Repository "13_Project_Genesis/Tests") -p "test_build_0045_retatrutide_longitudinal_review_handoff.py";Assert-Exit "Build 0045 tests"
 New-Item -ItemType Directory -Path $Outputs -Force|Out-Null
 $Journey=Join-Path $Outputs "journey.json";$Schedule=Join-Path $Outputs "schedule.json";$HandoffJson=Join-Path $Outputs "handoff.json";$HandoffMd=Join-Path $Outputs "handoff.md"
 & $Python.Source -B (Join-Path $Repository "Scripts/build_retatrutide_longitudinal_journey.py") (Join-Path $Repository "05_Monitoring/Retatrutide/Examples/longitudinal_journey_seed.example.json") --output $Journey;Assert-Exit "Journey generation"
 & $Python.Source -B (Join-Path $Repository "Scripts/generate_retatrutide_review_schedule.py") $Journey --policy (Join-Path $Repository "13_Project_Genesis/AI/retatrutide_review_scheduling_policy.json") --as-of "2026-07-20T12:00:00Z" --output $Schedule;Assert-Exit "Review schedule generation"
 & $Python.Source -B (Join-Path $Repository "Scripts/generate_retatrutide_clinician_handoff.py") $Journey $Schedule --output-json $HandoffJson --output-md $HandoffMd;Assert-Exit "Clinician handoff generation"
 $IdentifiableOutput=Join-Path $Outputs "should_not_exist.json"
 $SavedErrorActionPreference=$ErrorActionPreference
 $IdentifiableExit=$null
 try{
  $ErrorActionPreference="Continue"
  & $Python.Source -B (Join-Path $Repository "Scripts/record_retatrutide_longitudinal_event.py") (Join-Path $Repository "05_Monitoring/Retatrutide/Examples/longitudinal_event_identifiable.example.json") --journey $Journey --output $IdentifiableOutput 2>$null
  $IdentifiableExit=$LASTEXITCODE
 }finally{
  $ErrorActionPreference=$SavedErrorActionPreference
 }
 if($null -eq $IdentifiableExit){throw "Identifiable-input negative fixture did not return an exit code."}
 if($IdentifiableExit -eq 0){throw "Identifiable input was not rejected."}
 if(Test-Path -LiteralPath $IdentifiableOutput -PathType Leaf){throw "Rejected identifiable input created an output file."}
 $Urgent=Join-Path $Outputs "urgent_journey.json";& $Python.Source -B (Join-Path $Repository "Scripts/record_retatrutide_longitudinal_event.py") (Join-Path $Repository "05_Monitoring/Retatrutide/Examples/longitudinal_event_urgent.example.json") --journey $Journey --output $Urgent;Assert-Exit "Urgent event routing";$UrgentData=Get-Content $Urgent -Raw|ConvertFrom-Json;if($UrgentData.journey_state -ne "LOCKED_URGENT_ROUTING"){throw "Urgent event did not lock journey."};if(@($UrgentData.events).Count -ne 5){throw "Raw seed append did not preserve and enrich all events."};if(@($UrgentData.events|Where-Object{-not $_.event_id -or -not $_.event_hash}).Count -gt 0){throw "Raw seed events were not deterministically enriched."}
 $Artifacts=@(Get-ChildItem -LiteralPath $Repository -Recurse -Force|Where-Object{$_.Name -eq "__pycache__" -or $_.Extension -in @(".pyc",".pyo")});if($Artifacts.Count -gt 0){throw "Runtime artifacts detected."}
 git -C $Repository diff --check;Assert-Exit "git diff --check";git -C $Repository add -A;Assert-Exit "git stage";git -C $Repository diff --cached --check;Assert-Exit "git diff --cached --check"
 Write-Host "BUILD 0045 WINDOWS POWERSHELL 5.1 REGRESSION: PASS" -ForegroundColor Green
}catch{Write-Host "BUILD 0045 WINDOWS POWERSHELL 5.1 REGRESSION: FAIL" -ForegroundColor Red;throw}finally{if($TempRoot -and (Test-Path $TempRoot)){Remove-Item $TempRoot -Recurse -Force -ErrorAction SilentlyContinue}}
