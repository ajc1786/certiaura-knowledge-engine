# Customer Eligibility and Jurisdiction Standard

## Control objective

No customer or organisation receives marketplace access solely because an account exists, an identity check passes or an automated score is favourable. Eligibility requires a current legal-route record, intended-use declaration, identity controls, privacy controls, risk review and named human approval.

## Status model

`PENDING → UNDER_REVIEW → ELIGIBLE | CONDITIONAL | INELIGIBLE | SUSPENDED | EXPIRED`

Automation may move a record to `UNDER_REVIEW`, `SUSPENDED` or `EXPIRED` where a blocking control is detected. Only an authorised human reviewer may grant `ELIGIBLE` or `CONDITIONAL`, remove a suspension or approve reinstatement.

## Mandatory gates

- Jurisdiction route is explicitly APPROVED for the customer type and intended use.
- Identity verification is current and proportionate.
- Organisation authority is verified where an organisation is applying.
- Intended use is declared and matches the approved route.
- Responsible-use acknowledgement is current.
- Privacy notice and legal-basis records are current.
- Risk flags are reviewed and conditions recorded.
- Access privileges are least-privilege and time bounded.
- Human decision and independent review are recorded where required.

## Prohibitions

- No automatic eligibility or reinstatement.
- No eligibility in a PROHIBITED route.
- No use of an expired legal review.
- No inferred consent.
- No reuse of identity or health-related data beyond the recorded purpose.
- No conflation of customer eligibility with product, batch or Product Passport™ approval.
