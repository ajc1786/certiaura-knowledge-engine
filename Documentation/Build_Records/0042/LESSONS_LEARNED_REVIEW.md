# Build 0042 lessons-learned review

## Inherited preventive controls

- ASCII-only executable PowerShell and CMD files.
- Native PowerShell parser precheck before execution.
- Exact adjacent-package SHA-256 resolution; no broad Downloads/Dropbox/OneDrive search.
- No scalar indexing of an unnormalised executable-path pipeline.
- No CMD caret-pipeline escaping inside quoted PowerShell commands.
- No generic-list `return @($Records)` control-path pattern.
- Braced PowerShell interpolation before a colon.
- Central trailing-space/tab stripping and both Git diff checks.
- State-aware, ancestry-aware close-out resume.
- External backup before import and close-out writes.

## Build-specific anticipated risks

1. Trial exclusions could be misrepresented as approved contraindications.
2. Sponsor topline outcomes could be blended with peer-reviewed evidence.
3. Monitoring objects could drift into personal clinical instructions.
4. Cardiovascular or renal surrogate outcomes could be misrepresented as proven event reduction.

## Required close-out evidence

The close-out launcher must record defects, root causes, time lost, corrective actions, preventive controls, actual dry-run/apply results, backup path, register totals, validation results, tests, Git checks, import commit, Actions evidence and final checkpoint evidence.
