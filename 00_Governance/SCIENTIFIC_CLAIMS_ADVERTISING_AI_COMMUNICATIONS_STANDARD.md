# Certiaura Scientific Claims, Advertising, Artificial Intelligence Recommendation and Communications Standard

**Document ID:** CERT-GOV-CLAIMS-001  
**Version:** 1.0.0  
**Status:** ACTIVE  
**Owner:** Certiaura  
**Build provenance:** CERT-BUILD-0037

## 1. Purpose

This Standard controls how Certiaura creates, reviews, approves, publishes, monitors, corrects and withdraws scientific, health, medicinal, commercial and artificial-intelligence-assisted communications.

It applies to knowledge assets, reports, Product Passport™ content, marketplace content, Academy materials, websites, applications, artificial intelligence outputs, social media, affiliate communications, email, advertising and sales-support materials.

## 2. Governing principles

1. **Claim-level traceability.** Every material claim must be recorded exactly as communicated and linked to evidence, jurisdiction, audience, channel, approval and review status.
2. **Evidence before amplification.** A source summary, supplier statement or repeated market claim is not evidence merely because it is widely circulated.
3. **Scientific and commercial separation.** Editorial evidence assessment must not be altered to improve conversion, affiliate revenue or supplier acceptance.
4. **No evidence laundering.** Certiaura must not convert tentative, indirect, preclinical, low-quality or supplier-generated evidence into a stronger public claim.
5. **No silent artificial intelligence authority.** Artificial intelligence may assist retrieval, synthesis and drafting, but must not be presented as a clinician, regulator or autonomous authority.
6. **Human accountability.** High-risk outputs require an identified, competent human approver and an auditable decision.
7. **Audience protection.** Communications must account for vulnerable audiences, health anxiety, desperation, urgency, impaired decision-making and financial pressure.
8. **Commercial transparency.** Affiliate, sponsor, supplier, ownership and marketplace interests must be declared clearly where material.
9. **Expiry by design.** Approval is time-limited. Material scientific, regulatory, safety or product changes trigger re-review.
10. **Correction is mandatory.** Materially inaccurate or outdated communications must be corrected, withdrawn or quarantined without waiting for a routine review date.

## 3. Claim classes

| Class | Definition | Default risk |
|---|---|---:|
| FACTUAL_IDENTITY | Verifiable identity, composition or administrative fact | Low |
| SCIENTIFIC_EDUCATIONAL | Neutral explanation of mechanisms, studies or evidence | Medium |
| COMPARATIVE | Comparison between compounds, products, suppliers or approaches | Medium–High |
| HEALTH | Claim relating to health, physiological function, risk or outcome | High |
| MEDICINAL | Claim to prevent, diagnose, treat, cure or modify disease | High–Prohibited |
| SAFETY | Claim about safety, tolerability, absence of risk or side effects | High |
| COMMERCIAL | Claim intended to influence a transaction or product choice | Medium–High |
| TESTIMONIAL | Personal experience or endorsement used as evidence or persuasion | High |
| AI_RECOMMENDATION | Artificial-intelligence-generated selection, ranking, recommendation or personalised conclusion | High |

A single communication may contain multiple claim classes. The highest applicable risk governs the approval route.

## 4. Minimum claim record

Every material claim must record:

- stable claim identifier;
- exact claim text;
- claim class and risk level;
- intended audience and jurisdiction;
- channel and commercial purpose;
- named product, compound, supplier or service;
- regulatory classification where relevant;
- evidence object identifiers and source links;
- evidence strength, limitations and uncertainty;
- required warnings, qualifiers and disclosures;
- artificial intelligence involvement;
- medical, scientific, legal, regulatory and commercial review decisions as applicable;
- final disposition, approver, approval date and expiry date;
- withdrawal, correction and supersession history.

## 5. Prohibited or blocked patterns

The following are blocked unless an applicable lawful, regulated and approved route is evidenced:

- guaranteed outcomes;
- “100% safe”, “risk free”, “no side effects” or equivalent absolute safety claims;
- diagnosis, prescribing or treatment plans presented as autonomous Certiaura artificial intelligence output;
- public promotion of prescription-only medicines;
- medicinal claims for unlicensed products;
- claims that discourage essential professional care or prescribed treatment;
- undisclosed affiliate, sponsor or supplier influence;
- fabricated citations, unverifiable studies or references that do not support the communicated claim;
- urgency, scarcity or fear framing that exploits illness or vulnerability;
- testimonials presented as proof of efficacy or safety;
- implying regulator, clinician or Certiaura verification where only a supplier submission or structural check exists.

## 6. Evidence sufficiency

Evidence sufficiency is determined at claim level, not document level. The reviewer must assess:

- directness to the exact claim;
- relevance to the named compound, formulation, population, outcome and route;
- study design, sample size and uncertainty;
- replication and consistency;
- publication status and source quality;
- conflicts of interest;
- date and regulatory context;
- whether the proposed wording is weaker than, equal to or stronger than the evidence.

A claim must be narrowed, qualified, delayed or rejected where evidence does not support the proposed wording.

## 7. Approval levels

| Level | Typical content | Mandatory approval |
|---|---|---|
| L1 | Administrative or low-risk factual content | Content owner |
| L2 | Scientific educational content with no product promotion | Scientific reviewer |
| L3 | Health, comparison, safety or commercial content | Scientific reviewer plus responsible communications reviewer |
| L4 | Medicinal, prescription-only medicine, personalised health, regulated product or high-risk AI content | Scientific/medical and legal/regulatory review; release only through an approved route |
| BLOCKED | Unlawful, unsupported, misleading or unsafe communication | Reject or quarantine |

## 8. Channel controls

The same wording may require a different decision in a different channel. Public advertising, marketplace placement, social media and affiliate content receive the strictest commercial interpretation. Internal research notes and professional reports remain controlled but may contain more technical uncertainty where the audience and context are explicit.

## 9. Artificial intelligence controls

Artificial intelligence may:

- retrieve and summarise approved evidence;
- explain uncertainty and evidence strength;
- compare approved data without making an autonomous treatment decision;
- direct users to professional care, emergency services or source material;
- draft content for human review.

Artificial intelligence must not, without an approved regulated pathway and competent human accountability:

- diagnose a condition;
- prescribe or select a prescription-only medicine;
- create a personalised dose, cycle, treatment plan or titration schedule;
- represent itself as a clinician;
- conceal uncertainty or commercial influence;
- fabricate evidence or imply certainty beyond the source record.

## 10. Monitoring, correction and withdrawal

Triggers include new safety information, regulatory action, evidence reversal, material supplier or product change, citation invalidation, complaint, adverse-event signal, model behaviour defect, expired approval or material wording drift.

On trigger, the content owner must set the claim to `REVIEW_REQUIRED`, `SUSPENDED`, `WITHDRAWN` or `CORRECTED`, identify all downstream uses and record the action in the applicable registers.

## 11. Record retention

Claim records, evidence snapshots, approvals, prompts, generated outputs, disclosures, corrections and withdrawal records must be retained in accordance with Certiaura change control and audit requirements.

## 12. Boundary

This is an operational governance control. It does not replace case-specific legal, regulatory, medical, data-protection or advertising advice.
