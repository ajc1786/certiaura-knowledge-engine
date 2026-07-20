# Retatrutide Controlled Conversation Standard

## Core rule

The conversation layer orchestrates the canonical Build 0043 query engine. It must not answer from model memory or create uncited clinical claims.

## Session controls

- Maximum 12 user turns.
- Pseudonymous session reference and optional pseudonymous patient reference.
- Direct identifiers are rejected before query processing.
- Personalised medical requests remain refused.
- Insufficient evidence remains an explicit abstention.
- Urgent routing locks the session.
- Resetting creates a new session; it does not override an urgent instruction.

## Direct-identifier examples

The baseline blocks common email addresses, telephone-number patterns, National Health Service number patterns, explicit date-of-birth labels and explicit full-name labels. This is a risk-reduction filter, not a complete anonymisation system.

## Audit and provenance

Each exchange records the query SHA-256, response state, retrieval-set SHA-256, warnings and source metadata. Raw request bodies are not written to logs by the local server.
