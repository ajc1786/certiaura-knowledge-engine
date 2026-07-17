#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]

def rows(path):
    with (root / path).open(encoding="utf-8") as file:
        return list(csv.DictReader(file))

crosswalk = rows("Documentation/Audit/Asset_Submission_Class_Crosswalk.csv")
classes = rows("Documentation/Audit/Submission_Class_Summary.csv")
acceptance = rows("Documentation/Audit/Evidence_Acceptance_Criteria.csv")
expiry = rows("Documentation/Audit/Evidence_Expiry_and_Review_Rules.csv")
rejection = rows("Documentation/Audit/Rejection_and_Quarantine_Rules.csv")

submission_schema = json.loads(
    (root / "Schemas" / "Supplier_Evidence_Submission.schema.json").read_text(encoding="utf-8")
)
decision_schema = json.loads(
    (root / "Schemas" / "Product_Passport_Field_Decision.schema.json").read_text(encoding="utf-8")
)

quarantine_uais = {
    "CERT-PKS-000042",
    "CERT-PKS-000048",
    "CERT-PKS-000076",
    "CERT-PKS-000077",
    "CERT-PKS-000090",
    "CERT-MPS-000006",
    "CERT-MPS-000008",
    "CERT-MPS-000009",
    "CERT-MPS-000012",
    "CERT-PKS-000045",
}

checks = {
    "product_assets": len(crosswalk) == 102,
    "pks_assets": sum(row["System"] == "PKS" for row in crosswalk) == 90,
    "mps_assets": sum(row["System"] == "MPS" for row in crosswalk) == 12,
    "nine_classes": len(classes) == 9,
    "class_counts_total": sum(int(row["Asset Count"]) for row in classes) == 102,
    "all_classes_valid": {row["Submission Class"] for row in crosswalk}
    == {row["Submission Class"] for row in classes},
    "all_have_parenteral_overlay": all(
        "OV01_PARENTERAL_RISK" in row["Required Overlays"]
        for row in crosswalk
    ),
    "ten_quarantine_assets": {
        row["UAI"] for row in crosswalk if row["Submission Class"] == "SC09"
    } == quarantine_uais,
    "acceptance_matrix": len(acceptance) >= 8,
    "expiry_matrix": len(expiry) >= 10,
    "rejection_rules": len(rejection) >= 9,
    "submission_schema": submission_schema["title"]
    == "CertiAura Supplier Evidence Submission",
    "decision_schema": decision_schema["title"]
    == "CertiAura Product Passport Field Decision",
    "direct_sale_blocked": {row["Direct Sale Gate"] for row in crosswalk}
    == {"BLOCKED"},
    "no_platinum": {row["Platinum Certified"] for row in crosswalk} == {"NO"},
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0035D VALIDATION: PASS")
