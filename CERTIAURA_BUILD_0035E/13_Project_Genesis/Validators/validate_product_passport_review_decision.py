#!/usr/bin/env python3
"""Validate a Certiaura Build 0035E Product Passport review decision.

This validator uses the Python standard library only. Passing confirms defined
structural and logical controls; it does not authenticate evidence or make a
legal, regulatory, medical or commercial determination.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

REVIEW_ID_RE = re.compile(r"^PPS-REV-[A-Z0-9-]{6,64}$")
SUBMISSION_ID_RE = re.compile(r"^PPS-SUB-[A-Z0-9-]{6,64}$")
EVIDENCE_ID_RE = re.compile(r"^EVD-[A-Z0-9-]{3,64}$")
CLAIM_ID_RE = re.compile(r"^CLM-[A-Z0-9-]{3,64}$")
SHA_RE = re.compile(r"^[a-fA-F0-9]{64}$")
RISK_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
ALLOWED_TRANSITIONS = {
    "SUBMITTED": {"EVIDENCE_REVIEW", "CLARIFICATION_REQUIRED", "QUARANTINED", "REJECTED"},
    "INTAKE_CHECK": {"EVIDENCE_REVIEW", "CLARIFICATION_REQUIRED", "QUARANTINED", "REJECTED"},
    "EVIDENCE_REVIEW": {"CLARIFICATION_REQUIRED", "QUARANTINED", "REJECTED", "CONDITIONALLY_ACCEPTED", "VERIFIED"},
    "CLARIFICATION_REQUIRED": {"EVIDENCE_REVIEW", "QUARANTINED", "REJECTED", "CONDITIONALLY_ACCEPTED", "VERIFIED"},
    "CONDITIONALLY_ACCEPTED": {"EVIDENCE_REVIEW", "VERIFIED", "EXPIRED", "REJECTED"},
    "VERIFIED": {"EXPIRED", "QUARANTINED", "SUPERSEDED"},
    "EXPIRED": {"EVIDENCE_REVIEW", "SUPERSEDED"},
    "QUARANTINED": {"EVIDENCE_REVIEW", "REJECTED", "SUPERSEDED"},
    "REJECTED": {"SUPERSEDED"},
    "SUPERSEDED": set(),
}


def is_date(v: Any) -> bool:
    try:
        return isinstance(v, str) and bool(date.fromisoformat(v))
    except ValueError:
        return False


def is_datetime(v: Any) -> bool:
    try:
        return isinstance(v, str) and bool(datetime.fromisoformat(v.replace("Z", "+00:00")))
    except ValueError:
        return False


def req_str(obj: dict[str, Any], key: str, path: str, errors: list[str]) -> str:
    v = obj.get(key)
    if not isinstance(v, str) or not v.strip():
        errors.append(f"{path}.{key}: required non-empty string")
        return ""
    return v


def validate_review(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root: review decision must be a JSON object"]

    if data.get("schema_version") != "1.0.0":
        errors.append("schema_version: must equal 1.0.0")
    rid = data.get("review_decision_id")
    if not isinstance(rid, str) or not REVIEW_ID_RE.fullmatch(rid):
        errors.append("review_decision_id: invalid")
    sid = data.get("submission_id")
    if not isinstance(sid, str) or not SUBMISSION_ID_RE.fullmatch(sid):
        errors.append("submission_id: invalid")
    if data.get("source_submission_schema_version") != "1.0.0":
        errors.append("source_submission_schema_version: must equal 1.0.0")
    digest = data.get("source_submission_sha256")
    if not isinstance(digest, str) or not SHA_RE.fullmatch(digest):
        errors.append("source_submission_sha256: must be 64 hexadecimal characters")

    source = data.get("source_submission_status")
    target = data.get("target_submission_status")
    if source not in ALLOWED_TRANSITIONS:
        errors.append("source_submission_status: invalid")
    elif target not in ALLOWED_TRANSITIONS[source]:
        errors.append(f"state transition: {source} -> {target} is not permitted")

    if not is_datetime(data.get("review_started_at")):
        errors.append("review_started_at: invalid ISO date-time")
    if not is_datetime(data.get("review_completed_at")):
        errors.append("review_completed_at: invalid ISO date-time")

    team = data.get("review_team")
    lead_name = approver_name = ""
    if not isinstance(team, dict):
        errors.append("review_team: required object")
    else:
        lead = team.get("lead_reviewer")
        if not isinstance(lead, dict):
            errors.append("review_team.lead_reviewer: required object")
        else:
            lead_name = req_str(lead, "name", "review_team.lead_reviewer", errors)
            req_str(lead, "role", "review_team.lead_reviewer", errors)
            if lead.get("conflict_declared") is not True:
                errors.append("review_team.lead_reviewer.conflict_declared: must be true")
        approver = team.get("final_approver")
        if isinstance(approver, dict):
            approver_name = req_str(approver, "name", "review_team.final_approver", errors)
            req_str(approver, "role", "review_team.final_approver", errors)
            if approver.get("conflict_declared") is not True:
                errors.append("review_team.final_approver.conflict_declared: must be true")

    intake = data.get("intake_assessment")
    if not isinstance(intake, dict):
        errors.append("intake_assessment: required object")
        intake = {}

    evidence_reviews = data.get("evidence_reviews")
    if not isinstance(evidence_reviews, list):
        errors.append("evidence_reviews: must be an array")
        evidence_reviews = []
    evidence_by_id: dict[str, dict[str, Any]] = {}
    for i, ev in enumerate(evidence_reviews):
        path = f"evidence_reviews[{i}]"
        if not isinstance(ev, dict):
            errors.append(f"{path}: must be object")
            continue
        eid = ev.get("evidence_id")
        if not isinstance(eid, str) or not EVIDENCE_ID_RE.fullmatch(eid):
            errors.append(f"{path}.evidence_id: invalid")
        elif eid in evidence_by_id:
            errors.append(f"{path}.evidence_id: duplicate {eid}")
        else:
            evidence_by_id[eid] = ev
        if not is_datetime(ev.get("reviewed_at")):
            errors.append(f"{path}.reviewed_at: invalid ISO date-time")
        req_str(ev, "reviewer", path, errors)
        if ev.get("outcome") == "ACCEPTED" and ev.get("integrity_status") != "PASS":
            errors.append(f"{path}: ACCEPTED evidence requires integrity_status PASS")
        if ev.get("outcome") in {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"} and ev.get("applicability_confirmed") is not True:
            errors.append(f"{path}: accepted evidence requires applicability_confirmed true")

    claims = data.get("claim_reviews")
    if not isinstance(claims, list) or not claims:
        errors.append("claim_reviews: at least one claim review required")
        claims = []
    claim_ids = set()
    for i, claim in enumerate(claims):
        path = f"claim_reviews[{i}]"
        if not isinstance(claim, dict):
            errors.append(f"{path}: must be object")
            continue
        cid = claim.get("claim_id")
        if not isinstance(cid, str) or not CLAIM_ID_RE.fullmatch(cid):
            errors.append(f"{path}.claim_id: invalid")
        elif cid in claim_ids:
            errors.append(f"{path}.claim_id: duplicate {cid}")
        else:
            claim_ids.add(cid)
        if not is_date(claim.get("review_date")):
            errors.append(f"{path}.review_date: invalid ISO date")
        req_str(claim, "reviewer", path, errors)
        links = claim.get("evidence_ids")
        if not isinstance(links, list):
            errors.append(f"{path}.evidence_ids: must be an array")
            links = []
        for eid in links:
            if eid not in evidence_by_id:
                errors.append(f"{path}.evidence_ids: unknown evidence {eid}")
        if claim.get("decision") == "VERIFIED":
            if not links:
                errors.append(f"{path}: VERIFIED claim requires evidence")
            if claim.get("evidence_class_awarded") not in {"E4", "E5"}:
                errors.append(f"{path}: VERIFIED claim requires evidence class E4 or E5")
            if claim.get("batch_specific") is True and claim.get("batch_link_confirmed") is not True:
                errors.append(f"{path}: batch-specific VERIFIED claim requires batch link")
            for eid in links:
                ev = evidence_by_id.get(eid, {})
                if ev.get("outcome") not in {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"}:
                    errors.append(f"{path}: VERIFIED claim relies on non-accepted evidence {eid}")
                if ev.get("expiry_status") == "EXPIRED":
                    errors.append(f"{path}: VERIFIED claim relies on expired evidence {eid}")
        if claim.get("public_display_approved") is True and claim.get("decision") != "VERIFIED":
            errors.append(f"{path}: public display requires VERIFIED claim")

    risk = data.get("risk_assessment")
    if not isinstance(risk, dict):
        errors.append("risk_assessment: required object")
        risk = {}
    risk_keys = ["integrity_risk","supplier_identity_risk","manufacturer_identity_risk","product_identity_risk","batch_traceability_risk","evidence_independence_risk","expiry_risk","regulatory_misrepresentation_risk","conflict_of_interest_risk"]
    levels = []
    for key in risk_keys:
        level = risk.get(key)
        if level not in RISK_ORDER:
            errors.append(f"risk_assessment.{key}: invalid")
        else:
            levels.append(RISK_ORDER[level])
    overall = risk.get("overall_risk")
    if overall not in RISK_ORDER:
        errors.append("risk_assessment.overall_risk: invalid")
    elif levels and RISK_ORDER[overall] < max(levels):
        errors.append("risk_assessment.overall_risk: cannot be lower than the highest domain risk")
    flags = risk.get("critical_flags")
    if not isinstance(flags, list):
        errors.append("risk_assessment.critical_flags: must be an array")
        flags = []

    decision = data.get("decision")
    if not isinstance(decision, dict):
        errors.append("decision: required object")
        decision = {}
    status = decision.get("decision_status")
    if status != target:
        errors.append("decision.decision_status: must match target_submission_status")
    req_str(decision, "decision_reason", "decision", errors)
    decided_by = req_str(decision, "decided_by", "decision", errors)
    if not is_datetime(decision.get("decided_at")):
        errors.append("decision.decided_at: invalid ISO date-time")
    conditions = decision.get("conditions")
    actions = decision.get("required_actions")
    if not isinstance(conditions, list):
        errors.append("decision.conditions: must be an array")
        conditions = []
    if not isinstance(actions, list):
        errors.append("decision.required_actions: must be an array")
        actions = []

    if status == "VERIFIED":
        for key in ("submission_validator_passed","declarations_complete","product_batch_identifiable","evidence_hashes_present","claim_evidence_links_valid"):
            if intake.get(key) is not True:
                errors.append(f"intake_assessment.{key}: must be true for VERIFIED")
        if intake.get("duplicate_check_status") == "NOT_COMPLETED":
            errors.append("intake_assessment.duplicate_check_status: must be completed for VERIFIED")
        if intake.get("intake_outcome") != "PROCEED":
            errors.append("intake_assessment.intake_outcome: must be PROCEED for VERIFIED")
        if not approver_name:
            errors.append("review_team.final_approver: required for VERIFIED")
        if lead_name and approver_name and lead_name == approver_name:
            errors.append("four-eyes rule: lead reviewer and final approver must differ")
        approver = team.get("final_approver", {}) if isinstance(team, dict) else {}
        if isinstance(approver, dict) and approver.get("conflict_present") is not False:
            errors.append("review_team.final_approver.conflict_present: must be false for VERIFIED")
        if decided_by and approver_name and decided_by != approver_name:
            errors.append("decision.decided_by: must equal final approver for VERIFIED")
        if overall not in {"LOW", "MEDIUM"}:
            errors.append("risk_assessment.overall_risk: VERIFIED requires LOW or MEDIUM")
        if flags:
            errors.append("risk_assessment.critical_flags: must be empty for VERIFIED")
        if not is_date(decision.get("effective_until")):
            errors.append("decision.effective_until: required ISO date for VERIFIED")
        if not any(c.get("decision") == "VERIFIED" for c in claims if isinstance(c, dict)):
            errors.append("claim_reviews: at least one VERIFIED claim required for VERIFIED decision")
        for i, c in enumerate(claims):
            if isinstance(c, dict) and c.get("public_display_approved") is True and c.get("decision") != "VERIFIED":
                errors.append(f"claim_reviews[{i}]: public claim is not VERIFIED")

    if status == "CONDITIONALLY_ACCEPTED":
        if not conditions:
            errors.append("decision.conditions: at least one condition required")
        if not actions:
            errors.append("decision.required_actions: at least one action required")
        if not is_date(decision.get("next_review_date")):
            errors.append("decision.next_review_date: required for conditional acceptance")
        if decision.get("public_passport_eligibility") == "ELIGIBLE":
            errors.append("decision.public_passport_eligibility: conditional acceptance cannot be ELIGIBLE")

    if status in {"CLARIFICATION_REQUIRED", "QUARANTINED", "REJECTED"} and not actions:
        errors.append(f"decision.required_actions: at least one action required for {status}")

    if decision.get("public_passport_eligibility") == "ELIGIBLE" and status != "VERIFIED":
        errors.append("decision.public_passport_eligibility: ELIGIBLE requires VERIFIED")
    if decision.get("marketplace_eligibility") == "ELIGIBLE" and status != "VERIFIED":
        errors.append("decision.marketplace_eligibility: ELIGIBLE requires VERIFIED")
    if decision.get("marketplace_eligibility") == "ELIGIBLE" and risk.get("regulatory_misrepresentation_risk") in {"HIGH", "CRITICAL"}:
        errors.append("decision.marketplace_eligibility: prohibited with high regulatory misrepresentation risk")

    audit = data.get("audit")
    if not isinstance(audit, dict):
        errors.append("audit: required object")
    else:
        if not is_datetime(audit.get("created_at")):
            errors.append("audit.created_at: invalid ISO date-time")
        req_str(audit, "created_by", "audit", errors)
        if audit.get("immutable_record") is not True:
            errors.append("audit.immutable_record: must be true")
        if audit.get("change_requires_superseding_decision") is not True:
            errors.append("audit.change_requires_superseding_decision: must be true")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path, help="Path to review decision JSON")
    args = parser.parse_args()
    try:
        data = json.loads(args.review.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.review}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 2
    errors = validate_review(data)
    if errors:
        print(f"FAIL: {len(errors)} validation error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: review-decision structural and logical controls satisfied")
    print("NOTICE: this result does not authenticate evidence or determine legal, regulatory, medical or marketplace suitability")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
