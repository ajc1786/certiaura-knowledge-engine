# CERT-PKS-000001 — RETATRUTIDE

**Version:** 0.7.0  
**Status:** Consolidated — Not Platinum Certified  
**Knowledge System:** PKS  
**Asset Type:** Flagship Peptide Knowledge Asset  
**Owner:** Aidan Coleman  
**Last Review:** 2026-07-14

## 1. Plain-English summary

Retatrutide is a multi-receptor metabolic therapy under active clinical development in the Certiaura evidence model.

The current Certiaura knowledge base contains:

- Primary mechanism and early clinical evidence
- Primary phase 2 obesity evidence
- Primary phase 2 type 2 diabetes evidence
- Primary sponsor topline phase 3 obesity evidence
- An identified phase 3 type 2 diabetes Lancet publication that still requires direct full-text extraction
- Open primary-source gaps for body composition, TRIUMPH-4 and liver-fat / MASLD evidence

This asset is **substantially developed but not Platinum-certified**.

## 2. Identity and mechanism

**Development code:** LY3437943  
**Modality:** Triple receptor agonist

### Core biological relationships

- `CERT-PKS-000001 ACTS_ON CERT-BKS-000010` — GLP-1 Receptor
- `CERT-PKS-000001 ACTS_ON CERT-BKS-000011` — GIP Receptor
- `CERT-PKS-000001 ACTS_ON CERT-BKS-000012` — Glucagon Receptor

### Linked biological pathways

- `CERT-BKS-000001` — GLP-1
- `CERT-BKS-000002` — GIP
- `CERT-BKS-000003` — Glucagon
- `CERT-BKS-000020` — Insulin Secretion
- `CERT-BKS-000021` — Satiety
- `CERT-BKS-000022` — Gastric Emptying
- `CERT-BKS-000023` — Energy Homeostasis

**Primary mechanism evidence:** `CERT-EKS-000007`

## 3. Evidence foundation

| Evidence ID | Domain | Source closure state |
|---|---|---|
| CERT-EKS-000007 | Mechanism / early clinical pharmacology | CLOSED |
| CERT-EKS-000008 | Phase 2 obesity | CLOSED FOR CORE EXTRACTION |
| CERT-EKS-000009 | Phase 2 type 2 diabetes | CLOSED |
| CERT-EKS-000010 | Body composition | OPEN — PRIMARY NOT CAPTURED |
| CERT-EKS-000011 | Phase 3 obesity | CLOSED FOR TOPLINE / OPEN FOR FULL PUBLICATION |
| CERT-EKS-000012 | Phase 3 type 2 diabetes | IDENTIFIED — EXTRACTION BLOCKED |
| CERT-EKS-000013 | TRIUMPH-4 obesity + knee OA | OPEN — PRIMARY NOT CAPTURED |
| CERT-EKS-000014 | Liver-fat / MASLD | OPEN — PRIMARY NOT CAPTURED |

## 4. Controlled clinical findings

### Phase 2 obesity

Primary evidence captured in `CERT-EKS-000008` supports:

- Dose-dependent weight reduction
- Mean body-weight reduction of **24.2% at week 48** in the 12 mg group
- Mean placebo reduction of **2.1%**
- Gastrointestinal adverse events as the most frequent tolerability issue
- A dose-dependent heart-rate increase that peaked around week 24 and subsequently declined

### Phase 2 type 2 diabetes

Primary evidence captured in `CERT-EKS-000009` supports:

- Substantial HbA1c reduction in higher-dose groups at week 24
- Mean HbA1c reductions reaching approximately **2 percentage points**
- Meaningful body-weight reduction by week 36
- Gastrointestinal adverse events as an important tolerability domain
- No severe hypoglycaemia reported in that specific trial context

### Phase 3 obesity — TRIUMPH-1

`CERT-EKS-000011` contains **primary sponsor topline evidence**, not a full peer-reviewed publication.

The sponsor topline reported:

- Mean body-weight reduction of **28.3% at week 80** in the 12 mg group
- A prespecified extension result reaching **30.3% mean reduction at week 104** in the recorded extension population

These figures must remain labelled as sponsor topline evidence until the full publication is captured.

## 5. Safety architecture

| Safety asset | Domain | Current status |
|---|---|---|
| CERT-SKS-000001 | Gastrointestinal adverse events | Established evidence domain |
| CERT-SKS-000002 | Heart-rate increase | Primary phase 2 signal |
| CERT-SKS-000003 | Dysesthesia / abnormal skin sensation | Emerging late-stage signal |
| CERT-SKS-000004 | Treatment discontinuation and tolerability | Cross-study domain |
| CERT-SKS-000005 | Hypoglycaemia context | Context-specific primary evidence |

### Safety interpretation rule

Do not reduce the evidence to a binary **safe / unsafe** label.

Safety interpretation must preserve:

- Dose
- Titration
- Population
- Duration
- Severity
- Discontinuation
- Source status
- Publication status

## 6. Monitoring architecture

| Monitoring asset | Domain |
|---|---|
| CERT-MKS-000001 | HbA1c |
| CERT-MKS-000002 | Fasting Plasma Glucose |
| CERT-MKS-000003 | Body Weight |
| CERT-MKS-000004 | Fasting Insulin |
| CERT-MKS-000005 | HOMA-IR |
| CERT-MKS-000006 | Heart Rate |
| CERT-MKS-000007 | Gastrointestinal Tolerability |
| CERT-MKS-000008 | Dysesthesia / Abnormal Skin Sensation Monitoring |
| CERT-MKS-000009 | Treatment Discontinuation |
| CERT-MKS-000010 | Body Composition |

A Monitoring Knowledge Object identifies an evidence-supported domain.

It does **not** automatically define a universal schedule, threshold or intervention.

## 7. Conditions

- `CERT-CKS-000001` — Obesity
- `CERT-CKS-000002` — Type 2 Diabetes Mellitus
- `CERT-CKS-000003` — Metabolic Syndrome

## 8. Goals

- `CERT-GKS-000001` — Weight Management
- `CERT-GKS-000002` — Metabolic Health
- `CERT-GKS-000003` — Fat Loss

## 9. Pharmacology status

The early evidence base supports a pharmacokinetic rationale compatible with once-weekly clinical development.

This consolidated asset does not invent:

- a universal clinical schedule;
- a validated personal dosing protocol;
- an administration instruction outside the evidence context.

Detailed pharmacology should remain linked to `CERT-EKS-000007` and future dedicated pharmacokinetic assets.

## 10. Cost Intelligence™ integration

The Cost Intelligence™ framework is applicable to this asset.

Potential fields include:

- Cost per vial
- Cost per milligram
- Equipment and consumables
- Shipping
- Total research budget
- Historical price tracking
- Marketplace comparison
- Lifetime cost of ownership

**Build 0007 does not assert a verified universal market price.**

## 11. Product Passport™ integration

Product Passport™ remains a supported integration point.

Potential fields include:

- Supplier
- Manufacturer
- Product identifier
- Batch
- Certificate of Analysis availability
- Storage requirements
- Temperature guidance
- Packaging
- Cost history
- Quality indicators

**No validated commercial Product Passport is attached to this flagship asset in Build 0007.**

## 12. Marketplace and commercial integration

The asset may later support:

- Premium knowledge access
- Professional reports
- Enterprise licensing
- Academy content
- Marketplace resources
- Affiliate resources
- Product Passport™
- Future direct sales where legally permitted and compliant

Marketplace or product linkage must not bypass evidence, product-quality or legal/regulatory controls.

## 13. Regulatory-status control

Build 0007 makes **no regulatory approval claim**.

Regulatory assessment remains an open evidence domain and a certification blocker.

## 14. Evidence maturity

### Stronger / established domains

- Receptor pharmacology and mechanism
- Early clinical pharmacology
- Phase 2 obesity efficacy
- Phase 2 type 2 diabetes efficacy
- Gastrointestinal tolerability domain
- Phase 2 heart-rate signal

### Partially closed domains

- Phase 3 obesity: sponsor topline captured; full publication still required
- Phase 3 type 2 diabetes: primary publication identified; extraction blocked
- Body composition: publication identity known; direct source capture incomplete

### Open domains

- TRIUMPH-4 primary source
- Liver-fat / MASLD primary source
- Long-term safety
- Regulatory assessment
- Independent replication

## 15. Certification status

**Platinum Certified:** No

### Current blockers

1. Direct extraction of the identified phase 3 type 2 diabetes Lancet article
2. Direct capture of the body-composition primary publication
3. Primary-source closure for TRIUMPH-4
4. Primary-source closure for liver-fat / MASLD evidence
5. Long-term safety
6. Regulatory assessment
7. Independent replication

## 16. One-source-of-truth rule

This flagship asset is the **assembly layer**.

It must not become an uncontrolled duplicate of:

- Evidence Objects
- Safety Knowledge Objects
- Monitoring Knowledge Objects
- Cost Intelligence records
- Product Passports

Detailed facts remain in their canonical objects and are referenced here.
