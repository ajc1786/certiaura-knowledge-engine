#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"

with (audit / "P1_Closure_Wave_5_Register.csv").open(encoding="utf-8") as file:
    closure = list(csv.DictReader(file))

with (audit / "P1_Passport_Wave_5_Fields.csv").open(encoding="utf-8") as file:
    fields = list(csv.DictReader(file))

evidence_ids = {
    json.loads(path.read_text(encoding="utf-8"))["asset_id"]
    for path in (root / "06_Evidence" / "C11A").glob("*_Evidence.json")
}

nad = json.loads(
    (root / "10_Marketplace" / "C8A" / "CERT-MPS-000005_Product.json").read_text(
        encoding="utf-8"
    )
)
nad_codes = {
    sku["catalogue_code"]
    for sku in nad["catalogue_supplier_skus"]
}

checks = {
    "seven_assets": len(closure) == 7,
    "all_p1": {row["Priority"] for row in closure} == {"P1"},
    "two_new_passports": sum(row["Passport Action"] == "NEW" for row in closure) == 2,
    "five_patched_passports": sum(row["Passport Action"] == "PATCH" for row in closure) == 5,
    "passport_fields_present": len(fields) >= 56,
    "fourteen_evidence_objects": evidence_ids
    == {f"CERT-EKS-{number:06d}" for number in range(283, 297)},
    "all_identity_gates_blocked": {row["Identity Gate"] for row in closure} == {"BLOCKED"},
    "all_quality_gates_blocked": {row["Quality Gate"] for row in closure} == {"BLOCKED"},
    "all_sterility_gates_blocked": {row["Sterility Gate"] for row in closure} == {"BLOCKED"},
    "all_direct_sale_blocked": {row["Direct Sale Gate"] for row in closure} == {"BLOCKED"},
    "nj3100_preserved": "NJ3100" in nad_codes,
    "no_platinum": {row["Platinum Status"] for row in closure} == {"NO"},
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0033A VALIDATION: PASS")
