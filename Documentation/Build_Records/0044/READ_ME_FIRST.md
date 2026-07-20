# Certiaura Build 0044 - Read First

**Build title:** retatrutide patient-facing interface, branded report rendering and controlled conversation workflow baseline
**Package status:** Generated candidate requiring the bundled Windows PowerShell 5.1 end-to-end release regression before canonical import.

## Purpose

Build 0044 converts the Build 0043 Retatrutide patient-journey and grounded-query contracts into a controlled local user experience:

- patient-facing report workflow;
- deterministic Certiaura-branded HTML output;
- controlled PDF generation;
- multi-turn evidence-grounded conversation;
- privacy, abstention, refusal and urgent-routing controls.

## Mandatory order

1. Verify the ZIP SHA-256.
2. Run `Scripts/Invoke_Certiaura_Build_0044_Windows_PS51_Regression.ps1` in Windows PowerShell 5.1.
3. Do not import unless the regression ends with `BUILD 0044 WINDOWS POWERSHELL 5.1 REGRESSION: PASS`.
4. Run `Scripts/Run_Certiaura_Build_0044.ps1`.
5. Review the dry-run and enter `APPLY` only when conflicts and errors are empty.
6. Review the staged changes and enter `COMMIT`.
7. Confirm GitHub Actions green before recording `ACTIONS_GREEN_CLOSED`.

## Exact commit message

```text
Add Certiaura Build 0044 retatrutide patient-facing interface, branded report rendering and controlled conversation workflow baseline
```

## Safety boundary

This build is an educational discussion-support baseline. It is not an authenticated patient portal, medical device, clinical decision system or source of personalised treatment instructions.

## Corrected reissue notice

This is the corrected Build 0044 reissue. The first Windows PowerShell 5.1 regression correctly failed closed because the validator treated unrelated historical UAI serial `000044` files as Build 0044 content. This reissue uses exact manifest/provenance scope and includes a deliberate historical-collision regression fixture. Delete or disregard the superseded ZIP and verify the corrected SHA-256 before rerunning.
