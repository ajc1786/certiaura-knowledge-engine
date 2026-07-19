[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$RepositoryPath = "C:\Users\enqui\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine",

    [Parameter(Mandatory = $false)]
    [string]$OutputDirectory = "$env:USERPROFILE\Downloads"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "BUILD 0038 REISSUE BLOCKED" -ForegroundColor Red
    Write-Host $Message -ForegroundColor Red
    exit 1
}

function Get-InventoryPathColumn($Rows) {
    if (-not $Rows -or $Rows.Count -eq 0) {
        Fail "FILE_INVENTORY.csv contains no rows."
    }

    $properties = @($Rows[0].PSObject.Properties.Name)
    $candidates = @(
        "canonical_path",
        "Canonical Path",
        "Repository Path",
        "repository_path",
        "Relative Path",
        "relative_path",
        "File Path",
        "file_path",
        "Path",
        "path",
        "Destination",
        "destination"
    )

    foreach ($candidate in $candidates) {
        if ($properties -contains $candidate) {
            return $candidate
        }
    }

    # Robust fallback for future inventory schema variants.
    foreach ($property in $properties) {
        $normalised = ($property -replace '[^A-Za-z0-9]', '').ToLowerInvariant()
        if ($normalised -in @(
            "canonicalpath",
            "repositorypath",
            "relativepath",
            "filepath",
            "path",
            "destination"
        )) {
            return $property
        }
    }

    Fail ("Could not identify the path column in FILE_INVENTORY.csv. Columns found: " + ($properties -join ", "))
}

function Normalize-RelativePath([string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $null
    }

    $normal = $Value.Trim().Replace("\", "/")
    while ($normal.StartsWith("./")) {
        $normal = $normal.Substring(2)
    }

    if ($normal.StartsWith("/") -or $normal -match "^[A-Za-z]:") {
        Fail "Inventory contains an absolute path: $Value"
    }

    if ($normal -split "/" | Where-Object { $_ -eq ".." }) {
        Fail "Inventory contains path traversal: $Value"
    }

    return $normal
}

$repo = [System.IO.Path]::GetFullPath($RepositoryPath)
if (-not (Test-Path -LiteralPath $repo -PathType Container)) {
    Fail "Repository not found: $repo"
}

$inventoryRel = "Documentation/Build_Records/0038/FILE_INVENTORY.csv"
$inventoryPath = Join-Path $repo ($inventoryRel.Replace("/", "\"))
if (-not (Test-Path -LiteralPath $inventoryPath -PathType Leaf)) {
    Fail "Required inventory not found: $inventoryPath"
}

$manifestPath = Join-Path $repo "Documentation\Build_Records\0038\BUILD_MANIFEST.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    Fail "Required Build 0038 manifest not found: $manifestPath"
}

$allowedRoots = @(
    "00_Governance",
    "01_Knowledge_Systems",
    "02_Peptides",
    "03_Biology",
    "04_Conditions",
    "05_Monitoring",
    "06_Evidence",
    "07_Goals",
    "08_Product_Passports",
    "09_Cost_Intelligence",
    "10_Marketplace",
    "11_Academy",
    "12_Reports",
    "13_Project_Genesis",
    "Assets",
    "Database",
    "Documentation",
    "Images",
    "Schemas",
    "Scripts",
    "Standards",
    "Templates"
)

$rows = @(Import-Csv -LiteralPath $inventoryPath)
$pathColumn = Get-InventoryPathColumn $rows

$relativePaths = New-Object System.Collections.Generic.List[string]
$seen = @{}

foreach ($row in $rows) {
    $relative = Normalize-RelativePath ([string]$row.$pathColumn)
    if ([string]::IsNullOrWhiteSpace($relative)) {
        continue
    }

    $root = ($relative -split "/")[0]
    if ($allowedRoots -notcontains $root) {
        Fail "Unauthorised repository root in inventory: $relative"
    }

    if ($root -like "Certiaura_Build_*" -or $root -match "^003[5-9]") {
        Fail "Prohibited build-wrapper root in inventory: $relative"
    }

    $key = $relative.ToLowerInvariant()
    if ($seen.ContainsKey($key)) {
        Fail "Duplicate or case-colliding inventory path: $relative"
    }

    $seen[$key] = $true
    $relativePaths.Add($relative)
}

if ($relativePaths.Count -eq 0) {
    Fail "No package paths were resolved from FILE_INVENTORY.csv."
}

# Ensure critical corrected Build 0038 files are included even if an older
# inventory omitted one. Each must already exist in the corrected repository.
$criticalPaths = @(
    "00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",
    "13_Project_Genesis/Import/asset_register_reconciler.py",
    "13_Project_Genesis/Import/historical_asset_backfill.py",
    "13_Project_Genesis/Import/repair_master_asset_register.py",
    "13_Project_Genesis/Import/transactional_build_import.py",
    "13_Project_Genesis/Import/Run_Master_Asset_Register_Repair.cmd",
    "Documentation/Build_Records/0038/ASSET_INTENT_MANIFEST.json",
    "Documentation/Build_Records/0038/BUILD_0038_READ_ME_FIRST.md",
    "Documentation/Build_Records/0038/BUILD_MANIFEST.json",
    "Documentation/Build_Records/0038/CONFLICT_POLICY.json",
    "Documentation/Build_Records/0038/FILE_INVENTORY.csv",
    "Documentation/Build_Records/0038/PACKAGE_CONTENT_SHA256.csv",
    "Documentation/Build_Records/0038/PROJECT_GENESIS_IMPORT_HOOK.json",
    "Documentation/Build_Records/0038/PROPOSED_NEXT_ACTION.md",
    "Documentation/Build_Records/0038/TEST_REPORT.txt",
    "Documentation/Build_Records/0038/VALIDATION_REPORT.md"
)

foreach ($critical in $criticalPaths) {
    $key = $critical.ToLowerInvariant()
    if (-not $seen.ContainsKey($key)) {
        $fullCritical = Join-Path $repo ($critical.Replace("/", "\"))
        if (-not (Test-Path -LiteralPath $fullCritical -PathType Leaf)) {
            Fail "Critical corrected Build 0038 file is missing: $critical"
        }
        $seen[$key] = $true
        $relativePaths.Add($critical)
    }
}

$missing = New-Object System.Collections.Generic.List[string]
foreach ($relative in $relativePaths) {
    $source = Join-Path $repo ($relative.Replace("/", "\"))
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        $missing.Add($relative)
    }
}

if ($missing.Count -gt 0) {
    $missingReport = Join-Path $OutputDirectory "Certiaura_Build_0038_Missing_Files.txt"
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $missing | Sort-Object | Set-Content -LiteralPath $missingReport -Encoding UTF8
    Fail "$($missing.Count) inventory files are missing. No ZIP was created. Review: $missingReport"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ([string]$manifest.build_number -ne "0038") {
    Fail "BUILD_MANIFEST.json is not Build 0038."
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$stageRoot = Join-Path $env:TEMP "Certiaura_Build_0038_Reissue_$stamp"
New-Item -ItemType Directory -Force -Path $stageRoot | Out-Null

try {
    foreach ($relative in $relativePaths) {
        $source = Join-Path $repo ($relative.Replace("/", "\"))
        $destination = Join-Path $stageRoot ($relative.Replace("/", "\"))

        $destinationDirectory = Split-Path -Parent $destination
        New-Item -ItemType Directory -Force -Path $destinationDirectory | Out-Null
        Copy-Item -LiteralPath $source -Destination $destination -Force
    }

    # Never package runtime backups, Git metadata, caches or an accidental nested ZIP.
    Get-ChildItem -LiteralPath $stageRoot -Recurse -Force |
        Where-Object {
            $_.Name -in @(".git", ".certiaura_backups", "__pycache__", "node_modules") -or
            $_.FullName.EndsWith("Documentation\Build_Records\0038\CONFLICT_POLICY.zip",
                [System.StringComparison]::OrdinalIgnoreCase)
        } |
        Sort-Object FullName -Descending |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

    # Parse every JSON file.
    $jsonFailures = New-Object System.Collections.Generic.List[string]
    foreach ($jsonFile in Get-ChildItem -LiteralPath $stageRoot -Recurse -File -Filter "*.json") {
        try {
            Get-Content -LiteralPath $jsonFile.FullName -Raw | ConvertFrom-Json | Out-Null
        }
        catch {
            $jsonFailures.Add($jsonFile.FullName.Substring($stageRoot.Length + 1))
        }
    }

    if ($jsonFailures.Count -gt 0) {
        Fail ("JSON validation failed: " + ($jsonFailures -join "; "))
    }

    # Validate Python syntax where Python is available.
    $pythonCommand = $null
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $pythonCommand = "py"
        $pythonArgsPrefix = @("-3")
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCommand = "python"
        $pythonArgsPrefix = @()
    }
    else {
        Fail "Python was not found. Build 0038 cannot pass the mandatory Python syntax gate."
    }

    $pythonFailures = New-Object System.Collections.Generic.List[string]
    foreach ($pythonFile in Get-ChildItem -LiteralPath $stageRoot -Recurse -File -Filter "*.py") {
        $args = @($pythonArgsPrefix + @("-m", "py_compile", $pythonFile.FullName))
        & $pythonCommand @args 2>$null
        if ($LASTEXITCODE -ne 0) {
            $pythonFailures.Add($pythonFile.FullName.Substring($stageRoot.Length + 1))
        }
    }

    Get-ChildItem -LiteralPath $stageRoot -Recurse -Directory -Filter "__pycache__" |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

    if ($pythonFailures.Count -gt 0) {
        Fail ("Python syntax validation failed: " + ($pythonFailures -join "; "))
    }

    # Recreate package checksums from the exact staged reissue.
    $checksumRel = "Documentation/Build_Records/0038/PACKAGE_CONTENT_SHA256.csv"
    $checksumPath = Join-Path $stageRoot ($checksumRel.Replace("/", "\"))

    $checksumRows = foreach ($file in Get-ChildItem -LiteralPath $stageRoot -Recurse -File | Sort-Object FullName) {
        $relative = $file.FullName.Substring($stageRoot.Length + 1).Replace("\", "/")
        if ($relative -ieq $checksumRel) {
            continue
        }

        $hash = Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256
        [PSCustomObject]@{
            RepositoryPath = $relative
            SHA256 = $hash.Hash.ToLowerInvariant()
            SizeBytes = $file.Length
        }
    }

    $checksumRows | Export-Csv -LiteralPath $checksumPath -NoTypeInformation -Encoding UTF8

    # Final structure check.
    $stagedFiles = @(Get-ChildItem -LiteralPath $stageRoot -Recurse -File)
    foreach ($file in $stagedFiles) {
        $relative = $file.FullName.Substring($stageRoot.Length + 1).Replace("\", "/")
        $root = ($relative -split "/")[0]
        if ($allowedRoots -notcontains $root) {
            Fail "Final staging contains unauthorised root: $relative"
        }
    }

    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $zipName = "Certiaura_Build_0038_Asset_Register_Conflict_Fix.zip"
    $zipPath = Join-Path $OutputDirectory $zipName

    if (Test-Path -LiteralPath $zipPath) {
        $archiveName = "Certiaura_Build_0038_Asset_Register_Conflict_Fix_PREVIOUS_$stamp.zip"
        Move-Item -LiteralPath $zipPath -Destination (Join-Path $OutputDirectory $archiveName)
    }

    Compress-Archive -Path (Join-Path $stageRoot "*") -DestinationPath $zipPath -CompressionLevel Optimal

    # Inspect the ZIP for a prohibited wrapper.
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        $entries = @($archive.Entries | Where-Object { -not [string]::IsNullOrWhiteSpace($_.Name) })
        if ($entries.Count -eq 0) {
            Fail "Generated ZIP is empty."
        }

        $entryRoots = @(
            $entries |
            ForEach-Object { ($_.FullName.Replace("\", "/") -split "/")[0] } |
            Sort-Object -Unique
        )

        foreach ($root in $entryRoots) {
            if ($allowedRoots -notcontains $root) {
                Fail "Generated ZIP contains unauthorised root: $root"
            }
        }
    }
    finally {
        $archive.Dispose()
    }

    $zipHash = Get-FileHash -LiteralPath $zipPath -Algorithm SHA256
    $hashPath = "$zipPath.sha256"
    "$($zipHash.Hash.ToLowerInvariant())  $zipName" |
        Set-Content -LiteralPath $hashPath -Encoding ASCII

    Write-Host ""
    Write-Host "BUILD 0038 REISSUE CREATED" -ForegroundColor Green
    Write-Host "ZIP:    $zipPath"
    Write-Host "SHA256: $($zipHash.Hash.ToLowerInvariant())"
    Write-Host "Files:  $($stagedFiles.Count)"
    Write-Host ""
    Write-Host "Next: import this ZIP through Project Genesis and run DRY RUN only." -ForegroundColor Yellow
}
finally {
    if (Test-Path -LiteralPath $stageRoot) {
        Remove-Item -LiteralPath $stageRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
