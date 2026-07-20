[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Package,[Parameter(Mandatory=$true)][string]$ExpectedPackageSha256,[Parameter(Mandatory=$true)][string]$ReportRoot,[string]$SourceRepository)
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
  "05_Monitoring/Retatrutide/Longitudinal_Journey/CERT-MKS-000196_Retatrutide_Longitudinal_Journey_Tracking_Baseline.md"="# Build 0045 journey`n";
  "05_Monitoring/Retatrutide/Review_Scheduling/CERT-MKS-000197_Retatrutide_Review_Scheduling_Baseline.md"="# Build 0045 schedule`n";
  "12_Reports/Retatrutide/Clinician_Handoff/CERT-RKS-000005_Retatrutide_Clinician_Handoff_Baseline.md"="# Build 0045 handoff`n";
  "Scripts/build_retatrutide_longitudinal_journey.py"="print('dependency')`n";
  "Scripts/generate_retatrutide_review_schedule.py"="print('dependency')`n";
  "Scripts/generate_retatrutide_clinician_handoff.py"="print('dependency')`n";
  "HISTORICAL_UNRELATED.txt"="preserve`n"
 }
 foreach($Pair in $Files.GetEnumerator()){Write-AsciiFile -Path (Join-Path $Path $Pair.Key) -Text $Pair.Value}
 $Columns=@("Universal Asset Identifier","Asset Name","Knowledge System","Asset Type","Status","Owner","Parent Assets","Last Review","Notes","Repository Path","Supporting Files","Version","Completion Percentage","Child Assets","Relationship List","Evidence Links","Report Links","Marketplace Links","Next Review","Change History","Build Provenance","Source Builds","Registration Basis","File SHA256","Last Updated")
 $Rows=@(
  [pscustomobject]@{"Universal Asset Identifier"="CERT-PKS-000001";"Asset Name"="Retatrutide";"Knowledge System"="PKS";"Asset Type"="Peptide";Status="ACTIVE";Owner="Certiaura";"Repository Path"="02_Peptides/CERT-PKS-000001_Retatrutide.md";Version="1.0.0"},
  [pscustomobject]@{"Universal Asset Identifier"="CERT-MKS-000196";"Asset Name"="Journey";"Knowledge System"="MKS";"Asset Type"="Monitoring";Status="BASELINE";Owner="Certiaura";"Repository Path"="05_Monitoring/Retatrutide/Longitudinal_Journey/CERT-MKS-000196_Retatrutide_Longitudinal_Journey_Tracking_Baseline.md";Version="1.0.0";"Build Provenance"="CERT-BUILD-0045";"Source Builds"="0045"},
  [pscustomobject]@{"Universal Asset Identifier"="CERT-MKS-000197";"Asset Name"="Schedule";"Knowledge System"="MKS";"Asset Type"="Monitoring";Status="BASELINE";Owner="Certiaura";"Repository Path"="05_Monitoring/Retatrutide/Review_Scheduling/CERT-MKS-000197_Retatrutide_Review_Scheduling_Baseline.md";Version="1.0.0";"Build Provenance"="CERT-BUILD-0045";"Source Builds"="0045"},
  [pscustomobject]@{"Universal Asset Identifier"="CERT-RKS-000005";"Asset Name"="Handoff";"Knowledge System"="RKS";"Asset Type"="Report";Status="BASELINE";Owner="Certiaura";"Repository Path"="12_Reports/Retatrutide/Clinician_Handoff/CERT-RKS-000005_Retatrutide_Clinician_Handoff_Baseline.md";Version="1.0.0";"Build Provenance"="CERT-BUILD-0045";"Source Builds"="0045"}
 )
 $Complete=@();foreach($Row in $Rows){$O=[ordered]@{};foreach($C in $Columns){$V=$Row.PSObject.Properties[$C];$O[$C]=if($null -eq $V){""}else{[string]$V.Value}};$Complete+=[pscustomobject]$O}
 $Register=Join-Path $Path "Documentation/Master_Asset_Register.csv";New-Item -ItemType Directory -Path (Split-Path $Register -Parent) -Force|Out-Null;$Complete|Export-Csv -LiteralPath $Register -NoTypeInformation -Encoding UTF8
 $Historical=Join-Path $Path "03_Biology/CERT-BKS-000046_Synthetic_Historical_Text.md";New-Item -ItemType Directory -Path (Split-Path $Historical -Parent) -Force|Out-Null;[IO.File]::WriteAllText($Historical,"historical line with trailing space `r`n",[Text.Encoding]::ASCII)
 git -C $Path init|Out-Null;git -C $Path config user.email "regression@certiaura.local";git -C $Path config user.name "Certiaura Regression";git -C $Path add -A;git -C $Path commit -m "Synthetic baseline"|Out-Null;Assert-Exit "Synthetic baseline commit"
}
try{
 if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -lt 1){throw "Windows PowerShell 5.1 is required."}
 if(-not(Test-Path -LiteralPath $Package -PathType Leaf)){throw "Package not found: $Package"}
 $Actual=(Get-FileHash -LiteralPath $Package -Algorithm SHA256).Hash;if(-not [string]::Equals($Actual.Trim(),$ExpectedPackageSha256.Trim(),[StringComparison]::OrdinalIgnoreCase)){throw "Package SHA-256 mismatch."}
 New-Item -ItemType Directory -Path $ReportRoot -Force|Out-Null
 $TempRoot=Join-Path $env:TEMP ("Certiaura_0046_PS51_"+[guid]::NewGuid().ToString("N"));$PackageRoot=Join-Path $TempRoot "package";$Repository=Join-Path $TempRoot "repository";$BackupRoot=Join-Path $TempRoot "external_backups";$Outputs=Join-Path $TempRoot "outputs"
 Expand-Archive -LiteralPath $Package -DestinationPath $PackageRoot -Force
 $ParserFailures=@();$Scripts=@(Get-ChildItem -LiteralPath $PackageRoot -Recurse -Filter "*.ps1" -File)
 foreach($Script in $Scripts){$Bytes=[IO.File]::ReadAllBytes($Script.FullName);if(@($Bytes|Where-Object{$_ -gt 127}).Count -gt 0){$ParserFailures+="$($Script.Name): non-ASCII"};$Tokens=$null;$Errors=$null;[Management.Automation.Language.Parser]::ParseFile($Script.FullName,[ref]$Tokens,[ref]$Errors)|Out-Null;foreach($E in @($Errors)){$ParserFailures+="$($Script.Name): $($E.Message)"}}
 if($ParserFailures.Count -gt 0){$ParserFailures|ForEach-Object{Write-Host $_ -ForegroundColor Red};throw "Windows PowerShell 5.1 parser precheck failed."}
 New-SyntheticRepository -Path $Repository
 $Historical=Join-Path $Repository "03_Biology/CERT-BKS-000046_Synthetic_Historical_Text.md"
 $Python=Get-Python
 & (Join-Path $PackageRoot "Scripts/Invoke_Certiaura_Build_0046_Preflight.ps1") -Package $Package -Report (Join-Path $ReportRoot "BUILD_0046_PREFLIGHT.json")
 $Internal=Join-Path $Repository ".certiaura_backups/build_legacy/Documentation";New-Item -ItemType Directory -Path $Internal -Force|Out-Null;Copy-Item (Join-Path $Repository "Documentation/Master_Asset_Register.csv") (Join-Path $Internal "Master_Asset_Register.csv")
 $SavedErrorActionPreference=$ErrorActionPreference;$ErrorActionPreference="Continue";try{& $Python.Source -B (Join-Path $PackageRoot "Scripts/import_certiaura_build_0046.py") --package $Package --repository $Repository --report (Join-Path $ReportRoot "BUILD_0046_NEGATIVE_INTERNAL_BACKUP.json");$InternalExit=$LASTEXITCODE}finally{$ErrorActionPreference=$SavedErrorActionPreference}
 if($InternalExit -eq 0){throw "Internal backup negative fixture did not block import."}
 Remove-Item (Join-Path $Repository ".certiaura_backups") -Recurse -Force
 & (Join-Path $PackageRoot "Scripts/Invoke_Certiaura_Build_0046_Import.ps1") -Package $Package -Repository $Repository -Report (Join-Path $ReportRoot "BUILD_0046_DRY_RUN.json")
 $Dry=Get-Content (Join-Path $ReportRoot "BUILD_0046_DRY_RUN.json") -Raw|ConvertFrom-Json;if($Dry.transaction_status -ne "DRY_RUN_VALIDATED" -or @($Dry.allocations).Count -ne 3){throw "Build 0046 synthetic dry-run invalid."}
 & (Join-Path $PackageRoot "Scripts/Invoke_Certiaura_Build_0046_Import.ps1") -Package $Package -Repository $Repository -Report (Join-Path $ReportRoot "BUILD_0046_APPLY.json") -BackupRoot $BackupRoot -Apply
 $Apply=Get-Content (Join-Path $ReportRoot "BUILD_0046_APPLY.json") -Raw|ConvertFrom-Json;if($Apply.transaction_status -ne "APPLIED_VALIDATED"){throw "Build 0046 synthetic apply invalid."};if(([IO.Path]::GetFullPath($Apply.backup_path)).StartsWith([IO.Path]::GetFullPath($Repository),[StringComparison]::OrdinalIgnoreCase)){throw "Backup was created inside repository."}
 & $Python.Source -B (Join-Path $Repository "13_Project_Genesis/Validators/validate_build_0046_retatrutide_analytics_visualisation_alerting.py") $Repository --report (Join-Path $ReportRoot "BUILD_0046_VALIDATOR.json");Assert-Exit "Build 0046 validator"
 & $Python.Source -B -m unittest discover -s (Join-Path $Repository "13_Project_Genesis/Tests") -p "test_build_0046_retatrutide_analytics_visualisation_alerting.py";Assert-Exit "Build 0046 tests"
 New-Item -ItemType Directory -Path $Outputs -Force|Out-Null;$Analytics=Join-Path $Outputs "analytics.json";$TrendJson=Join-Path $Outputs "trend.json";$TrendSvg=Join-Path $Outputs "trend.svg";$Alert=Join-Path $Outputs "alert.json"
 & $Python.Source -B (Join-Path $Repository "Scripts/analyze_retatrutide_longitudinal_outcomes.py") (Join-Path $Repository "05_Monitoring/Retatrutide/Analytics/Examples/analytics_journey.example.json") --policy (Join-Path $Repository "13_Project_Genesis/AI/retatrutide_controlled_alerting_policy.json") --output $Analytics;Assert-Exit "Analytics"
 & $Python.Source -B (Join-Path $Repository "Scripts/render_retatrutide_outcome_trends.py") $Analytics --output-json $TrendJson --output-svg $TrendSvg;Assert-Exit "Trend rendering"
 & $Python.Source -B (Join-Path $Repository "Scripts/evaluate_retatrutide_controlled_alerts.py") (Join-Path $Repository "05_Monitoring/Retatrutide/Analytics/Examples/analytics_journey.example.json") $Analytics (Join-Path $Repository "05_Monitoring/Retatrutide/Analytics/Examples/review_schedule.example.json") --policy (Join-Path $Repository "13_Project_Genesis/AI/retatrutide_controlled_alerting_policy.json") --output $Alert;Assert-Exit "Controlled alert"
 $Rejected=Join-Path $Outputs "rejected.json";$SavedErrorActionPreference=$ErrorActionPreference;$ErrorActionPreference="Continue";try{& $Python.Source -B (Join-Path $Repository "Scripts/analyze_retatrutide_longitudinal_outcomes.py") (Join-Path $Repository "05_Monitoring/Retatrutide/Analytics/Examples/analytics_identifiable.example.json") --policy (Join-Path $Repository "13_Project_Genesis/AI/retatrutide_controlled_alerting_policy.json") --output $Rejected;$IdentifierExit=$LASTEXITCODE}finally{$ErrorActionPreference=$SavedErrorActionPreference}
 if($IdentifierExit -eq 0){throw "Identifier input was not rejected."};if(Test-Path $Rejected){throw "Rejected identifier input created output."}
 $Artifacts=@(Get-ChildItem $Repository -Recurse -Force|Where-Object{$_.Name -eq "__pycache__" -or $_.Extension -in @(".pyc",".pyo")});if($Artifacts.Count -gt 0){throw "Runtime artifacts detected."}
 if((Get-Content $Historical -Raw) -notmatch "historical line"){throw "Historical fixture changed."}
 git -C $Repository diff --check;Assert-Exit "git diff --check";git -C $Repository add -A;Assert-Exit "git stage";git -C $Repository diff --cached --check;Assert-Exit "git diff --cached --check"
 Write-Host "BUILD 0046 WINDOWS POWERSHELL 5.1 REGRESSION: PASS" -ForegroundColor Green
}catch{Write-Host "BUILD 0046 WINDOWS POWERSHELL 5.1 REGRESSION: FAIL" -ForegroundColor Red;throw}finally{if($TempRoot -and (Test-Path $TempRoot)){Remove-Item $TempRoot -Recurse -Force -ErrorAction SilentlyContinue}}
