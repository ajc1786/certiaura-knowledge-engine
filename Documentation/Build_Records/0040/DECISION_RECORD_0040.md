# Build 0040 Decision Record

## Decision

Correct and reissue Build 0040 under the same build identity after importer inspection found Build 0039 metadata hard-coded in the installed transactional importer.

## Root cause

The first Build 0040 release gate validated package structure and direct synthetic extraction, but did not execute the actual Project Genesis transactional importer that would be used against the real repository.

## Corrective action

- replace the Build 0039-specific importer with a build-neutral importer;
- add a dedicated Build 0040 runner;
- execute real importer dry-run and apply modes during final-ZIP preflight;
- validate current-build metadata, paths, register reconciliation, identifier allocation, backup and transaction journal;
- add regression coverage that rejects prior-build importer residue;
- lock the control for all future builds;
- retain Build number 0040 because the correction does not create a materially new work package.

## Status

LOCKED — corrected reissue authorised.
