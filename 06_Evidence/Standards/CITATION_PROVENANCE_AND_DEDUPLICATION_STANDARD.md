# Citation Provenance and Deduplication Standard

**UAI:** CERT-EKS-000755
**Version:** 1.0.0

## Identifier precedence

1. DOI
2. PMID / PMCID
3. Trial registry identifier
4. Publisher identifier
5. Normalised title + first author + year
6. Canonical URL

Exact strong-identifier matches are duplicates unless a documented version relationship applies. Fuzzy matches are quarantined for human resolution. Metadata merges must retain field-level provenance and must not silently replace a verified value with a lower-confidence value.

## Citation approval

A citation used for a scientific claim must identify the supporting passage or result, the reviewer, approval state, review date and any limitation affecting interpretation.
