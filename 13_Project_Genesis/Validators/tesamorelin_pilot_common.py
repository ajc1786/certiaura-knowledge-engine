from __future__ import annotations

import json
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def nonempty_list(value):
    return isinstance(value, list) and len(value) > 0


def text_contains_any(text, terms):
    value = str(text).lower()
    return any(term.lower() in value for term in terms)


def validate_record(record):
    errors = []
    record_type = record.get("record_type")
    if record.get("build_number") != "0056":
        errors.append("build_number must be 0056")
    if record.get("peptide") != "Tesamorelin":
        errors.append("peptide must be Tesamorelin")
    if record.get("clinical_equivalence_claimed") is not False:
        errors.append("clinical equivalence is prohibited")
    if record.get("clinical_decision_support_authorised") is not False:
        errors.append("clinical decision support is not authorised")

    if record_type == "tesamorelin_evidence_corpus_map":
        if not nonempty_list(record.get("scope")):
            errors.append("evidence scope is required")
        if not nonempty_list(record.get("source_records")):
            errors.append("evidence source records are required")
        if record.get("decision") == "ACCEPT_FOR_BOUNDARY_DEFINITION":
            if record.get("coverage_state") != "BASELINE_MAPPED":
                errors.append("accepted evidence map must be baseline mapped")
            if record.get("open_critical_gaps"):
                errors.append("accepted evidence map cannot have critical gaps")
            if not nonempty_list(record.get("approvers")):
                errors.append("accepted evidence map requires human approval")

    elif record_type == "tesamorelin_biological_boundary":
        if not str(record.get("mechanism_summary", "")).strip():
            errors.append("mechanism summary is required")
        if not nonempty_list(record.get("known_contexts")):
            errors.append("known contexts are required")
        if not nonempty_list(record.get("excluded_claims")):
            errors.append("excluded claims are required")
        if not nonempty_list(record.get("uncertainties")):
            errors.append("uncertainties are required")
        prohibited = ["guarantee", "reverses ageing", "cures", "equivalent to retatrutide"]
        if text_contains_any(record.get("mechanism_summary", ""), prohibited):
            errors.append("biological boundary contains prohibited overclaim")
        if record.get("decision") == "ACCEPT_BIOLOGICAL_BOUNDARY":
            if record.get("boundary_state") != "DEFINED":
                errors.append("accepted biological boundary must be defined")
            if not nonempty_list(record.get("approvers")):
                errors.append("accepted biological boundary requires human approval")

    elif record_type == "tesamorelin_safety_boundary":
        for key, label in [
            ("contraindication_categories", "contraindication categories"),
            ("caution_categories", "caution categories"),
            ("monitoring_dependencies", "monitoring dependencies"),
            ("stop_or_escalate_triggers", "stop or escalate triggers"),
        ]:
            if not nonempty_list(record.get(key)):
                errors.append(f"{label} are required")
        if not str(record.get("emergency_instruction", "")).strip():
            errors.append("emergency instruction is required")
        if record.get("decision") == "ACCEPT_SAFETY_BOUNDARY_FOR_KNOWLEDGE_PILOT":
            if record.get("boundary_state") != "DEFINED":
                errors.append("accepted safety boundary must be defined")
            if not nonempty_list(record.get("approvers")):
                errors.append("accepted safety boundary requires human approval")

    elif record_type == "tesamorelin_monitoring_model":
        if not nonempty_list(record.get("baseline_domains")):
            errors.append("baseline monitoring domains are required")
        if not nonempty_list(record.get("ongoing_domains")):
            errors.append("ongoing monitoring domains are required")
        if not nonempty_list(record.get("decision_rules")):
            errors.append("monitoring decision rules are required")
        actions = {str(item.get("action")) for item in record.get("decision_rules", []) if isinstance(item, dict)}
        if "STOP_AND_ESCALATE" not in actions:
            errors.append("monitoring model requires a stop-and-escalate rule")
        automation_limit = str(record.get("automation_limit", "")).lower()
        if not automation_limit or "no autonomous" not in automation_limit:
            errors.append("monitoring model must prohibit autonomous clinical decisions")
        if record.get("decision") == "ACCEPT_MONITORING_MODEL_FOR_CONTROLLED_PILOT":
            if record.get("model_state") != "DEFINED":
                errors.append("accepted monitoring model must be defined")
            if not nonempty_list(record.get("approvers")):
                errors.append("accepted monitoring model requires human approval")

    elif record_type == "tesamorelin_controlled_pilot_acceptance":
        if not nonempty_list(record.get("pilot_scope")):
            errors.append("pilot scope is required")
        if not nonempty_list(record.get("prohibited_scope")):
            errors.append("prohibited pilot scope is required")
        if record.get("decision") == "ACCEPT_CONTROLLED_KNOWLEDGE_PILOT":
            required_states = {
                "evidence_corpus_state": "BASELINE_MAPPED",
                "biological_boundary_state": "DEFINED",
                "safety_boundary_state": "DEFINED",
                "monitoring_model_state": "DEFINED",
            }
            for key, expected in required_states.items():
                if record.get(key) != expected:
                    errors.append(f"accepted pilot requires {key}={expected}")
            if record.get("open_critical_gaps"):
                errors.append("accepted pilot cannot have critical gaps")
            if not nonempty_list(record.get("approvers")):
                errors.append("accepted pilot requires human approval")
            prohibited_text = " ".join(map(str, record.get("prohibited_scope", []))).lower()
            for required in ["clinical recommendation", "dosing", "diagnosis", "prescribing"]:
                if required not in prohibited_text:
                    errors.append(f"accepted pilot prohibited scope must include {required}")

    elif record_type == "tesamorelin_evidence_gap_decision":
        if not record.get("gap_id"):
            errors.append("gap id is required")
        if not record.get("gap_category"):
            errors.append("gap category is required")
        if not str(record.get("required_action", "")).strip():
            errors.append("required action is required")
        if not str(record.get("closure_authority", "")).strip() or str(record.get("closure_authority", "")).lower() == "system":
            errors.append("human closure authority is required")
        if record.get("decision") == "CLOSE_WITH_EVIDENCE":
            if not nonempty_list(record.get("evidence")):
                errors.append("gap closure requires evidence")
            if not nonempty_list(record.get("approvers")):
                errors.append("gap closure requires human approval")
        if record.get("severity") == "CRITICAL" and record.get("status") == "CLOSED_EVIDENCED" and not nonempty_list(record.get("evidence")):
            errors.append("critical gap cannot close without evidence")
    else:
        errors.append("unsupported record_type")
    return errors


def validate_bundle(records):
    errors = []
    by_type = {record.get("record_type"): record for record in records}
    required_types = {
        "tesamorelin_evidence_corpus_map",
        "tesamorelin_biological_boundary",
        "tesamorelin_safety_boundary",
        "tesamorelin_monitoring_model",
        "tesamorelin_controlled_pilot_acceptance",
        "tesamorelin_evidence_gap_decision",
    }
    for missing in sorted(required_types - set(by_type)):
        errors.append(f"bundle missing {missing}")
    for record in records:
        errors.extend(validate_record(record))

    acceptance = by_type.get("tesamorelin_controlled_pilot_acceptance", {})
    evidence = by_type.get("tesamorelin_evidence_corpus_map", {})
    biological = by_type.get("tesamorelin_biological_boundary", {})
    safety = by_type.get("tesamorelin_safety_boundary", {})
    monitoring = by_type.get("tesamorelin_monitoring_model", {})
    if acceptance.get("decision") == "ACCEPT_CONTROLLED_KNOWLEDGE_PILOT":
        if evidence.get("decision") != "ACCEPT_FOR_BOUNDARY_DEFINITION":
            errors.append("accepted pilot requires accepted evidence corpus")
        if biological.get("decision") != "ACCEPT_BIOLOGICAL_BOUNDARY":
            errors.append("accepted pilot requires accepted biological boundary")
        if safety.get("decision") != "ACCEPT_SAFETY_BOUNDARY_FOR_KNOWLEDGE_PILOT":
            errors.append("accepted pilot requires accepted safety boundary")
        if monitoring.get("decision") != "ACCEPT_MONITORING_MODEL_FOR_CONTROLLED_PILOT":
            errors.append("accepted pilot requires accepted monitoring model")
    return errors
