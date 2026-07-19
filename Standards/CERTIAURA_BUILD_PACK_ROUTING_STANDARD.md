# Certiaura Build Pack Routing Standard

**Build:** CERT-BUILD-0038  
**Status:** Locked implementation control  
**Effective date:** 2026-07-19

## Mandatory package structure

A downloadable ZIP may be named after its build, but its contents must begin at canonical repository-relative paths. A top-level build-name wrapper folder is prohibited.

Permitted root routes are:

- `00_Governance/`
- `01_Knowledge_Systems/`
- `02_Peptides/`
- `03_Biology/`
- `04_Conditions/`
- `05_Monitoring/`
- `06_Evidence/`
- `07_Goals/`
- `08_Product_Passports/`
- `09_Cost_Intelligence/`
- `10_Marketplace/`
- `11_Academy/`
- `12_Reports/`
- `13_Project_Genesis/`
- `Assets/`
- `Database/`
- `Documentation/`
- `Images/`
- `Schemas/`
- `Scripts/`
- `Standards/`
- `Templates/`

Build administration records must be stored at:

```text
Documentation/Build_Records/[BUILD_NUMBER]/
```

Generated Python cache files, compiled bytecode, temporary folders and local execution output must not be included.

## Import gate

Project Genesis must perform a dry run, validate routes, compare hashes, identify collisions, block silent destructive overwrites, create a recoverable checkpoint before applying changes, validate the repository after import, and emit an auditable import report.

## Build 0038 restoration scope

This package restores the canonical content of Builds 0035E, 0035F, 0035G, 0035H, 0035I, 0035J, 0035K and 0036 after their incorrectly routed root build folders were deleted. It retains each original build identity while correcting package routing.
