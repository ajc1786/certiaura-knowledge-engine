# Build 0044 Decision Record

## Decision

Implement a controlled local presentation and conversation layer over the already-installed Build 0043 contracts rather than creating a parallel evidence engine, safety engine or patient data store.

## Rationale

- preserves one source of truth;
- reuses Build 0041 evidence, Build 0042 safety and Build 0043 report/query contracts;
- makes the capability demonstrable without introducing remote hosting, authentication or data-retention risk;
- creates reusable interface, report-rendering and conversation workflow intellectual property;
- keeps uncertain or unsupported questions in explicit abstention.

## Boundaries retained

- investigational status and uncertainty remain visible;
- no diagnosis, prescribing, dosing, titration, procurement or treatment selection;
- no direct identifiers;
- no remote analytics or dependencies;
- no persistent patient data;
- urgent routing cannot be diluted by later conversation turns.

No locked governance decision is amended or superseded.

## Corrected validation-scope decision

Build validation ownership is resolved only from exact package classifications and canonical Build Provenance. Filename substrings, identifier serials and incidental free text are not valid ownership evidence.
