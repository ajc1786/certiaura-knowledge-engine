# Build 0036 Validation Report

**Build:** CERT-BUILD-0036  
**Date:** 2026-07-19  
**Result:** PASS — repository-ready

## Validator results

- Valid individual eligibility: PASS
- Valid conditional organisation eligibility: PASS
- Invalid automatic eligibility: FAIL as designed — 19 breaches
- Invalid prohibited-jurisdiction eligibility: FAIL as designed — 4 breaches
- Valid privacy rights request: PASS
- Invalid automated privacy closure: FAIL as designed — 8 breaches
- Valid critical surveillance signal: PASS
- Valid trend signal: PASS
- Invalid automated signal closure: FAIL as designed — 22 breaches

## Technical validation

- Automated tests: 56/56 passed
- JSON files parsed: 25
- Python files compiled: 24
- Automation outputs: generated successfully
- Dashboards: generated successfully
- External Python packages: none
- Filename length: 67 characters

## Control conclusion

The pack blocks automatic customer approval, prohibited-jurisdiction eligibility, automated privacy closure, automated surveillance closure and automated reportability decisions. Generated analytics and alerts remain advisory or protective only.
