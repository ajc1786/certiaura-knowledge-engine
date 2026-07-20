# Retatrutide safety, monitoring, contraindication and clinical-outcome integration baseline

**Build:** 0042
**Flagship parent:** `CERT-PKS-000001`
**Status:** Scientific integration baseline; human review required

## Regulatory boundary

Retatrutide remains investigational, has no approved product label, and is not approved for public use. This asset is evidence intelligence, not prescribing guidance.

There is no approved retatrutide label. This build therefore separates:

1. observed trial adverse events;
2. protocol-specific eligibility exclusions;
3. unresolved or ongoing safety questions;
4. class-derived hypotheses that must not be transposed as retatrutide facts;
5. efficacy outcomes by evidence maturity.

## Integrated safety position

The strongest recurring tolerability signal is gastrointestinal, with nausea, diarrhoea, constipation and vomiting reported across phase 2 and phase 3 programmes. Phase 2 obesity evidence also reported dose-dependent heart-rate increases. Phase 3 reporting adds dysesthesia as a signal requiring structured surveillance. These observations do not constitute an approved safety label.

## Monitoring architecture

Monitoring objects in this package are evidence-review data contracts. They do not define personal thresholds, dosing changes, treatment intervals, diagnosis or emergency management. Every monitoring field must retain population, trial, dose group, time point and evidence source.

## Contraindication architecture

No entry may be labelled an established product contraindication unless supported by a retatrutide-specific approved regulatory label. Trial exclusions remain protocol-specific. Approved GLP-1 or dual-agonist label language must not be silently copied.

## Clinical-outcome integration

Efficacy is integrated with tolerability and evidence maturity. Peer-reviewed randomised evidence, sponsor topline results and ongoing registry records remain visibly distinct. Cardiovascular and renal event reduction is unresolved pending dedicated outcome evidence.

## Source map

The package references the Build 0041 evidence corpus (`RET-EVD-0001` to `RET-EVD-0012`) and official trial registries. Full source URLs are preserved in `RETATRUTIDE_SAFETY_SOURCE_MAP.json`.
