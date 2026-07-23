from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

BUILD_NUMBER = "0053"
PEPTIDE_UAI = "CERT-PKS-000001"

RECORD_TYPES = {
    "RETATRUTIDE_KNOWLEDGE_CHANGE_PROPOSAL",
    "RETATRUTIDE_CROSS_ASSET_IMPACT_ASSESSMENT",
    "RETATRUTIDE_CONTROLLED_CHANGE_APPROVAL",
    "RETATRUTIDE_CHANGE_IMPLEMENTATION_PACKAGE",
    "RETATRUTIDE_PUBLICATION_RELEASE",
    "RETATRUTIDE_POST_CHANGE_EFFECTIVENESS_REVIEW",
    "RETATRUTIDE_CHANGE_REOPENING_DECISION",
}


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalise_path(value: str) -> str:
    return value.strip().replace("\\", "/")


def require(data: dict[str, Any], names: list[str], errors: list[str]) -> None:
    for name in names:
        if name not in data:
            errors.append(f"missing required field: {name}")


def common_errors(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(data, ["schema_version", "record_type", "build_number", "created_at", "created_by", "peptide_uai"], errors)
    if data.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if data.get("build_number") != BUILD_NUMBER:
        errors.append("build_number must be 0053")
    if data.get("peptide_uai") != PEPTIDE_UAI:
        errors.append("peptide_uai must be CERT-PKS-000001")
    if data.get("record_type") not in RECORD_TYPES:
        errors.append("unsupported record_type")
    return errors


def validate_record(data: dict[str, Any]) -> list[str]:
    errors = common_errors(data)
    record_type = data.get("record_type")
    if record_type == "RETATRUTIDE_KNOWLEDGE_CHANGE_PROPOSAL":
        require(data, ["change_id", "originating_governance_decision_id", "originating_decision_state", "change_classification", "evidence_basis", "proposed_changes", "human_scientific_approval_required", "autonomous_action", "status"], errors)
        if data.get("autonomous_action") is not False:
            errors.append("autonomous_action must be false")
        if data.get("human_scientific_approval_required") is not True:
            errors.append("human_scientific_approval_required must be true")
        if data.get("originating_decision_state") not in {"APPROVED_FOR_KNOWLEDGE_CHANGE", "NO_CHANGE_WATCH"}:
            errors.append("originating decision state is not authorised")
        changes = data.get("proposed_changes")
        if not isinstance(changes, list) or not changes:
            errors.append("proposed_changes must be a non-empty array")
        if data.get("change_classification") != "NO_CHANGE_WATCH" and not data.get("evidence_basis"):
            errors.append("an actionable change requires evidence_basis")
    elif record_type == "RETATRUTIDE_CROSS_ASSET_IMPACT_ASSESSMENT":
        require(data, ["impact_id", "change_id", "impacted_assets", "unresolved_assets", "all_declared", "relationship_changes", "status"], errors)
        if data.get("status") == "COMPLETE":
            if data.get("all_declared") is not True:
                errors.append("complete impact assessment requires all_declared=true")
            if data.get("unresolved_assets"):
                errors.append("complete impact assessment cannot contain unresolved_assets")
        seen: set[str] = set()
        for asset in data.get("impacted_assets", []):
            path = normalise_path(str(asset.get("repository_path", "")))
            if not path:
                errors.append("impacted asset repository_path is required")
            if path.lower() in seen:
                errors.append(f"duplicate impacted asset path: {path}")
            seen.add(path.lower())
    elif record_type == "RETATRUTIDE_CONTROLLED_CHANGE_APPROVAL":
        require(data, ["approval_id", "change_id", "impact_id", "reviewers", "outcome", "conditions", "human_approval", "effective_date", "status"], errors)
        if data.get("human_approval") is not True:
            errors.append("human_approval must be true")
        roles = {item.get("role") for item in data.get("reviewers", [])}
        if data.get("outcome") == "APPROVED" and not {"SCIENTIFIC_REVIEWER", "GOVERNANCE_APPROVER"}.issubset(roles):
            errors.append("approved change requires scientific and governance reviewers")
        if data.get("outcome") == "APPROVED" and any(item.get("decision") != "APPROVE" for item in data.get("reviewers", [])):
            errors.append("approved outcome cannot contain a non-approve reviewer decision")
    elif record_type == "RETATRUTIDE_CHANGE_IMPLEMENTATION_PACKAGE":
        require(data, ["implementation_id", "change_id", "approval_id", "approval_outcome", "expected_targets", "applied_targets", "propagation_complete", "before_after_changes", "rollback_plan", "status"], errors)
        expected = {normalise_path(str(x)) for x in data.get("expected_targets", [])}
        applied = {normalise_path(str(x)) for x in data.get("applied_targets", [])}
        if data.get("approval_outcome") != "APPROVED":
            errors.append("implementation requires approval_outcome=APPROVED")
        if data.get("propagation_complete") is True and expected != applied:
            errors.append("propagation_complete requires applied_targets to equal expected_targets")
        if data.get("status") == "IMPLEMENTED" and data.get("propagation_complete") is not True:
            errors.append("implemented change requires propagation_complete=true")
        plan = data.get("rollback_plan") or {}
        if not plan.get("trigger_conditions") or not plan.get("restore_checkpoint") or not plan.get("owner"):
            errors.append("complete rollback_plan is required")
    elif record_type == "RETATRUTIDE_PUBLICATION_RELEASE":
        require(data, ["release_id", "implementation_id", "approval_state", "implementation_state", "publication_state", "audience_channels", "published_assets", "publication_approval_id", "effective_at", "responsible_communications_validated"], errors)
        if data.get("publication_state") == "PUBLISHED":
            if data.get("approval_state") != "APPROVED":
                errors.append("published release requires approval_state=APPROVED")
            if data.get("implementation_state") != "IMPLEMENTED":
                errors.append("published release requires implementation_state=IMPLEMENTED")
            if data.get("responsible_communications_validated") is not True:
                errors.append("published release requires responsible communications validation")
            if not data.get("effective_at"):
                errors.append("published release requires effective_at")
    elif record_type == "RETATRUTIDE_POST_CHANGE_EFFECTIVENESS_REVIEW":
        require(data, ["review_id", "implementation_id", "measures", "evidence_complete", "outcome", "next_action", "reviewed_at", "reviewer_id"], errors)
        measures = data.get("measures", [])
        if not measures:
            errors.append("at least one effectiveness measure is required")
        if data.get("outcome") != "INSUFFICIENT_EVIDENCE":
            if data.get("evidence_complete") is not True:
                errors.append("determinate effectiveness outcome requires evidence_complete=true")
            for measure in measures:
                if not str(measure.get("evidence_ref", "")).strip():
                    errors.append("each determinate effectiveness measure requires evidence_ref")
        if data.get("outcome") == "EFFECTIVE" and any(item.get("met") is not True for item in measures):
            errors.append("effective outcome requires every mandatory measure to be met")
    elif record_type == "RETATRUTIDE_CHANGE_REOPENING_DECISION":
        require(data, ["reopening_id", "review_id", "trigger", "decision", "rationale", "human_approval", "approver_id", "decided_at", "new_change_id"], errors)
        if data.get("human_approval") is not True:
            errors.append("reopening decision requires human_approval=true")
        if data.get("decision") == "REOPEN" and not data.get("new_change_id"):
            errors.append("REOPEN decision requires new_change_id")
        if len(str(data.get("rationale", ""))) < 10:
            errors.append("reopening rationale is too short")
    return errors


def validate_bundle(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    by_type = {record.get("record_type"): record for record in records}
    for record in records:
        errors.extend([f"{record.get('record_type')}: {item}" for item in validate_record(record)])
    proposal = by_type.get("RETATRUTIDE_KNOWLEDGE_CHANGE_PROPOSAL")
    impact = by_type.get("RETATRUTIDE_CROSS_ASSET_IMPACT_ASSESSMENT")
    approval = by_type.get("RETATRUTIDE_CONTROLLED_CHANGE_APPROVAL")
    implementation = by_type.get("RETATRUTIDE_CHANGE_IMPLEMENTATION_PACKAGE")
    publication = by_type.get("RETATRUTIDE_PUBLICATION_RELEASE")
    effectiveness = by_type.get("RETATRUTIDE_POST_CHANGE_EFFECTIVENESS_REVIEW")
    if proposal and impact and impact.get("change_id") != proposal.get("change_id"):
        errors.append("impact change_id does not match proposal")
    if approval and impact and approval.get("impact_id") != impact.get("impact_id"):
        errors.append("approval impact_id does not match impact assessment")
    if implementation and approval and implementation.get("approval_id") != approval.get("approval_id"):
        errors.append("implementation approval_id does not match approval")
    if publication and implementation and publication.get("implementation_id") != implementation.get("implementation_id"):
        errors.append("publication implementation_id does not match implementation")
    if effectiveness and implementation and effectiveness.get("implementation_id") != implementation.get("implementation_id"):
        errors.append("effectiveness implementation_id does not match implementation")
    return errors
