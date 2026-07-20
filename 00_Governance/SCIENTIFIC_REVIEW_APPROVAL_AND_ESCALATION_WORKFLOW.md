# Scientific Review Approval and Escalation Workflow

**UAI:** CERT-EKS-000753
**Version:** 1.0.0

## Review roles

- Evidence analyst: prepares the structured evidence record.
- Scientific reviewer: evaluates methods, relevance, certainty and limitations.
- Senior reviewer: resolves high-risk disagreements, safety signals and policy-sensitive conclusions.
- Artificial intelligence: may extract, compare and flag; it is never the final approval authority.

## Decisions

- `APPROVED`: suitable for the declared use.
- `CONDITIONAL`: suitable only with recorded limitations or monitoring.
- `REJECTED`: unsuitable for use.
- `ESCALATED`: senior review required.
- `SUPERSEDED`: replaced by a later controlled review.

## Automatic escalation triggers

Retraction, correction affecting conclusions, unresolved authorship or source identity, material conflict of interest, rights breach, urgent safety signal, high-impact disagreement, or AI-only review.
