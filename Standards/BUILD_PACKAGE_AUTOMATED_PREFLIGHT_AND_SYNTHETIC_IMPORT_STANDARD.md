# Build Package Automated Preflight and Synthetic Import Standard

**Version:** 1.1.0
**Status:** LOCKED — ACTIVE
**Effective date:** 2026-07-20
**Build provenance:** CERT-BUILD-0040 corrected reissue

## 1. Purpose

This standard converts the Build 0039 and Build 0040 lessons learned into a mandatory, fail-closed release gate for every future Certiaura build package.

A package is not repository-ready merely because its ZIP structure, manifests, checksums, source compilation or direct file extraction pass.

The exact transactional import route intended for the real repository must also pass against the exact final ZIP.

## 2. Mandatory package controls

Every final ZIP must pass:

- repository-relative path safety;
- canonical root allowlisting;
- no build-named wrapper folder;
- no duplicate or case-only path collision;
- complete routing and Asset Intent Manifest classification;
- package inventory equality with ZIP members;
- checksum verification from ZIP bytes;
- UTF-8, LF line endings, final newlines and no trailing whitespace;
- JSON parsing and Python compilation;
- no generated runtime artefacts;
- exact locked commit-message validation.

## 3. Actual importer compatibility gate

Every future build must contain either:

1. the canonical build-neutral transactional importer; or
2. a dedicated current-build importer and runner that have passed the same controls.

The importer must derive from the candidate package:

- build number;
- full build title;
- package version;
- build-record root;
- Build Manifest path;
- Routing Manifest path;
- Asset Intent Manifest path;
- dry-run and apply report destinations.

Hard-coded metadata, paths, package versions, report locations or assumptions from a prior build block release.

A missing current-build runner or uncertainty about which importer will execute also blocks release.

## 4. Synthetic transactional installation

The preflight must create a temporary Git repository containing:

- unrelated tracked historical files;
- realistic existing replacement paths;
- a structurally valid Master Asset Register;
- existing Universal Asset Identifiers that must remain preserved.

The exact final ZIP must then be processed through the actual importer in both modes.

### 4.1 Dry run

The dry run must prove:

- no repository modification;
- correct current-build metadata;
- correct build-record and manifest paths;
- valid routing and conflict classification;
- correct expected register total;
- correct identifier preservation and proposed allocation;
- `apply_allowed=true` only where no blocking error exists.

### 4.2 Apply transaction

The apply test must prove:

- transaction backup creation;
- transaction journal creation;
- package files written to canonical paths;
- Master Asset Register updated in the same transaction;
- new identifiers allocated only for genuinely new assets;
- existing identifiers preserved;
- post-apply hashes validated;
- unrelated historical files preserved;
- rollback-safe journal data contains the current build metadata.

## 5. Git integrity gate

After the synthetic apply transaction, all resulting repository changes must be staged.

The staged set must equal:

- all package member paths; plus
- the canonical Master Asset Register where reconciliation changes it.

The following must then pass:

```text
git diff --check
git diff --cached --check
```

Release is blocked by:

- unexpected deletions;
- unstaged changes;
- untracked files;
- runtime artefacts;
- staged-path drift;
- modification or loss of unrelated history.

## 6. Regression requirements

Every build package must include automated regression coverage for:

- correct current-build metadata discovery;
- at least one subsequent synthetic build number to prove build-neutral operation;
- rejection of prior-build hard-coded importer residue;
- wrapper folders;
- trailing whitespace;
- runtime artefacts;
- case collisions;
- unclassified files;
- checksum drift;
- transactional register reconciliation.

## 7. PowerShell-first operating rule

All founder-facing build, validation, import, report inspection, Git and close-out instructions must be provided as complete PowerShell command blocks.

File Explorer or manual navigation must not be required unless no reliable PowerShell route exists.

## 8. Build 0040 correction

The first Build 0040 package passed package-level synthetic extraction but did not execute the installed Project Genesis transactional importer. Inspection then found Build 0039 metadata hard-coded in that importer.

That package was blocked before import.

The corrected Build 0040 package retains the same build number and title and introduces release-gate version `1.1.0`.

## 9. Authority

This standard is locked by explicit founder instruction and remains active until explicitly amended or superseded.
