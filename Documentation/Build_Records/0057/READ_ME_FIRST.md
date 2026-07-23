# Certiaura Build 0057 RC1

Title: tesamorelin governed evidence ingestion, provenance validation, monitoring workflow simulation, safety escalation, audit replay and controlled acceptance baseline

Run `Scripts/Run_Certiaura_Build_0057.ps1` through the verified outer launcher. After `BUILD_0057_CANONICAL_VALIDATED_AND_STAGED`, run `Scripts/Close_Certiaura_Build_0057.ps1`. The close script uses the non-interactive Git guard. The regression must emit `NO_MANUAL_GIT_OBJECT_CLEANUP_PROMPTS`, and closure must emit exact Actions evidence before founder `GREEN`.
