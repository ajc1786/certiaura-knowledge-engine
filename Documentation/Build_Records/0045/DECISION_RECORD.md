# Build 0045 Decision Record

## Decisions

- Longitudinal data is pseudonymised, append-only and hash chained.
- Review scheduling is administrative and policy driven; it does not make treatment decisions.
- Urgent terms lock routine scheduling and route to immediate clinical assessment.
- Clinician handoff output separates recorded facts, calculations, provenance and questions for clinician judgement.
- Direct identifiers are rejected before persistence or report generation.
- Transactional backups must be outside the canonical repository.
- Validator ownership is resolved only from exact manifest paths and `CERT-BUILD-0045` provenance.

## Same-build correction decision

Build 0045 is reissued under the same build identity because the correction changes no agreed capability or architecture. It repairs raw-seed compatibility in the event engine and strengthens regression evidence. The superseded candidate must not be imported.
