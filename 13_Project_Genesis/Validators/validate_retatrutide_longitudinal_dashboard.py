from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

from build_0047_asset_ownership import BUILD_PROVENANCE, owned_paths

ALLOWED_ACTIONS = {
    "REQUEST_REPEAT_MEASUREMENT",
    "REQUEST_SOURCE_VERIFICATION",
    "CONTACT_DESIGNATED_CLINICIAN",
    "FOLLOW_LOCAL_URGENT_CARE_ROUTE",
    "CORRECT_DATA_WITH_AUDIT_TRAIL",
    "CONTINUE_OBSERVATION_UNDER_PROTOCOL",
    "CLINICIAN_DECISION_REQUIRED",
}
PROHIBITED_TOKENS = {
    "DOSE", "INCREASE", "DECREASE", "START_MEDICINE", "STOP_MEDICINE",
    "DIAGNOSE", "DIAGNOSIS_CONFIRMED", "NO_CLINICAL_REVIEW_NEEDED",
}
DIRECT_IDENTIFIER_KEYS = {
    "patient_name", "full_name", "address", "email", "telephone",
    "phone", "national_identifier", "nhs_number", "date_of_birth",
}


def parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def contains_prohibited(value: object) -> bool:
    text = json.dumps(value, ensure_ascii=True).upper()
    return any(token in text for token in PROHIBITED_TOKENS)


def validate_journey(data: dict) -> list[str]:
    errors: list[str] = []
    for key in ("schema_version", "build_provenance", "journey_id", "subject_reference", "compound", "governance", "observations", "alert_rules"):
        if key not in data:
            errors.append(f"missing required field: {key}")
    if data.get("build_provenance") != BUILD_PROVENANCE:
        errors.append("build_provenance mismatch")
    if data.get("compound") != "retatrutide":
        errors.append("compound must be retatrutide")
    if not re.fullmatch(r"RET-JOURNEY-[A-Z0-9-]+", str(data.get("journey_id", ""))):
        errors.append("invalid journey_id")
    if not re.fullmatch(r"SUBJ-[A-Z0-9-]+", str(data.get("subject_reference", ""))):
        errors.append("invalid subject_reference")
    for key in DIRECT_IDENTIFIER_KEYS:
        if key in data:
            errors.append(f"direct identifier field prohibited: {key}")
    governance = data.get("governance") or {}
    if governance.get("direct_identifiers_present") is not False:
        errors.append("direct_identifiers_present must be false")
    if governance.get("pseudonymised") is not True:
        errors.append("pseudonymised must be true")
    if not governance.get("investigational_status_source_id"):
        errors.append("investigational status source is required")
    try:
        parse_date(governance.get("status_checked_date", ""))
    except Exception:
        errors.append("status_checked_date must be ISO date")

    observations = data.get("observations") or []
    if not observations:
        errors.append("at least one observation is required")
    seen_ids: set[str] = set()
    dates: list[dt.date] = []
    for obs in observations:
        oid = obs.get("observation_id")
        if not oid or oid in seen_ids:
            errors.append("observation identifiers must be unique and non-empty")
        seen_ids.add(oid)
        try:
            dates.append(parse_date(obs.get("observed_date", "")))
        except Exception:
            errors.append(f"invalid observed_date for {oid}")
        if not obs.get("source_type") or not obs.get("source_reference"):
            errors.append(f"source provenance missing for {oid}")
        exp = obs.get("exposure_record")
        if exp and exp.get("recorded_only") is not True:
            errors.append(f"exposure record for {oid} must be recorded_only")
    if dates != sorted(dates):
        errors.append("observations must be ordered by date")

    for rule in data.get("alert_rules") or []:
        for key in ("rule_id", "version", "effective_date", "source_reference", "approved_by", "logic", "severity", "automatic_action"):
            if not rule.get(key):
                errors.append(f"alert rule missing {key}")
        if rule.get("automatic_action") != "CLINICIAN_DECISION_REQUIRED":
            errors.append("automatic_action must be CLINICIAN_DECISION_REQUIRED")
        if contains_prohibited(rule):
            errors.append("alert rule contains prohibited autonomous treatment or diagnosis language")
    return errors


def validate_alert(data: dict) -> list[str]:
    errors: list[str] = []
    for key in ("schema_version", "build_provenance", "alert_id", "journey_id", "rule", "severity", "state", "trigger", "review"):
        if key not in data:
            errors.append(f"missing required field: {key}")
    if data.get("build_provenance") != BUILD_PROVENANCE:
        errors.append("build_provenance mismatch")
    rule = data.get("rule") or {}
    for key in ("rule_id", "version", "source_reference", "approved_by", "effective_date"):
        if not rule.get(key):
            errors.append(f"alert rule provenance missing {key}")
    review = data.get("review") or {}
    actions = review.get("permitted_actions") or []
    for action in actions:
        if action not in ALLOWED_ACTIONS:
            errors.append(f"prohibited or unknown review action: {action}")
    decision = review.get("decision")
    if decision is not None and decision not in ALLOWED_ACTIONS:
        errors.append(f"prohibited or unknown decision: {decision}")
    if contains_prohibited(data):
        errors.append("alert record contains prohibited autonomous treatment or diagnosis language")
    return errors


def validate_export(data: dict) -> list[str]:
    errors: list[str] = []
    for key in ("schema_version", "build_provenance", "export_id", "journey_id", "subject_reference", "status", "summary", "active_alerts", "uncertainties", "provenance", "disclaimer"):
        if key not in data:
            errors.append(f"missing required field: {key}")
    if data.get("build_provenance") != BUILD_PROVENANCE:
        errors.append("build_provenance mismatch")
    for key in DIRECT_IDENTIFIER_KEYS:
        if key in data:
            errors.append(f"direct identifier field prohibited: {key}")
    if contains_prohibited(data):
        errors.append("export contains prohibited autonomous treatment or diagnosis language")
    return errors


def validate_repository(root: Path) -> dict:
    errors: list[str] = []
    checked: list[str] = []
    try:
        exact_paths = owned_paths(root)
    except Exception as exc:
        return {"valid": False, "errors": [f"asset ownership failure: {exc}"], "checked_paths": []}

    expected_examples = {
        "05_Monitoring/Examples/Retatrutide/valid_longitudinal_journey.example.json": (validate_journey, True),
        "05_Monitoring/Examples/Retatrutide/conditional_insufficient_trend.example.json": (validate_journey, True),
        "05_Monitoring/Examples/Retatrutide/invalid_autonomous_treatment.example.json": (validate_journey, False),
        "05_Monitoring/Examples/Retatrutide/valid_alert_review.example.json": (validate_alert, True),
        "05_Monitoring/Examples/Retatrutide/invalid_alert_treatment_action.example.json": (validate_alert, False),
    }
    for rel, (validator, expected_valid) in expected_examples.items():
        if rel not in exact_paths:
            errors.append(f"example path is not exactly owned by manifest: {rel}")
            continue
        path = root / rel
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            item_errors = validator(data)
            actual_valid = not item_errors
            if actual_valid != expected_valid:
                errors.append(f"unexpected validation result for {rel}: {item_errors}")
            checked.append(rel)
        except Exception as exc:
            errors.append(f"failed to validate {rel}: {exc}")

    for rel in exact_paths:
        p = root / rel
        if not p.is_file():
            errors.append(f"manifest-owned path missing: {rel}")
    return {"valid": not errors, "errors": errors, "checked_paths": checked, "owned_path_count": len(exact_paths), "build_provenance": BUILD_PROVENANCE}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = validate_repository(args.repository.resolve())
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
