# Build 0058 lessons learned

The build prevents aggregate quality scores from concealing weak or rejected evidence, requires explicit handling of conflicting sources, links recurrent signals across time, and places controlled amendment and pilot continuation behind validation, rollback, audit replay and human approval. The Build 0057 non-interactive Git guard remains mandatory and regression-tested.

RC1 exposed a Windows-only path-normalisation defect: generated report self-exclusion must convert each single backslash to the canonical repository separator before comparing owned paths. RC2 adds this as a mandatory executable regression.
