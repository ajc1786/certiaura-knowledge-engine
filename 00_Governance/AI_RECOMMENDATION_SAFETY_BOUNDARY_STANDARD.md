# Certiaura Artificial Intelligence Recommendation Safety Boundary Standard

**Document ID:** CERT-GOV-AI-SAFE-001  
**Version:** 1.0.0  
**Status:** ACTIVE  
**Owner:** Certiaura  
**Build provenance:** CERT-BUILD-0037

## Objective

Define the boundary between permitted educational assistance and outputs requiring human review, regulated-product assessment or prohibition.

## Output taxonomy

| Output type | Description | Default disposition |
|---|---|---|
| SOURCE_NAVIGATION | Locate approved records or evidence | ALLOW |
| EDUCATIONAL_SYNTHESIS | Summarise approved evidence with limitations | ALLOW_WITH_CONTROLS |
| NON_PERSONALISED_COMPARISON | Compare approved attributes without selecting treatment | ALLOW_WITH_CONTROLS |
| PRODUCT_RANKING | Rank products, suppliers or options | HUMAN_REVIEW |
| PERSONALISED_RISK | Infer individual health risk | HUMAN_REVIEW_HIGH_RISK |
| REGIMEN_SUGGESTION | Suggest timing, cycle, stacking or administration | HUMAN_REVIEW_HIGH_RISK |
| DOSE_OR_TITRATION | Calculate or recommend a personal dose or titration | REGULATED_PATHWAY_OR_BLOCK |
| DIAGNOSIS | Determine a disease or condition | REGULATED_PATHWAY_OR_BLOCK |
| PRESCRIPTION_SELECTION | Select a prescription-only medicine | BLOCK_PUBLIC_AUTOMATION |
| TREATMENT_PLAN | Direct clinical treatment | REGULATED_PATHWAY_OR_BLOCK |

## Mandatory gates

An output is blocked from automatic release where any of the following applies:

- diagnosis, prescribing, treatment planning or personalised dosing;
- a prescription-only medicine is promoted to the public;
- the underlying product is unlicensed and a medicinal claim is proposed;
- special-category health data is used without an approved lawful basis, transparency and data-protection controls;
- the system is used for solely automated significant decisions without the required safeguards;
- the output lacks evidence references, uncertainty, limitations or a traceable model/prompt record;
- commercial interest is material but not disclosed;
- the model output conflicts with a current safety, contraindication, regulatory or withdrawal control.

## Human review requirements

High-risk review records must identify:

- reviewer and competence basis;
- exact input and output;
- model and configuration version;
- evidence objects used;
- intended purpose, audience and channel;
- data-protection assessment status;
- medical-device qualification assessment status where relevant;
- commercial-interest disclosure;
- approval, conditional approval, rejection or quarantine decision;
- expiry and monitoring trigger.

## User-facing communication controls

AI outputs must clearly distinguish:

- educational information from professional advice;
- evidence-backed facts from inference;
- general information from personalisation;
- platform-generated ranking from independent scientific conclusion;
- editorial content from paid, affiliate or marketplace influence.

The output must not claim to be a clinician or imply that a human reviewed it where no such review occurred.

## Fail-safe behaviour

When evidence, identity, contraindications, jurisdiction, age, pregnancy status, medication interaction or emergency context is uncertain, the system must narrow the output, disclose the uncertainty and route to appropriate human or emergency support rather than guess.
