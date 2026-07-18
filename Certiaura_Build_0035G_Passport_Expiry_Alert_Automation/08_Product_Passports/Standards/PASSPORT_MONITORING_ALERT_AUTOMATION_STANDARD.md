# CERTIAURA PRODUCT PASSPORT™ EXPIRY, TRIGGER MONITORING AND ALERT AUTOMATION STANDARD

**Build:** CERT-BUILD-0035G  
**Version:** 1.0.0  
**Status:** Repository-ready approved build  
**Depends on:** CERT-BUILD-0035D, CERT-BUILD-0035E and CERT-BUILD-0035F  
**UAI:** UAI_ALLOCATION_REQUIRED

## 1. Purpose

This standard operationalises the lifecycle controls established by Build 0035F. It governs scheduled and event-driven monitoring of Product Passport™ records, expiry and review thresholds, evidence-refresh alerts, critical-trigger protective actions, review queues and marketplace-status notifications.

The standard is designed to prevent silent expiry, stale public claims, unresolved integrity events and active marketplace representation after a passport becomes ineligible.

## 2. Continuity and scope

This build consumes the 0035F lifecycle record and does not replace or weaken:

- supplier submission controls from 0035D;
- review and verification controls from 0035E;
- publication, lifecycle and marketplace controls from 0035F;
- the Master Asset Register, Decision Log, release controls or Universal Asset & Relationship Standard.

It adds an automation layer that creates deterministic findings, alert records and protective-action instructions.

## 3. Critical automation boundary

> Automation may apply or recommend fail-safe protective restrictions; it must not create a positive assurance or approval.

The monitoring engine must never automatically:

- verify supplier evidence;
- approve a claim for public display;
- publish a passport;
- reinstate a suspended or expired passport;
- approve or restore marketplace eligibility;
- close an integrity, legal or regulatory alert; or
- alter historical evidence or decision records.

Permitted automatic protective outputs are limited to:

- mark a passport as due or overdue for review;
- generate and route alerts;
- queue evidence refresh or human review;
- instruct deterministic expiry where the effective period has ended;
- instruct immediate suspension for an unresolved critical trigger;
- instruct marketplace suspension or removal where 0035F requires it; and
- prevent repeated duplicate alerts through idempotent deduplication keys.

Positive restoration requires a separate authorised human decision under the relevant upstream workflow.

## 4. Monitoring modes

| Mode | Use | Minimum control |
|---|---|---|
| SCHEDULED | Regular portfolio scan | Stable as-of time, policy version and run identifier |
| EVENT_DRIVEN | Trigger received from evidence, supplier, marketplace or legal source | Source event identifier and received timestamp |
| MANUAL | Controlled reviewer-initiated scan | Named executor and reason |
| REPLAY | Re-evaluation of historical inputs after policy change | Original as-of time, replay reason and new policy version |

Production scheduling is held in `MONITORING_SCHEDULE_REGISTER.csv`.

## 5. Monitoring inputs

Each scan must use an immutable snapshot or content hash of the source lifecycle record. The minimum input is:

- passport identifier and version;
- lifecycle state;
- publication effective-from, effective-until and next-review dates;
- controlling 0035E review effective-until date;
- public claim next-review dates;
- marketplace state and marketplace next-review date;
- open lifecycle events, their severity and status;
- supplier authority status where available; and
- the source-record SHA-256 hash.

A malformed or unhashed input is quarantined from automatic action and routed for data-quality review.

## 6. Standard checks

Every monitoring run evaluates, where applicable:

1. Passport effective-until threshold.
2. Passport next-review threshold.
3. Controlling 0035E review effective-until threshold.
4. Public claim next-review thresholds.
5. Marketplace decision next-review threshold.
6. Open high or critical lifecycle events.
7. Evidence-withdrawal, report-integrity, batch-mismatch, counterfeit and legal-regulatory triggers.
8. Supplier or manufacturer identity change.
9. Public price, availability, storage, temperature, shelf-life or specification change.
10. Successor-passport publication.
11. Alert ageing and escalation.
12. Duplicate-alert suppression.
13. Source-record hash change since the last completed run.

## 7. Expiry and review thresholds

The default thresholds are held in `EXPIRY_THRESHOLD_MATRIX.csv`.

For future target dates, alerts are generated at 60, 30, 14, 7 and 1 calendar day before the target. At zero or negative days remaining:

- an expired `effective_until` date creates `PASSPORT_EXPIRED` and instructs passport state `EXPIRED`;
- an expired controlling review creates `UPSTREAM_REVIEW_EXPIRED` and instructs passport suspension pending re-verification;
- an overdue next-review date creates `REVIEW_OVERDUE`, queues urgent human review and suspends active marketplace eligibility until review; and
- an overdue claim-review date creates `CLAIM_REVIEW_OVERDUE`; affected public claims must be hidden or the passport suspended where claim-level suppression is not supported.

A warning threshold never extends the underlying validity period.

## 8. Trigger severity and protective actions

| Trigger class | Default severity | Automatic protective action | Human decision required |
|---|---:|---|---:|
| Evidence withdrawn | CRITICAL | Suspend passport and marketplace | Yes, for resolution or reinstatement |
| Report integrity dispute | CRITICAL | Suspend passport and marketplace | Yes |
| Batch mismatch | CRITICAL | Suspend passport; remove marketplace listing | Yes |
| Legal or regulatory alert | CRITICAL | Suspend passport; remove marketplace listing | Yes |
| Counterfeit or duplicate concern | CRITICAL | Suspend passport; remove marketplace listing | Yes |
| Open high-severity lifecycle event | HIGH | Suspend marketplace; queue passport review | Yes |
| Effective period expired | HIGH | Set passport to expired; remove marketplace eligibility | Yes, for any successor or reinstatement route |
| Review overdue | HIGH | Suspend marketplace; queue urgent review | Yes |
| Upcoming expiry or review | LOW to HIGH | Alert and queue evidence refresh | Yes, to renew |
| Price or availability change | MEDIUM | Queue display review | Yes where public data changes |

No automatic action may reduce severity, close an event or restore a positive state.

## 9. Alert model

Every alert must contain:

- permanent alert identifier;
- passport identifier and version;
- alert type and severity;
- detection and due timestamps;
- target date where applicable;
- finding codes and source event identifiers;
- deduplication key;
- owner or routing group;
- required action;
- proposed passport and marketplace states;
- status and escalation level;
- first-seen and last-seen timestamps; and
- immutable audit metadata.

The deduplication key is stable for the same passport, finding type, threshold and target date. A repeated scan updates `last_seen_at` or suppresses a duplicate; it must not create uncontrolled alert multiplication.

## 10. Alert routing

Routing follows `ALERT_ROUTING_MATRIX.csv`.

Minimum routes are:

- Product Passport review queue;
- Evidence review queue;
- Marketplace operations queue;
- legal and regulatory escalation queue;
- supplier clarification queue; and
- platform data-quality queue.

Critical alerts require immediate multi-route notification. Delivery failure is itself recorded as an alert-delivery event and escalated through a fallback route.

## 11. Review queue priorities

| Priority | Entry criteria | Target response |
|---|---|---|
| P0 | Critical integrity, legal, counterfeit or batch mismatch | Immediate |
| P1 | Expired validity, overdue mandatory review or open high trigger | Same business day |
| P2 | 1–7 days to expiry or review | 1 business day |
| P3 | 8–30 days to expiry or review | 3 business days |
| P4 | 31–60 days to expiry or review | Normal planning cycle |

Queue priority does not replace severity. Both values are retained.

## 12. Marketplace notifications

Where a finding requires `SUSPENDED`, `REMOVED` or `INELIGIBLE` marketplace state, the automation output must:

- identify the controlling finding;
- state the required marketplace action;
- route the notification to marketplace operations;
- record whether acknowledgement was received;
- prevent a later monitoring run from assuming the action was completed without a recorded transaction; and
- prohibit automatic restoration.

## 13. Deterministic expiry

Expiry is calculated against the run `as_of` date in Coordinated Universal Time. A date is expired when it is earlier than `as_of.date()`.

The engine must not use local workstation time without recording the timezone. Scheduled production runs should use a trusted platform clock.

## 14. Idempotency and concurrency

Each run requires:

- unique `run_id`;
- `policy_version`;
- input file hash or record hash;
- stable alert deduplication keys;
- start and completion timestamps;
- run status; and
- a lock or equivalent transaction control in production.

Two concurrent scans must not create contradictory state instructions or duplicate open alerts. Where the source hash changes during a run, the result is marked `STALE_INPUT` and no automatic protective transaction is applied until re-scanned.

## 15. Monitoring run states

- `STARTED`
- `COMPLETED`
- `COMPLETED_WITH_ALERTS`
- `PARTIAL`
- `FAILED`
- `STALE_INPUT`

A failed or partial run cannot be represented as a complete portfolio check.

## 16. Audit and immutability

Monitoring run records and alerts are immutable evidence of what the system observed at a point in time. Corrections create a new run, alert event or superseding record.

The audit record must preserve:

- executor;
- run timestamps;
- as-of date;
- policy version;
- source hashes;
- engine version;
- findings;
- action instructions;
- notification outcomes; and
- validation result.

## 17. Project Genesis enforcement

Project Genesis should implement this build in stages:

1. Read-only dry-run portfolio scan.
2. Alert and queue generation.
3. Notification delivery with acknowledgement tracking.
4. Transactional protective-state application.
5. Scheduled execution, locking and dashboards.

The supplied engine is deliberately read-only. It produces a machine-readable monitoring run and alert queue without editing the source lifecycle records. Repository integration may later consume the action instructions through audited transactions.

## 18. Validation gates

A monitoring run fails validation where, among other controls:

- an automatic positive approval or reinstatement is proposed;
- expired validity does not create an expiry action;
- an unresolved critical trigger does not create passport and marketplace suspension/removal;
- an active marketplace state is proposed for an inactive passport;
- source hashes are absent or malformed;
- alert identifiers or deduplication keys are duplicated;
- a critical alert is routed only to a low-priority queue;
- alert due time precedes detection time without an overdue explanation;
- run totals do not reconcile to findings and alerts; or
- the audit record is not immutable.

## 19. Acceptance criteria

Build 0035G is accepted when:

- the valid no-action monitoring run passes;
- the valid expiry-and-critical-alert run passes;
- the deliberately invalid auto-reinstatement run fails;
- engine tests demonstrate threshold, expiry, critical-trigger and deduplication behaviour;
- all unit tests pass using the Python standard library only; and
- the complete build ZIP passes integrity testing.
