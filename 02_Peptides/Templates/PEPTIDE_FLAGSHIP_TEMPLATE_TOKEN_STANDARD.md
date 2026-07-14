# PEPTIDE FLAGSHIP TEMPLATE TOKEN STANDARD

**Version:** 1.0.0

| Token | Meaning |
|---|---|
| `{{PEPTIDE_UAI}}` | Allocated permanent Universal Asset Identifier, e.g. CERT-PKS-XXXXXX |
| `{{PEPTIDE_NAME}}` | Canonical peptide / compound name |
| `{{DEVELOPMENT_CODE}}` | Development code if applicable |
| `{{BUILD_NUMBER}}` | Certiaura build number |
| `{{ASSET_VERSION}}` | Semantic asset version |
| `{{BUILD_DATE}}` | YYYY-MM-DD |
| `{{OWNER}}` | Asset owner |
| `{{STATUS}}` | Current asset status |
| `{{PLAIN_ENGLISH_SUMMARY}}` | Lay summary |
| `{{MECHANISM_SUMMARY}}` | Mechanism summary |
| `{{EVIDENCE_IDS}}` | Linked Evidence Object identifiers |
| `{{SAFETY_IDS}}` | Linked Safety Knowledge System identifiers |
| `{{MONITORING_IDS}}` | Linked Monitoring Knowledge System identifiers |
| `{{CONDITION_IDS}}` | Linked Condition Knowledge System identifiers |
| `{{GOAL_IDS}}` | Linked Goal Knowledge System identifiers |
| `{{CERTIFICATION_BLOCKERS}}` | Open certification blockers |

## Token rules

1. Tokens are placeholders only.
2. A token must not survive in a production asset unless intentionally retained as an unresolved field.
3. `{{PEPTIDE_UAI}}` must be allocated through the established asset-control process.
4. This template must not invent a permanent UAI.
5. Existing canonical object IDs should be referenced, not copied.
6. Missing scientific content should remain explicitly open rather than filled by inference.
