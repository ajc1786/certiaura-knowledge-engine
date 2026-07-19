# CERTIAURA HISTORICAL ASSET REGISTER BACKFILL STANDARD

**Document ID:** Pending canonical Universal Asset Identifier allocation  
**Version:** 1.0.0  
**Status:** ACTIVE  
**Owner:** Certiaura  
**Build provenance:** CERT-BUILD-0038

## Purpose

This standard requires Project Genesis to perform a repository-wide census and reconcile all registerable historical Certiaura assets with the one canonical Master Asset Register.

The control applies to assets created before automatic register reconciliation was introduced, including assets from earlier builds whose build records, manifests or inventories are incomplete.

## Mandatory outcome

After a successful reconciliation:

- every registerable historical repository item has one valid Master Asset Register entry;
- every existing Universal Asset Identifier is preserved where identity can be established;
- genuinely unregistered assets receive the next valid identifier for their Knowledge System;
- duplicate identifiers, duplicate canonical paths and ambiguous identity matches are blocked;
- administrative build records, test fixtures, examples, caches and temporary outputs remain excluded and are reported;
- register entries pointing to missing files are blocked unless their status explicitly records retirement, supersession, archive, deprecation or an approved exception;
- the census, exclusions, changes and unresolved conflicts are written to the Build 0038 audit record.

## Historical discovery sources

The backfill process must use, in order of evidential strength:

1. existing Master Asset Register identifiers and canonical paths;
2. explicit Universal Asset Identifier metadata embedded in an asset;
3. prior Build Record file inventories and manifests;
4. canonical repository path and Knowledge System;
5. normalised asset title and asset type;
6. repository-wide census where earlier build provenance is unavailable.

The process must quarantine ambiguity rather than guess.

## Registerable asset classes

Registerable classes include governance controls, knowledge assets, standards, schemas, templates, registers, validators, automation, scripts, dashboards, reports, calculators, controlled documentation, datasets and reusable media assets.

Administrative records and disposable fixtures are not formal assets unless explicitly designated otherwise.

## Transactional requirement

The historical backfill is part of the Build 0038 transaction. Repository restoration, register reconciliation, relationship checks, validation and control-record updates must succeed together or roll back together.
