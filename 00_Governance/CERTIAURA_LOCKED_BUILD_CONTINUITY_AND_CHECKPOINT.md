# CERTIAURA LOCKED BUILD CONTINUITY AND CHECKPOINT

**Document ID:** CERT-GOV-CONT-002
**Version:** 1.4.0
**Status:** LOCKED — ACTIVE
**Effective date:** 2026-07-19
**Last updated:** 2026-07-21
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
2. `CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md`
3. `CERTIAURA_REFERENCE_PACK_READ_FIRST.md`
4. `CERTIAURA_MASTER_PROJECT_CHARTER.md`
5. `CERTIAURA_LOCKED_DECISIONS_REFERENCE.md`, where available
6. `CERTIAURA_CONTINUITY_AND_CHANGE_CONTROL.md`
7. `CERTIAURA_CURRENT_STATE_BASELINE.md` or the current equivalent
8. The existing Master Asset Register at its current canonical repository path
9. The latest installed build record and latest pending build record

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

## 16. Current locked correction

### Founder-confirmed repository position

The founder has deleted the incorrectly routed root-level build folders for Builds **0035E through 0036** from the working repository.

The repository therefore requires a controlled restoration of the deleted build content into canonical repository-relative paths.

Deletion of those folders does not authorise deletion or renumbering of any corresponding formal asset identities.

### Build 0038 correction

An initial Build 0038 restoration package was generated, but it did not include automatic Master Asset Register reconciliation.

That package must **not** be imported.

Build 0038 must be reissued under the same build identity as a corrected integrated package:

```text
Build 0038 — repository restoration canonical routing and Master Asset Register reconciliation for Builds 0035E to 0036
```

The corrected Build 0038 must:

- restore Builds 0035E through 0036 directly into canonical repository paths;
- include no build-named wrapper folder;
- locate and reconcile the existing Master Asset Register;
- preserve existing Universal Asset Identifiers;
- allocate identifiers only for genuinely new formal assets;
- detect orphaned files and orphaned register entries;
- update relationships, applicable registers, change log, Production Dashboard and build records;
- provide dry-run routing and Asset Register Change Reports;
- provide backup, transactional rollback and post-import validation;
- remove no additional repository content without an explicit approved action;
- block commit and push if asset reconciliation fails.

### Build 0037

Build 0037 remains generated but not correctly installed.

After Build 0038 has restored and validated the prerequisite repository position, Build 0037 must be reissued with:

- flat repository-relative routing;
- no build-named wrapper folder;
- an Asset Intent Manifest;
- automatic Master Asset Register reconciliation;
- transactional rollback and full repository validation.

### Following scientific build

After corrected Builds 0038 and 0037 are imported, validated, committed, pushed and confirmed green, the planned scientific production package is:

```text
Build 0039 — evidence ingestion citation management living evidence surveillance and scientific review controls
```

---

## 17. Current continuation checkpoint

**Checkpoint date:** 2026-07-21
**Checkpoint status:** ACTIVE - BUILD 0052 RC6 GENERATED, CANONICAL REGRESSION REQUIRED

### Last confirmed closed build

```text
Build 0051 - Retatrutide post-closure surveillance, governed case reopening, periodic review and recurrence analytics baseline
Status: ACTIONS_GREEN_CLOSED
Successful package lineage: RC3
```

### Current active build

```text
Build 0052 - Retatrutide cross-case signal aggregation, cohort surveillance, governed escalation and controlled knowledge feedback baseline
Status: RC6 GENERATED outside the canonical repository; RC1, RC2, RC3, RC4 and RC5 withdrawn
```

### Immediate next action

Run the final Build 0052 RC6 Windows PowerShell 5.1 regression. It must derive the exact Build 0051 predecessor evidence from canonical Git history, migrate valid historical lessons schemas with recorded provenance, keep the current matrix strict, expose rollback reasons directly, and return `BUILD_0052_RC6_READY_FOR_CANONICAL_IMPORT`. Only then complete canonical dry-run, forced rollback, clean transactional import, Master Asset Register reconciliation, repository validation, exact commit, push and GitHub Actions verification.

### Following planned build

```text
Build 0053 - Retatrutide controlled evidence-feedback adjudication, knowledge-asset update impact assessment and publication governance baseline
```

### Founder close-out rule

`GREEN` is the definitive close-out phrase only after canonical import, validation, commit, push and GitHub Actions evidence exists. On `GREEN`, mark Build 0052 `ACTIONS_GREEN_CLOSED` and begin Build 0053 immediately.

### Mandatory predecessor release gate

- Predecessor fixture identity: exact Build 0051.
- Predecessor provenance and commit subject: exact match.
- Predecessor/current Asset Intent Manifest intersection: empty unless an explicit approved update is declared.
- Predecessor paths: preserved unchanged.
- Executable predecessor-aware dry-run: `DRY_RUN_VALIDATED` with no conflicts.

---

## 18. Decision history

| Date | Decision | Status |
|---|---|---|
| 2026-07-21 | Build 0051 closed as `ACTIONS_GREEN_CLOSED` on successful RC3 lineage | LOCKED FACT |
| 2026-07-21 | Build 0052 begins immediately after founder `GREEN` | LOCKED |
| 2026-07-21 | Build 0052 RC1 withdrawn because predecessor truth was candidate-authored rather than derived from canonical Git objects | LOCKED FACT |
| 2026-07-21 | Build 0052 RC3 required strict historical manifest schema detection but was withdrawn after a historical lessons matrix schema incompatibility | LOCKED |
| 2026-07-22 | Build 0052 RC4 must use `CERT-GOV-LEARN-001` v2.5.0, recorded historical lessons migration, strict current-build schema and operator-visible transactional failure reasons | LOCKED |
| 2026-07-22 | Build 0052 RC4 cumulative updater must treat same-build pre-merged lesson replay as idempotent while retaining stronger-control enforcement for any genuinely new origin build | LOCKED |
| 2026-07-21 | Build 0052 RC2 withdrawn after `PREDECESSOR_MANIFEST_PATH_INVALID` exposed a current-schema-only historical manifest parser | LOCKED FACT |
| 2026-07-21 | Every build must include executable lessons-learned controls and block closure if incomplete | LOCKED |
| 2026-07-21 | Predecessor fixtures must identify the exact prior build and have an empty intersection with the current exact Asset Intent Manifest | LOCKED |
| 2026-07-21 | Predecessor-aware dry-run must return `DRY_RUN_VALIDATED` with no conflicts before delivery | LOCKED |
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

---

## 19. Machine-readable checkpoint

```json
{
  "document_id": "CERT-GOV-CONT-002",
  "version": "1.4.0",
  "status": "LOCKED_ACTIVE",
  "checkpoint_date": "2026-07-21",
  "last_closed_build": {
    "build_number": "0051",
    "status": "ACTIONS_GREEN_CLOSED",
    "successful_lineage": "RC3",
    "title": "Retatrutide post-closure surveillance, governed case reopening, periodic review and recurrence analytics baseline"
  },
  "current_build": {
    "build_number": "0052",
    "status": "RC6_GENERATED_PENDING_CANONICAL_REGRESSION",
    "title": "Retatrutide cross-case signal aggregation, cohort surveillance, governed escalation and controlled knowledge feedback baseline",
    "required_endpoint": "BUILD_0052_RC6_READY_FOR_CANONICAL_IMPORT"
  },
  "following_planned_build": {
    "build_number": "0053",
    "title": "Retatrutide controlled evidence-feedback adjudication, knowledge-asset update impact assessment and publication governance baseline"
  },
  "predecessor_gate": {
    "exact_build": "0051",
    "manifest_intersection_required": "EMPTY",
    "commit_subject_required": "EXACT_MATCH",
    "paths_preserved_required": true,
    "dry_run_endpoint": "DRY_RUN_VALIDATED",
    "conflicts_required": "NONE"
  },
  "green_close_phrase": "GREEN"
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

## Build 0052 RC3 withdrawal and RC4 correction

RC3 completed canonical predecessor evidence, dry run and forced rollback, then clean reapply rolled back because the cumulative updater treated `control_family` as mandatory in the valid historical Build 0041 lessons matrix. RC4 became the corrective candidate at that stage. Historical omissions may be migrated only through recorded provenance; current Build 0052 records remain strict.

## Build 0052 RC4 pre-delivery updater replay correction

The full outside-canonical transaction identified that replaying the already pre-merged Build 0052 lesson matrix was incorrectly treated as a new recurrence. RC4 was corrected before delivery. Same-origin replay is now idempotent, while a genuinely new origin build with unchanged repeated-defect controls remains release-blocking.

## Build 0052 RC4 withdrawal and RC5 PowerShell scalar-output correction

RC4 completed package preflight and reached the intentional forced rollback. The importer returned exit code 3, rolled back cleanly, wrote the exact rollback report and emitted `BUILD_0052_TRANSACTION_ROLLED_BACK`. The regression falsely failed because `-notmatch` was applied directly to the output array. RC5 joins captured output into one deterministic scalar before matching, applies the same correction to the canonical import wrapper and includes multi-line positive and negative controls. RC1 through RC4 remain withdrawn.

Build 0052 RC5 was withdrawn after canonical runtime proved that Builds 0039, 0040 and 0043-0046 have no retained per-build lessons matrices. RC6 validates those legacy builds through exact SHA-256-bound lesson-ID sets already present in the authoritative cumulative ledger and prohibits fabricated matrices.

<!-- CERTIAURA_BUILD_0053_CHECKPOINT_START -->
## Build 0053 continuation checkpoint - generated by controlled import

- Last closed build: `0052` (`ACTIONS_GREEN_CLOSED`)
- Closed predecessor commit: `890df218b4f4dea92f4ccfa36b8106de59eca1b1`
- Current build: `0053` candidate `RC4`
- Build title: `retatrutide governed knowledge change implementation, cross-asset impact control, controlled publication and post-change effectiveness surveillance baseline`
- Current state after import: `REPOSITORY_VALIDATED` pending exact commit, push, GitHub Actions and founder `GREEN`
- Prohibited Build 0052 predecessor candidates: `RC1-RC5`
- Withdrawn and prohibited Build 0053 candidates: `RC1`, `RC2`, `RC3`
- Required next action: commit using the reserved subject, push, verify GitHub Actions, then obtain founder `GREEN`
- Proposed following action: Build 0054 Retatrutide end-to-end operational assurance and Platinum readiness assessment

<!-- CERTIAURA_BUILD_0053_CHECKPOINT_END -->

<!-- CERTIAURA_BUILD_0054_CHECKPOINT_START -->
## Build 0054 continuation checkpoint - generated by controlled import

- Last closed build: `0053` (`ACTIONS_GREEN_CLOSED`)
- Canonical predecessor commit: `d5b7b84a2c543bbdd5cad8727f1c9005c27ca70d`
- Predecessor GitHub Actions run ID: `29986875639` (`completed`, `success`, attempt 1)
- Current build: `0054` candidate `RC4`
- Build title: `retatrutide end-to-end operational assurance, controlled release readiness, failure-mode coverage and Platinum readiness assessment baseline`
- State after import: `REPOSITORY_VALIDATED` pending commit, push, exact Actions run ID and founder `GREEN`
- Closure prohibition: do not mark `ACTIONS_GREEN_CLOSED` without an Actions run ID tied to the canonical commit

<!-- CERTIAURA_BUILD_0054_CHECKPOINT_END -->

<!-- CERTIAURA_BUILD_0055_CHECKPOINT_START -->
## Build 0055 continuation checkpoint - generated by controlled import

- Last closed build: `0054` (`ACTIONS_GREEN_CLOSED`)
- Canonical predecessor commit: `8a9dba6615448c1ad85c44cdf89269a8fc3e00e8`
- Predecessor GitHub Actions run ID: `29993394313` (`completed`, `success`, attempt 1)
- Current build: `0055` candidate `RC2`
- Build title: `historical GitHub Actions evidence reconciliation, retatrutide baseline closure, reusable architecture handoff and governed next-peptide transition baseline`
- State after import: `REPOSITORY_VALIDATED` pending canonical commit, push, exact Actions run ID and founder `GREEN`
- Retatrutide boundary: operational knowledge baseline closure is not clinical or regulatory approval

<!-- CERTIAURA_BUILD_0055_CHECKPOINT_END -->

<!-- CERTIAURA_BUILD_0056_CHECKPOINT_START -->
## Build 0056 continuation checkpoint - generated by controlled import

- Last closed build: `0055` (`ACTIONS_GREEN_CLOSED`)
- Canonical predecessor commit: `977829a987baf744beab4762478d9f0a88165fb0`
- Predecessor GitHub Actions run ID: `29997204286` (`completed`, `success`, attempt 1)
- Historical Actions baseline: Builds 0001-0054 fully accounted, 53 exact run IDs and one controlled Build 0001 exception
- Current build: `0056` candidate `RC1`
- Build title: `tesamorelin evidence corpus mapping, biological and safety boundary definition, target-specific data contracts, monitoring model and controlled pilot acceptance baseline`
- State after import: `REPOSITORY_VALIDATED` pending canonical commit, push, exact Actions run ID and founder `GREEN`
- Pilot boundary: Tesamorelin knowledge-architecture work only; no clinical recommendation, dosing, diagnosis or prescribing authority

<!-- CERTIAURA_BUILD_0056_CHECKPOINT_END -->

<!-- CERTIAURA_BUILD_0057_CHECKPOINT_START -->
## Build 0057 continuation checkpoint - generated by controlled import

- Last closed build: `0056` (`ACTIONS_GREEN_CLOSED`)
- Canonical predecessor commit: `2e6fe434bf1d0566bf3d1afa33bae24ce13b3b44`
- Predecessor GitHub Actions run ID: `29999430792` (`completed`, `success`, attempt 1)
- Current build: `0057` candidate `RC1`
- Build title: `tesamorelin governed evidence ingestion, provenance validation, monitoring workflow simulation, safety escalation, audit replay and controlled acceptance baseline`
- State after import: `REPOSITORY_VALIDATED` pending canonical commit, push, exact Actions run ID and founder `GREEN`
- Clinical boundary: governed knowledge-workflow simulation only
- Git control: automatic GC and maintenance prompts prohibited during commit, push and closure

<!-- CERTIAURA_BUILD_0057_CHECKPOINT_END -->

<!-- CERTIAURA_BUILD_0058_CHECKPOINT_START -->
Build 0058 establishes governed Tesamorelin multi-source quality assessment, conflicting-evidence adjudication, longitudinal recurrence review, controlled amendment and pilot continuation or suspension governance. Canonical closure still requires exact GitHub Actions evidence and founder GREEN.
<!-- CERTIAURA_BUILD_0058_CHECKPOINT_END -->
