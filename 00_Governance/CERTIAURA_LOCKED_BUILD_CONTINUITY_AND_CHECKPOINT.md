# CERTIAURA LOCKED BUILD CONTINUITY AND CHECKPOINT

**Document ID:** CERT-GOV-CONT-002  
**Version:** 1.1.0  
**Status:** LOCKED — ACTIVE  
**Effective date:** 2026-07-19  
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
- build status interpretation;
- continuity between chats;
- maintenance of the current next planned action.

It exists to stop future chats, assistants, developers or build tools from:

- recreating previously settled controls;
- packaging builds inside build-named wrapper folders;
- depositing build folders in the repository root;
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
7. The latest installed build record and latest pending build record

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
8. Create a pre-import backup or recoverable Git checkpoint.
9. Produce a dry-run routing report.
10. Merge approved files into canonical paths.
11. Update the relevant registers, build record, change log and continuation checkpoint.
12. Run full repository validation.
13. Produce a post-import report.
14. Support rollback where validation fails.
15. Prevent commit and push when mandatory validation fails.

Automation may route, compare, hash, validate, block and report. It must not silently approve a destructive overwrite or conceal a collision.

---

## 10. Locked Git commit-message convention

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

## 11. Locked delivery format

Every completed build delivery to the founder must contain:

1. **One ZIP download link only**
2. **One ready-to-copy exact Git commit message**
3. **One proposed next build or next action**

Do not provide separate checksum, read-me or inventory links unless the founder specifically asks.

The ZIP must contain its own checksum and supporting build records.

---

## 12. Mandatory build-pack pre-release gate

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
- conflict policy is declared;
- rollback instructions are present where relevant;
- exact commit message is included in the build record;
- proposed next action is recorded;
- this continuation checkpoint is updated.

A build that fails any mandatory gate must not be represented as repository-ready.

---

## 13. Continuity checkpoint update rule

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

## 14. New-chat continuation protocol

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

## 15. Current locked correction

### Repository deletion and restoration position

The incorrectly routed root folders for Builds **0035E through 0036** have now been deleted from the repository by the founder. Their content must be restored through one canonical, repository-relative package rather than recreated as root-level build folders.

### Restoration build

The current integrated recovery package is:

```text
Build 0038 — repository restoration and canonical routing for Builds 0035E to 0036
```

Build 0038:

- restores the functional content of Builds 0035E, 0035F, 0035G, 0035H, 0035I, 0035J, 0035K and 0036;
- preserves each historical build identity and build record;
- places build records under `Documentation/Build_Records/[BUILD_NUMBER]/`;
- removes all build-name wrapper folders from package routing;
- excludes Python cache and compiled artefacts;
- resolves the three cross-build path collisions through compatible merged controls;
- adds Project Genesis route validation and safe dry-run import controls;
- supplies one flat repository-relative ZIP.

### Build 0037

Build 0037 retains its original identity and must next be reissued with corrected flat repository-relative routing before installation.

### Following scientific build

After Build 0038 is installed and closed, and Build 0037 is correctly reissued and closed, the planned scientific production package remains:

```text
Build 0039 — evidence ingestion citation management living evidence surveillance and scientific review controls
```

---

## 16. Current continuation checkpoint

**Checkpoint date:** 2026-07-19  
**Checkpoint status:** ACTIVE — BUILD 0038 GENERATED FOR RESTORATION

### Last confirmed project position

- The incorrectly routed repository folders for Builds 0035E–0036 were deleted by the founder.
- Build 0038 now consolidates their restoration into canonical repository paths.
- Build 0037 remains generated but requires a corrected flat reissue before installation.
- The 0035 lettered series remains closed at 0035K.
- Materially distinct integrated work packages continue to use whole build numbers.

### Immediate next action

```text
Import Build 0038, run repository validation, commit and push using the exact supplied commit message, and confirm GitHub Actions green.
```

### Next action after Build 0038 closes

```text
Reissue and install Build 0037 with flat repository-relative routing.
```

### Following planned build

```text
Build 0039 — evidence ingestion citation management living evidence surveillance and scientific review controls
```

### Current hold point

Do not proceed to Build 0039 until:

- Build 0038 has restored Builds 0035E–0036;
- repository validation passes;
- Build 0038 is committed and pushed;
- GitHub Actions are confirmed green;
- Build 0037 is reissued, installed, validated, committed and closed.

---

## 17. Decision history

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
| 2026-07-19 | Restore deleted Builds 0035E–0036 through one canonical flat Build 0038 package | LOCKED |

---

## 18. Machine-readable checkpoint

```json
{
  "document_id": "CERT-GOV-CONT-002",
  "version": "1.1.0",
  "status": "LOCKED_ACTIVE",
  "checkpoint_date": "2026-07-19",
  "canonical_repository_path": "00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md",
  "zip_naming_pattern": "Certiaura_Build_[BUILD_NUMBER]_[Short_Descriptive_Title].zip",
  "zip_filename_target_max_characters": 80,
  "zip_filename_absolute_max_characters": 100,
  "zip_wrapper_folder_allowed": false,
  "build_record_path_pattern": "Documentation/Build_Records/[BUILD_NUMBER]/",
  "commit_pattern": "Add Certiaura Build [BUILD_NUMBER] [full agreed build title in sentence case]",
  "delivery": {
    "zip_links": 1,
    "include_exact_commit_message": true,
    "include_proposed_next_action": true
  },
  "restoration": {
    "build_number": "0038",
    "title": "repository restoration and canonical routing for Builds 0035E to 0036",
    "restores": [
      "0035E",
      "0035F",
      "0035G",
      "0035H",
      "0035I",
      "0035J",
      "0035K",
      "0036"
    ],
    "status": "GENERATED_PENDING_IMPORT"
  },
  "immediate_next_action": "Import Build 0038, validate repository, commit and push, confirm GitHub Actions green",
  "next_action": "Reissue and install Build 0037 with corrected flat repository-relative routing",
  "following_planned_build": {
    "build_number": "0039",
    "title": "evidence ingestion citation management living evidence surveillance and scientific review controls"
  },
  "hold_point": "Do not start Build 0039 until Builds 0038 and corrected 0037 are installed, validated, committed, pushed and Actions green"
}
```

---

## 19. Authority and amendment rule

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
