# CERTIAURA LOCKED BUILD CONTINUITY AND CHECKPOINT

**Document ID:** CERT-GOV-CONT-002  
**Version:** 1.4.0  
**Status:** LOCKED — ACTIVE  
**Effective date:** 2026-07-19  
**Last updated:** 2026-07-19  
**Authority:** Explicit founder instruction from Aidan Coleman  
**Canonical repository path:** `00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md`  
**GPT Project use:** Upload this file to the Certiaura GPT Project sources and replace it with the latest version whenever the continuation checkpoint is updated.

---

## 1. Purpose

This document is the locked operational amendment for:

- Certiaura build-pack creation;
- repository-relative file routing;
- build naming and numbering;
- Git commit naming;
- Project Genesis import behaviour;
- Master Asset Register reconciliation and automatic updating;
- build status interpretation;
- continuity between chats;
- maintenance of the current next planned action.

It exists to stop future chats, assistants, developers or build tools from:

- recreating previously settled controls;
- packaging builds inside build-named wrapper folders;
- depositing build folders in the repository root;
- importing formal assets without reconciling the existing Master Asset Register;
- creating a competing or duplicate asset register;
- changing naming or commit conventions;
- issuing unnecessary micro-builds;
- losing the current build position;
- skipping an agreed next action;
- inventing a different project direction without an explicit founder instruction.

This document **amends and operationalises** the existing Certiaura governance baseline. It does not replace the Master Project Charter or create a competing governance system.

---

## 2. Mandatory read order for every new Certiaura chat

Before proposing, creating, repackaging or continuing any Certiaura build, the assistant must read the newest available versions of:

1. `CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md`
2. `CERTIAURA_REFERENCE_PACK_READ_FIRST.md`
3. `CERTIAURA_MASTER_PROJECT_CHARTER.md`
4. `CERTIAURA_LOCKED_DECISIONS_REFERENCE.md`, where available
5. `CERTIAURA_CONTINUITY_AND_CHANGE_CONTROL.md`
6. `CERTIAURA_CURRENT_STATE_BASELINE.md` or the current equivalent
7. The existing Master Asset Register at its current canonical repository path
8. The latest installed build record and latest pending build record

The assistant must use the **latest explicit founder instruction** where it conflicts with an older document.

The assistant must not rely on chat memory alone when the project source files are available.

---

## 3. Source-of-truth hierarchy

The current source-of-truth model remains:

- **GitHub:** canonical repository and version-controlled project record;
- **OneDrive:** synced working copy and backup;
- **ChatGPT:** production environment;
- **Project Genesis:** controlled build import, validation and repository-management platform;
- **This document:** locked build-production rules and live continuation checkpoint.

A build is not canonically implemented merely because a ZIP has been generated. Canonical implementation requires the applicable stages to be completed and recorded.

---

## 4. Locked build-status model

Every build must use these states consistently:

| State | Meaning |
|---|---|
| `PLANNED` | Agreed future work, not yet authorised for production |
| `GREEN_AUTHORISED` | Founder has authorised production |
| `GENERATED` | Build pack has been created and validated outside the canonical repository |
| `DELIVERED` | ZIP and exact commit message have been issued to the founder |
| `IMPORTED` | Project Genesis has merged the package into canonical repository paths |
| `REPOSITORY_VALIDATED` | Repository checks have passed after import |
| `COMMITTED_PUSHED` | Exact commit has been committed and pushed |
| `ACTIONS_GREEN_CLOSED` | GitHub Actions are green and the build is closed |

### Interpretation of the founder's word `green`

Unless the surrounding message explicitly says otherwise, a founder response of **green** after a delivered build means:

1. the delivered build is accepted for installation/close-out; and
2. the proposed next action is authorised to proceed.

A future assistant must still avoid falsely claiming `COMMITTED_PUSHED` or `ACTIONS_GREEN_CLOSED` unless that status is evidenced or expressly confirmed.

---

## 5. Locked build-numbering convention

### 5.1 New integrated work packages

Use a new whole build number for a materially distinct integrated capability:

```text
0036
0037
0038
0039
```

### 5.2 Lettered suffixes

Use suffix letters only where builds are genuinely:

- subdivisions of one parent work package;
- tightly coupled phases of one original scope;
- sequential extensions that remain inside the same work package.

Example:

```text
0035D
0035E
0035F
```

### 5.3 Corrections and repackaging

A packaging correction, routing correction or non-functional reissue must:

- retain the original build number;
- retain the full agreed build title;
- be identified in the build record as a corrected/reissued package;
- not consume a new build number unless the correction introduces a materially new capability.

### 5.4 Dependency recording

Related builds must record dependencies in metadata and manifests. Relatedness alone does not justify keeping all future work under one parent number.

---

## 6. Locked build optimisation standard

Future Certiaura builds must default to **larger integrated work-package builds**, not narrow micro-builds.

Each build should normally include the end-to-end capability required to become operational:

- workflow and state model;
- schemas and data contracts;
- templates and checklists;
- validators;
- valid, conditional and deliberately defective examples;
- automated tests;
- registers;
- audit and change-control records;
- dashboards or reporting outputs;
- Project Genesis integration;
- repository update instructions;
- rollback and recovery controls where relevant.

Split a build only when scientific, legal, regulatory, technical, security or repository risk makes separation materially safer.

---

## 7. Locked downloadable ZIP naming convention

Every future downloadable build file must use:

```text
Certiaura_Build_[BUILD_NUMBER]_[Short_Descriptive_Title].zip
```

Mandatory rules:

- preserve the complete build number and suffix letter;
- use underscores only;
- use no spaces;
- avoid unnecessary punctuation;
- keep the description concise and recognisable;
- target a complete filename length of **80 characters or fewer**;
- treat **100 characters as the absolute maximum**;
- shorten the filename title without changing the full agreed build title used in the commit message and build record.

Example:

```text
Certiaura_Build_0038_Repo_Routing_Migration.zip
```

---

## 8. Locked ZIP internal structure

### 8.1 No build-named wrapper folder

The downloadable ZIP filename may identify the build, but the ZIP contents must **not** be wrapped inside a build-named top-level folder.

Prohibited:

```text
Certiaura_Build_0038_Repo_Routing_Migration/
    00_Governance/
    13_Project_Genesis/
```

Required:

```text
00_Governance/
13_Project_Genesis/
Documentation/
Scripts/
```

### 8.2 Repository-relative routing

The ZIP root must mirror the canonical repository structure. Importing the ZIP must merge files directly into their correct existing repository destinations.

Current permitted canonical root routes include:

```text
00_Governance/
01_Knowledge_Systems/
02_Peptides/
03_Biology/
04_Conditions/
05_Monitoring/
06_Evidence/
07_Goals/
08_Product_Passports/
09_Cost_Intelligence/
10_Marketplace/
11_Academy/
12_Reports/
13_Project_Genesis/
Assets/
Database/
Documentation/
Images/
Schemas/
Scripts/
Standards/
Templates/
```

A build must not invent another repository-root folder unless an explicit founder-approved architecture amendment authorises it.

### 8.3 Build records

Build-specific administrative records must be routed to:

```text
Documentation/Build_Records/[BUILD_NUMBER]/
```

This includes, where applicable:

- read-me-first file;
- build manifest;
- package inventory;
- validation report;
- decision record;
- proposed change-log entry;
- test report;
- checksum record;
- import report;
- rollback report.

Build records must not create root-level build folders.

---

## 9. Locked Project Genesis import controls

Project Genesis Build Pack Import must perform the following controls before modifying the repository:

1. Reject any ZIP containing a top-level build-name wrapper directory.
2. Validate every proposed destination against the canonical route allowlist.
3. Detect duplicate paths and case-only filename collisions.
4. Hash existing and incoming files.
5. Skip identical files with an audit entry.
6. Prevent silent overwriting of non-identical files.
7. Classify conflicts as:
   - approved replacement;
   - merge required;
   - supersession;
   - quarantine;
   - rejection.
8. Locate and read the existing canonical Master Asset Register.
9. Block the import if the Master Asset Register is missing, ambiguous, unreadable or structurally invalid.
10. Read the incoming Asset Intent Manifest and classify every package file.
11. Produce a dry-run Asset Register Change Report showing creations, updates, supersessions, retirements, unchanged assets, relationship changes and identifier allocations.
12. Create a pre-import backup or recoverable Git checkpoint covering both repository files and register state.
13. Produce a dry-run routing and collision report.
14. Merge approved files into canonical paths.
15. Reconcile and update the Master Asset Register in the same controlled transaction.
16. Update the relationship index, applicable system registers, change log, Production Dashboard, build record and continuation checkpoint.
17. Run full repository validation, including asset-to-register and relationship referential-integrity checks.
18. Produce a post-import report.
19. Roll back files, register entries, relationships and control records where validation fails.
20. Prevent commit and push when mandatory validation or reconciliation fails.

Automation may route, compare, hash, classify, allocate identifiers, reconcile, validate, block and report. It must not silently approve a destructive overwrite, conceal a collision, create a competing register or leave a formal asset outside the canonical Master Asset Register.

---

## 10. Locked Master Asset Register reconciliation and transactional update standard

### 10.1 One canonical register

The existing Certiaura Master Asset Register is the sole canonical asset register.

This amendment does not authorise:

- a parallel register;
- a replacement register;
- a build-specific master register;
- an unapproved relocation of the existing register.

Project Genesis must resolve the existing register from the repository configuration or its established canonical location. If it cannot resolve one unique valid register, import must stop.

### 10.2 Mandatory Asset Intent Manifest

Every build pack must include a machine-readable Asset Intent Manifest under:

```text
Documentation/Build_Records/[BUILD_NUMBER]/
```

Every package file must be classified as one of:

- `FORMAL_ASSET`
- `SUPPORTING_FILE`
- `SCHEMA`
- `SCRIPT`
- `TEMPLATE`
- `TEST`
- `EXAMPLE`
- `BUILD_RECORD`
- `NON_ASSET_ADMIN`

For each `FORMAL_ASSET`, the manifest must state, where applicable:

- repository-relative path;
- asset title;
- asset type;
- Knowledge System;
- intended action;
- existing Universal Asset Identifier, where known;
- proposed version and status;
- owner;
- parent and child assets;
- relationship declarations;
- evidence, report, marketplace and Product Passport links;
- last-review and next-review fields;
- build provenance.

Permitted intended actions are:

- `CREATE`
- `UPDATE`
- `SUPERSEDE`
- `RETIRE`
- `NO_CHANGE`

### 10.3 Identity preservation and identifier allocation

Project Genesis must:

1. preserve the existing Universal Asset Identifier for an existing asset;
2. match existing assets using the strongest available identifiers and repository metadata;
3. allocate a new identifier only where the asset is genuinely new;
4. use the locked `CERT-[SYSTEM]-[NUMBER]` convention;
5. prevent duplicate identifiers, duplicate canonical asset paths and identifier reuse;
6. never renumber an existing asset merely because it is moved, revised or restored;
7. retain superseded and retired identifiers in history.

Where identity is ambiguous, Project Genesis must quarantine the change for human resolution rather than guess.

### 10.4 Automatic register reconciliation

For every approved import, Project Genesis must automatically reconcile:

- newly created formal assets;
- restored formal assets;
- updated asset versions;
- status changes;
- ownership and review metadata;
- build provenance;
- parent and child references;
- Universal Relationship Engine relationship records;
- superseded and retired assets;
- moved canonical paths;
- deleted or missing file exceptions.

A formal asset must not exist in the canonical repository without a valid Master Asset Register entry after import.

A Master Asset Register entry must not point to a missing formal asset unless its status explicitly records retirement, supersession, archive or an approved exception.

### 10.5 Transactional integrity

Repository file changes and Master Asset Register changes form one transaction.

The import must not be treated as successful unless all of the following pass together:

- routing;
- collision controls;
- file merge;
- identifier allocation;
- register reconciliation;
- relationship reconciliation;
- applicable register updates;
- change-log update;
- Production Dashboard update;
- build-record update;
- repository validation.

A failure in any mandatory component must roll back the whole transaction to the pre-import checkpoint.

### 10.6 Dry-run and approval evidence

Before applying changes, Project Genesis must produce an Asset Register Change Report containing:

- assets to be created;
- assets to be updated;
- preserved identifiers;
- proposed new identifiers;
- duplicate or ambiguous matches;
- relationship additions and removals;
- supersessions and retirements;
- unresolved conflicts;
- excluded non-assets;
- expected register totals after import.

No unresolved high-risk conflict may proceed automatically.

### 10.7 Deletion and restoration controls

Deleting a repository folder does not by itself retire or delete the corresponding formal assets.

Restoration builds must:

- preserve the original asset identities;
- reconcile restored files to existing register entries;
- avoid allocating replacement identifiers to restored assets;
- identify orphaned register entries and orphaned files;
- record the restoration build as provenance;
- retain Git history and supersession history.

### 10.8 Build and closure gates

A build must not be represented as repository-ready unless it contains:

- the Asset Intent Manifest;
- the register reconciliation mechanism;
- dry-run reporting;
- rollback controls;
- automated tests for duplicate identifiers, orphan files, orphan register entries and failed transactional imports.

A build must not reach `ACTIONS_GREEN_CLOSED` where formal imported assets remain unregistered or the register points to unresolved missing files.

---

## 11. Locked Git commit-message convention

Every build commit message must use exactly:

```text
Add Certiaura Build [BUILD_NUMBER] [full agreed build title in sentence case]
```

Mandatory rules:

- begin with the exact words `Add Certiaura Build`;
- include the exact build number and suffix;
- use the full agreed descriptive title;
- do not shorten or paraphrase the title;
- do not substitute the shorter ZIP filename title;
- keep Product Passport wording aligned with existing repository history.

Example:

```text
Add Certiaura Build 0038 repository auto-routing and legacy build folder migration
```

---

## 12. Locked delivery format

Every completed build delivery to the founder must contain:

1. **One ZIP download link only**
2. **One ready-to-copy exact Git commit message**
3. **One proposed next build or next action**

Do not provide separate checksum, read-me or inventory links unless the founder specifically asks.

The ZIP must contain its own checksum and supporting build records.

---

## 13. Mandatory build-pack pre-release gate

Before issuing a build ZIP, confirm:

- filename complies with the locked naming convention;
- filename length is within the agreed limit;
- ZIP has no outer build wrapper;
- all paths are repository-relative;
- no unauthorised root folder is present;
- build records are under `Documentation/Build_Records/[BUILD_NUMBER]/`;
- schemas parse;
- scripts compile or execute as applicable;
- tests pass;
- defective examples fail as designed;
- routing manifest is complete;
- Asset Intent Manifest is complete;
- the existing Master Asset Register can be uniquely resolved;
- dry-run Asset Register Change Report is produced;
- formal asset identity preservation and new identifier allocation are validated;
- no duplicate Universal Asset Identifier, orphan formal asset or unresolved register reference remains;
- transactional rollback covers files and register changes;
- conflict policy is declared;
- rollback instructions are present where relevant;
- exact commit message is included in the build record;
- proposed next action is recorded;
- this continuation checkpoint is updated.

A build that fails any mandatory gate must not be represented as repository-ready.

---

## 14. Continuity checkpoint update rule

This document contains a live checkpoint. It must be updated whenever any of the following occurs:

- a build is authorised;
- a build is generated;
- a package is reissued;
- a build is imported;
- a build is committed and pushed;
- GitHub Actions become green;
- a defect is identified;
- the next planned action changes;
- a locked decision is amended or superseded.

Each updated version must:

- increment the version number;
- update the checkpoint date;
- retain the decision history;
- identify the last closed build;
- identify the current pending build;
- state the immediate next action;
- state the following planned action;
- record any known repository defect;
- be committed to the canonical repository;
- replace the older copy in the Certiaura GPT Project sources.

The older version may remain in Git history but should not remain as a competing active GPT Project source.

---

## 15. New-chat continuation protocol

At the start of a new Certiaura chat, the assistant must state internally and act on:

1. What is the last build evidenced as closed?
2. What build is delivered but not yet closed?
3. What defect or migration action is open?
4. What is the exact immediate next action?
5. What action follows it?
6. Which locked rules govern the output?

The assistant must not:

- restart from an earlier build;
- propose a duplicate build;
- skip an open correction;
- change the agreed next action without saying why;
- claim a build is installed merely because it was generated;
- create a new governance framework where this amendment already controls the issue.

Where the source files and the founder's latest explicit message conflict, the latest explicit founder message takes precedence and the checkpoint must be amended.

---


## 16. Current locked position

### Build 0038 closure confirmed by the founder

Build 0038 — repository restoration canonical routing and complete historical Master Asset Register reconciliation — is confirmed `ACTIONS_GREEN_CLOSED`.

Confirmed outcomes:

- corrected package contained 415 files;
- canonical Master Asset Register path is `Documentation/Master_Asset_Register.csv`;
- Master Asset Register contains 2,860 formal asset rows;
- blank Universal Asset Identifiers: 0;
- duplicate Universal Asset Identifier groups: 0;
- legacy `NO NEW UAI` placeholder removed;
- `Supporting Files` field implemented;
- transactional import completed successfully;
- total conflicts: 0;
- repository validation, commit, push and GitHub Actions closure confirmed.

### Build 0037 corrected reissue

Build 0037 retains its original identity and title:

```text
Build 0037 — Scientific content claims advertising AI recommendation and responsible communications controls
```

The corrected reissue is generated with:

- flat repository-relative routing;
- no build-named wrapper directory;
- a complete Asset Intent Manifest;
- automatic reconciliation against `Documentation/Master_Asset_Register.csv` through the installed Build 0038 transactional importer;
- preservation of existing Universal Asset Identifiers;
- dry-run routing, collision and Asset Register change reporting;
- backup and transactional rollback;
- full repository and Master Asset Register validation;
- claim, communications and artificial intelligence output schemas, validators, examples and automated tests.

### Following scientific build

```text
Build 0039 — evidence ingestion citation management living evidence surveillance and scientific review controls
```

Build 0039 remains planned and is not authorised to start until Build 0037 is imported, reconciled, repository-validated, committed, pushed and confirmed GitHub Actions green.

---

## 17. Current continuation checkpoint

**Checkpoint date:** 2026-07-19  
**Checkpoint status:** ACTIVE — BUILD 0037 CORRECTED REISSUE GENERATED

### Last closed build

```text
Build 0038 — ACTIONS_GREEN_CLOSED
```

### Current pending build

```text
Build 0037 — GENERATED corrected reissue; awaiting Project Genesis import and closure
```

### Immediate next action

```text
Import corrected Build 0037 through Project Genesis → review dry-run routing and Master Asset Register Change Reports → apply the transaction → run full repository validation → commit and push using the exact locked commit message → confirm GitHub Actions green.
```

### Hold point

Do not start Build 0039 until corrected Build 0037 reaches `ACTIONS_GREEN_CLOSED`.

---
## 18. Decision history

| Date | Decision | Status |
|---|---|---|
| 2026-07-19 | Use concise convention-compliant ZIP filenames | LOCKED |
| 2026-07-19 | Target filename length ≤80 characters; absolute maximum 100 | LOCKED |
| 2026-07-19 | Use one ZIP link, exact commit message and proposed next action | LOCKED |
| 2026-07-19 | Use exact `Add Certiaura Build...` commit convention | LOCKED |
| 2026-07-19 | Default to larger integrated work-package builds | LOCKED |
| 2026-07-19 | Use whole build numbers for materially distinct work packages | LOCKED |
| 2026-07-19 | Prohibit build-named wrapper folders inside ZIPs | LOCKED |
| 2026-07-19 | Route build records to `Documentation/Build_Records/[BUILD_NUMBER]/` | LOCKED |
| 2026-07-19 | Correct root build folders through controlled migration | LOCKED |
| 2026-07-19 | Maintain a live continuation checkpoint for new-chat continuity | LOCKED |
| 2026-07-19 | Require an Asset Intent Manifest in every build pack | LOCKED |
| 2026-07-19 | Automatically reconcile the existing Master Asset Register on every formal asset import | LOCKED |
| 2026-07-19 | Preserve existing Universal Asset Identifiers during update, move, restoration, supersession and retirement | LOCKED |
| 2026-07-19 | Treat file import and Master Asset Register update as one rollback-safe transaction | LOCKED |
| 2026-07-19 | Block build closure where formal assets or register entries are orphaned | LOCKED |
| 2026-07-19 | Reissue Build 0038 before import with integrated asset register reconciliation | LOCKED |
| 2026-07-19 | Confirm Build 0038 repository restoration and complete historical Master Asset Register reconciliation as ACTIONS_GREEN_CLOSED | LOCKED |
| 2026-07-19 | Reissue Build 0037 with flat routing, complete Asset Intent Manifest and Build 0038 transactional register reconciliation controls | LOCKED |

---

## 19. Machine-readable checkpoint

```json
{
  "document_id": "CERT-GOV-CONT-002",
  "version": "1.4.0",
  "status": "LOCKED_ACTIVE",
  "checkpoint_date": "2026-07-19",
  "canonical_repository_path": "00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",
  "zip_naming_pattern": "Certiaura_Build_[BUILD_NUMBER]_[Short_Descriptive_Title].zip",
  "zip_wrapper_folder_allowed": false,
  "canonical_master_asset_register": "Documentation/Master_Asset_Register.csv",
  "last_closed_build": {
    "build_number": "0038",
    "title": "repository restoration canonical routing and complete historical Master Asset Register reconciliation",
    "status": "ACTIONS_GREEN_CLOSED",
    "package_files": 415,
    "master_asset_register_rows": 2860,
    "blank_uai_rows": 0,
    "duplicate_uai_groups": 0,
    "legacy_placeholder_present": false,
    "supporting_files_field": true,
    "transactional_import": "SUCCESS",
    "conflicts": 0
  },
  "current_pending_build": {
    "build_number": "0037",
    "title": "Scientific content claims advertising AI recommendation and responsible communications controls",
    "status": "GENERATED_CORRECTED_REISSUE",
    "flat_repository_relative_routing": true,
    "asset_intent_manifest_complete": true,
    "automatic_master_asset_register_reconciliation": true,
    "preserve_existing_uai": true,
    "dry_run_required": true,
    "transactional_rollback": true,
    "full_repository_validation": true
  },
  "immediate_next_action": "Import corrected Build 0037 through Project Genesis, review dry-run reports, apply transaction, validate, commit and push, then confirm GitHub Actions green",
  "following_planned_build": {
    "build_number": "0039",
    "title": "evidence ingestion citation management living evidence surveillance and scientific review controls",
    "status": "PLANNED_ON_HOLD"
  },
  "hold_point": "Do not start Build 0039 until corrected Build 0037 reaches ACTIONS_GREEN_CLOSED"
}
```

---

## 20. Authority and amendment rule

This document is locked by explicit founder instruction.

It remains in force until Aidan Coleman explicitly:

- amends it;
- supersedes it; or
- approves a later replacement control.

Any proposed change must state:

1. the exact existing rule being changed;
2. the reason;
3. the replacement;
4. whether the old rule is amended, superseded or retained;
5. the effect on the current continuation checkpoint.

No assistant, developer or automation may silently alter these rules.
