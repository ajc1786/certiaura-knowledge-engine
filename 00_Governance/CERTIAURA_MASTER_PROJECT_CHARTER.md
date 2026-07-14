# CERTIAURA MASTER PROJECT CHARTER

**Document ID:** CERT-GOV-CHARTER-001  
**Version:** 1.0.0  
**Status:** Active Reference Baseline  
**Effective date:** 2026-07-14

## Purpose

This Charter consolidates previously agreed Certiaura decisions. It does not create a new governance layer. Its purpose is to preserve continuity so the project does not repeatedly revisit settled matters.

## 1. Project identity and commercial purpose

**Working company / platform name:** Certiaura

Certiaura is being developed as a commercial scientific knowledge and intelligence platform with structured, reusable intellectual property at its core.

The agreed commercial model includes:

- Scientific knowledge platform
- Premium membership
- Professional reports
- Enterprise licensing
- Academy
- Marketplace
- Affiliate income
- Product Passport™
- Future direct sale of peptides where legally permitted
- A future foundation that may receive a portion of profits

Certiaura is not being developed as a purely not-for-profit project. Commercial profit, scalability and the founder's financial objectives remain legitimate goals.

## 2. Operating model

The agreed operating model is:

- **80% production**
- **15% platform improvement**
- **5% innovation / future opportunities**

Core principles:

- Build once, use everywhere.
- One source of truth.
- Repository-first development.
- Every session should aim to create permanent reusable intellectual property.
- Reuse existing standards before inventing new ones.
- Do not re-propose previously agreed structures as new ideas.
- Do not create duplicate governance documents where an existing standard already covers the subject.
- Architecture and governance are revisited only when production exposes a genuine gap, the founder explicitly requests a change, or external scientific, regulatory, legal or technical change requires review.
- Project names should include the actual task in brackets where useful for clarity.

## 3. Continuity rule

Once a decision is agreed, it remains in force unless it is:

1. Explicitly amended;
2. Explicitly superseded; or
3. Rendered obsolete by an external scientific, regulatory, legal or technical change requiring review.

A future assistant, developer or collaborator must not casually overwrite, reframe or duplicate a locked decision.

Before recommending a structural change, the existing reference baseline must be checked first.

Any proposed change to a locked decision should state:

- The existing decision being changed;
- Why the change is necessary;
- What replaces it;
- Whether the old decision is amended, superseded or retained.

## 4. Knowledge architecture already agreed

The following are already established and must not be reintroduced as new concepts:

- Layered Knowledge Standard
- Platinum Asset Standard
- Evidence Intelligence Framework
- Core Knowledge Objects
- Composite Knowledge Assets
- Living Evidence
- Master Asset Register
- Decision Log
- Production Dashboard
- Completeness Scoring
- Work Packages
- Production Queue

The default is to use and extend these systems rather than recreate them.

## 5. Universal Asset & Relationship Standard (UARS)

Every formal Certiaura asset receives a permanent Universal Asset Identifier (UAI).

Current repository implementation:

```text
CERT-[SYSTEM]-[NUMBER]
```

Examples:

```text
CERT-PKS-000001
CERT-BKS-000001
CERT-CKS-000001
CERT-MKS-000001
CERT-EKS-000001
CERT-GKS-000001
```

This naming approach must not be changed casually. Any future alteration should be treated as an explicit migration decision.

Mandatory asset metadata includes, where applicable:

- Universal Asset Identifier
- Version
- Status
- Owner
- Completion percentage
- Knowledge System
- Parent Assets
- Child Assets
- Relationship List
- Evidence Links
- Report Links
- Marketplace Links
- Last Review
- Next Review
- Change History

Agreed relationship types include:

- HAS_MECHANISM
- ACTS_ON
- HAS_RECEPTOR
- HAS_BIOMARKER
- HAS_CONDITION
- SUPPORTS_GOAL
- HAS_EVIDENCE
- HAS_REPORT
- HAS_PRODUCT
- HAS_PASSPORT
- HAS_CALCULATOR
- HAS_MONITORING
- HAS_WARNING
- HAS_CONTRAINDICATION
- HAS_SAFETY
- COMPARES_WITH
- REQUIRES
- PARENT_OF
- CHILD_OF
- RELATED_TO
- GENERATES
- SUPERSEDES

Relationship attributes may include:

- Target
- Strength
- Evidence
- Source

Knowledge graph rule:

> Every non-root asset should have meaningful incoming and/or outgoing relationships.

One concept should be defined once and referenced elsewhere.

A central Universal Relationship Engine (URE) is the agreed direction so the website, artificial intelligence, search, reports, marketplace, Academy and future application programming interfaces use one relationship model and one dataset.

## 6. Knowledge Systems

Current repository systems:

- **PKS** — Peptide Knowledge System
- **BKS** — Biology Knowledge System
- **CKS** — Condition Knowledge System
- **MKS** — Monitoring Knowledge System
- **SKS** — Safety Knowledge System
- **EKS** — Evidence Knowledge System
- **GKS** — Goal Knowledge System
- **RKS** — Report Knowledge System
- **CIS** — Cost Intelligence System
- **PPS** — Product Passport System
- **MPS** — Marketplace System
- **AKS** — Academy Knowledge System
- **SYS** — Platform System

A Library Knowledge System (LKS) has been discussed but was not confirmed as locked. It must not be treated as agreed unless explicitly approved.

## 7. Cost Intelligence™ — locked scope

Every applicable Knowledge Asset may include:

- Cost per vial
- Cost per milligram
- Cost per research unit
- Cost comparison
- Equipment costs
- Shipping allowance
- Estimated total research cost
- Budget, mid-range and premium scenarios
- Value-for-money assessment
- Historical pricing where available
- Cost dashboard
- Cost comparison engine
- Cost history graphs
- Total Research Budget Calculator
- Marketplace price comparison
- Equipment Cost Calculator
- Affiliate revenue tracking
- Margin calculator
- Subscription value calculator
- Lifetime cost of ownership

Lifetime cost of ownership may include:

- Initial equipment
- Ongoing consumables
- Storage replacement
- Travel equipment
- Annual estimated cost

A dedicated Cost Report may contain:

- Compound cost
- Consumables
- Storage equipment
- Travel/storage equipment
- Total project budget
- Comparable alternatives
- Estimated ongoing costs

## 8. Product Passport™ — locked scope

Product Passport™ may include:

- Supplier
- Manufacturer
- Product identifier
- Batch
- Concentration
- Certificate of Analysis availability
- Storage requirements
- Temperature guidance
- Packaging
- Availability
- Cost history
- Quality indicators

## 9. Marketplace and resource model

The platform may integrate:

- Storage products
- Laboratory consumables
- Travel coolers
- Reconstitution equipment
- Educational resources
- Trusted affiliate partners

Agreed direction:

1. Affiliate and trusted third-party resource links initially;
2. Marketplace capability later;
3. Product Passport™ integration;
4. Future direct sales where legally appropriate and compliant.

The future sale of peptides is an agreed long-term commercial objective and should not be silently omitted from future strategy discussions.

## 10. Knowledge asset output features already agreed

Applicable assets may include:

- Printable branded PDF outputs
- Research dosing / calculator sections
- Reconstitution guidance
- Delivery method guidance
- Research cycle information
- Layperson / basic summaries
- Educational pathways
- Reference links where appropriate
- Marketplace integration
- Comparison functions
- Monitoring
- Safety
- Evidence links
- Product Passport™ links

## 11. Repository and source-of-truth model

Agreed arrangement:

- **GitHub** — canonical version-controlled source
- **OneDrive** — synced local working storage and backup
- **ChatGPT** — production environment
- **Project Genesis** — developing automation and repository management platform

Repository:

```text
ajc1786/certiaura-knowledge-engine
```

Local repository path:

```text
C:\Users\enqui\OneDrive\Documents\CERTIAURA\Repository\certiaura-knowledge-engine
```

The repository is private and proprietary.

No open-source licence was adopted.

## 12. Repository structure already established

Top-level folders include:

- 00_Governance
- 01_Knowledge_Systems
- 02_Peptides
- 03_Biology
- 04_Conditions
- 05_Monitoring
- 06_Evidence
- 07_Goals
- 08_Product_Passports
- 09_Cost_Intelligence
- 10_Marketplace
- 11_Academy
- 12_Reports
- 13_Project_Genesis
- Assets
- Database
- Documentation
- Images

Repository foundation documents already created include:

- CONTRIBUTING.md
- REPOSITORY_STRUCTURE.md
- NAMING_STANDARD.md
- VERSIONING_STANDARD.md
- RELEASE_POLICY.md
- ROADMAP.md
- LICENSE.md

These documents should be amended where necessary rather than duplicated with competing standards.

## 13. Project Genesis — current agreed role

Project Genesis is the internal platform intended to reduce repetitive repository administration and ultimately support the wider Certiaura knowledge engine.

Current position:

- v0.1 repository automation script has been added.
- v1.0 desktop application scaffold has been added.
- GitHub Actions repository validation is operational.
- The latest validation baseline passed successfully.
- The next planned development step is **Project Genesis v1.1 — Build Pack Import**.

The long-term Genesis direction includes:

- Repository management
- Asset register management
- Automatic asset numbering
- Dashboarding
- Change log management
- Decision log access
- Build import
- Validation
- Search
- Asset creation and editing
- Asset linking
- Relationship viewing
- Duplicate detection
- Evidence building
- Citation management
- Artificial intelligence-assisted workflows
- Report generation
- Cost Intelligence™
- Product Passport™
- Marketplace support

The exact implementation technology may evolve. The function and role of Project Genesis are more important than preserving any temporary technical approach.

## 14. Scientific production baseline

Current flagship Platinum Knowledge Asset:

```text
CERT-PKS-000001 — Retatrutide
```

Previously discussed modules include:

- Identity
- Mechanism
- Pharmacology
- Pharmacokinetics
- Clinical Outcomes Framework
- Safety
- Monitoring
- Contraindication Matrix
- Comparison Engine
- Patient Journey Engine
- Cost Intelligence™
- Product Passport™ integration
- Report generation
- Mechanism cascade
- Outcome matrix
- Safety monitoring timeline
- Knowledge graph connections
- Artificial intelligence query support

Accuracy rule:

> Previous chat completion percentages are draft estimates only. Retatrutide must not be represented as scientifically complete or Platinum-certified until real evidence objects, citations and review requirements are satisfied.

Planned peptide production backlog has included:

- Retatrutide
- BPC-157
- Tesamorelin
- CJC-1295
- Ipamorelin
- MOTS-c
- GHK-Cu
- Thymosin Beta-4 / TB-500
- Melanotan II
- Epitalon

## 15. Known preservation gap

The repository currently contains a structured foundation and partial reconstruction of prior work.

It does **not** yet contain a complete archival reconstruction of every useful item previously discussed in chat.

Therefore:

- Do not claim that all historic Certiaura intellectual property is already preserved.
- Preservation and migration should continue until all material prior decisions and assets have been captured.
- Future production should be repository-backed so important work is not left only in chat.

## 16. Anti-repetition rule for future recommendations

Before recommending a new:

- Charter
- Governance framework
- Dashboard
- Decision log
- Asset register
- Naming system
- Versioning system
- Release process
- Knowledge architecture
- Relationship architecture
- Repository structure
- Production control system

first check whether that item already exists.

If it already exists, the default action is:

> Use it, extend it, or explicitly amend it — do not reintroduce it as a new concept.

## 17. Default next-action rule

Unless the founder requests otherwise:

1. Continue tangible production;
2. Save reusable output to the repository;
3. Update the relevant register, change log or dashboard where required;
4. Validate;
5. Commit and push;
6. Avoid unnecessary governance discussion.

## 18. Authority

This Charter is the consolidated reference baseline for previously agreed Certiaura decisions as of 2026-07-14.

Where this Charter conflicts with a later explicit founder instruction, the later explicit instruction takes precedence and should be recorded as an amendment or superseding decision.
