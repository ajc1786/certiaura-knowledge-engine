# CERTIAURA PRODUCT PASSPORT™ PUBLICATION, LIFECYCLE AND MARKETPLACE CONTROL STANDARD

**Build:** CERT-BUILD-0035F  
**Version:** 1.0.0  
**Status:** Repository-ready approved build  
**Depends on:** CERT-BUILD-0035D and CERT-BUILD-0035E  
**UAI:** UAI_ALLOCATION_REQUIRED

## 1. Purpose

This standard governs how a Product Passport™ moves from an approved 0035E review decision into controlled publication, lifecycle monitoring, suspension, expiry, supersession and marketplace eligibility.

It ensures that:

- only specifically verified and public-display-approved claims are published;
- publication does not imply regulatory approval, clinical suitability or marketplace admission;
- every public record has an effective period, review date and audit trail;
- material changes trigger review, suspension or withdrawal;
- marketplace eligibility remains a separate, documented decision;
- expired, suspended, withdrawn or superseded passports cannot remain represented as current; and
- public, member-only and internal fields are explicitly separated.

## 2. Dependencies and continuity

This build consumes but does not alter:

- the 0035D supplier submission object;
- the 0035E review decision object;
- the Product Passport System (PPS);
- the Evidence Knowledge System (EKS);
- the Marketplace System (MPS);
- the Master Asset Register, Decision Log or existing release controls.

A 0035E `VERIFIED` decision is necessary for publication but is not sufficient for marketplace eligibility.

## 3. Core rules

1. **Publication is claim-specific.** Only claims marked `VERIFIED` and `public_display_approved=true` in the controlling 0035E review may be published.
2. **Public status is time-bound.** Every published passport requires `effective_from`, `effective_until` and `next_review_date`.
3. **No silent continuation.** Expiry, unresolved critical triggers or upstream invalidation blocks current publication.
4. **Lifecycle records are immutable snapshots.** Corrections create a superseding version or event; they do not rewrite history.
5. **Marketplace eligibility is separate.** Evidence verification alone cannot approve sale, promotion, fulfilment or listing.
6. **Visibility is explicit.** Every field is classified as `PUBLIC`, `MEMBER`, or `INTERNAL`.
7. **Suspension is fail-safe.** Where a material risk cannot promptly be resolved, public current-status and marketplace eligibility are suspended.
8. **Supersession is linked.** A superseded passport identifies its successor and records a `SUPERSEDES` relationship.
9. **Public wording is bounded.** Public claims must retain scope statements and limitations and must not be reframed as medical, regulatory or safety assurances.
10. **Marketplace state follows the stricter control.** A passport may be published but marketplace-ineligible; it may not be marketplace-eligible while unpublished, suspended, expired, withdrawn or superseded.

## 4. Lifecycle states

| State | Meaning | Public current display | Marketplace eligible |
|---|---|---:|---:|
| DRAFT | Record being prepared | No | No |
| READY_FOR_PUBLICATION | Gates complete; awaiting release | No | No |
| PUBLISHED | Active public passport | Yes | Potentially, by separate decision |
| SUSPENDED | Temporarily removed from current representation | No | No |
| EXPIRED | Effective period ended | No | No |
| WITHDRAWN | Intentionally removed | No | No |
| SUPERSEDED | Replaced by a newer passport/version | Historical only | No |
| ARCHIVED | Retained for record purposes | No | No |

Permitted standard transitions are held in `PASSPORT_STATE_MATRIX.csv`.

## 5. Publication gates

Before `PUBLISHED`, all of the following are mandatory:

- controlling 0035E decision status is `VERIFIED`;
- 0035E public passport eligibility is `ELIGIBLE`;
- source review decision hash is recorded;
- at least one public claim is present;
- every public claim matches an upstream verified claim identifier;
- every public claim retains evidence class, scope and limitations;
- no public claim exceeds the scope of the controlling review;
- effective and review dates are valid and current;
- publisher and publication timestamp are recorded;
- public URL or slug is unique;
- mandatory disclaimers are present;
- no unresolved `CRITICAL` lifecycle event exists; and
- visibility classification has been applied to all display fields.

## 6. Public claim object

Each public claim records:

- claim identifier;
- category;
- display value;
- evidence class;
- source review decision identifier;
- scope statement;
- limitations;
- last verified date;
- next review date; and
- visibility.

Public claims must not imply any of the following unless separately and lawfully evidenced and approved:

- regulatory approval;
- treatment effectiveness;
- safety for an individual;
- suitability for human use;
- prescribing authority;
- sterility where only purity or identity was tested; or
- equivalence between untested batches.

## 7. Visibility controls

### PUBLIC

Permitted for approved public display, subject to the controlling review. Typical examples include supplier trading name, product identifier, batch identifier, approved claim summaries, evidence class, review date, limitations and passport status.

### MEMBER

Available only to authorised member tiers. Examples may include extended evidence summaries, cost history or fuller analytical context where lawful and licensed.

### INTERNAL

Never rendered publicly. Examples include reviewer personal details, conflict declarations, internal escalation notes, unredacted contact details, security information and unpublished evidence files.

The `PUBLIC_FIELD_MATRIX.csv` supplies the baseline classification. A stricter classification may always be applied.

## 8. Lifecycle monitoring

Lifecycle monitoring operates on events, not informal notes. Each event records:

- event identifier and passport identifier;
- event type;
- detection time and source;
- severity;
- description;
- required action;
- owner and due date;
- resolution state; and
- resulting passport and marketplace state.

Mandatory trigger categories include:

- evidence expiry or withdrawal;
- supplier or manufacturer identity change;
- product or batch mismatch;
- altered or disputed laboratory report;
- material label or specification change;
- regulator or legal escalation;
- adverse integrity information;
- duplicate or counterfeit concern;
- material price or availability change where displayed;
- change to storage, temperature or shelf-life claims;
- marketplace terms failure;
- unresolved conflict of interest; and
- successor passport publication.

## 9. Trigger response

- `LOW`: log and review during normal cycle unless aggregation increases risk.
- `MEDIUM`: assign owner and due date; assess whether public notes or conditions are needed.
- `HIGH`: immediate review; suspend marketplace eligibility and consider passport suspension.
- `CRITICAL`: immediately suspend public current-status and marketplace eligibility pending formal resolution.

A passport cannot remain `PUBLISHED` with an unresolved `CRITICAL` event.

## 10. Expiry and review

A passport expires automatically when `effective_until` passes unless a valid superseding record is published before that date.

The next review date must not be later than the effective-until date. Review may be accelerated by any lifecycle trigger.

Expiry does not delete the historical record. The public interface may retain a clearly labelled historical record where permitted, but it must not present it as current.

## 11. Suspension, withdrawal and reinstatement

### Suspension

Suspension is temporary and requires:

- recorded reason;
- suspension timestamp;
- initiating event;
- decision owner;
- required corrective action; and
- marketplace state set to `SUSPENDED` or `REMOVED`.

### Withdrawal

Withdrawal is final for that record version and requires a reason and authority. A replacement must be issued as a new or superseding record.

### Reinstatement

Reinstatement requires a new lifecycle decision confirming that the initiating issue is resolved, upstream verification remains valid and all publication gates pass. Marketplace eligibility must be separately restored.

## 12. Supersession

A `SUPERSEDED` passport must:

- identify the successor passport;
- record the supersession date and reason;
- retain historical audit access;
- prevent current marketplace eligibility; and
- include a `SUPERSEDES` relationship from the successor to the previous passport.

## 13. Marketplace eligibility

Marketplace states are:

- `NOT_ASSESSED`;
- `ELIGIBLE`;
- `CONDITIONALLY_ELIGIBLE`;
- `INELIGIBLE`;
- `SUSPENDED`; and
- `REMOVED`.

`ELIGIBLE` requires, at minimum:

- passport state `PUBLISHED`;
- controlling review decision `VERIFIED`;
- legal and regulatory assessment recorded as complete for the intended listing route;
- supplier identity and authority current;
- product and batch identifiers current where batch listing applies;
- no unresolved high or critical marketplace trigger;
- commercial terms and availability review current;
- marketplace approver identified;
- decision basis, date and review date recorded; and
- no statement that marketplace admission proves safety, efficacy or regulatory approval.

`CONDITIONALLY_ELIGIBLE` must list explicit conditions, actions, owners and due dates. It cannot override a legal prohibition, expired passport or critical integrity concern.

## 14. Marketplace and publication separation

The following are valid combinations:

- `PUBLISHED` + `NOT_ASSESSED`;
- `PUBLISHED` + `INELIGIBLE`;
- `PUBLISHED` + `CONDITIONALLY_ELIGIBLE`;
- `PUBLISHED` + `ELIGIBLE`.

The following are prohibited:

- non-`PUBLISHED` passport + `ELIGIBLE`;
- expired passport + active listing;
- suspended passport + active listing;
- unresolved critical trigger + active listing;
- marketplace decision based solely on evidence verification; or
- automatic restoration of marketplace eligibility following passport reinstatement.

## 15. Audit and relationships

Every lifecycle record must retain:

- immutable creation metadata;
- source submission identifier;
- source review decision identifier and hash;
- passport version;
- prior and successor passport links where applicable;
- lifecycle event links;
- marketplace decision links; and
- relationship entries compatible with the Universal Asset & Relationship Standard.

Applicable relationship types include `HAS_PASSPORT`, `HAS_EVIDENCE`, `HAS_PRODUCT`, `RELATED_TO`, `SUPERSEDES`, `HAS_WARNING` and `REQUIRES`.

## 16. Project Genesis enforcement

The 0035F validator checks the critical machine-enforceable controls, including:

- state validity and permitted combinations;
- publication gate completion;
- date ordering and active-period rules;
- public claim provenance;
- critical trigger blocking;
- marketplace separation;
- suspension and supersession controls; and
- immutable audit requirements.

Schema validation alone is not sufficient. Repository validation must run the semantic validator and unit tests.
