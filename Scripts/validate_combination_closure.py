#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"

with (audit / "P1_Combination_Closure_Register.csv").open(encoding="utf-8") as file:
    closure = list(csv.DictReader(file))

with (audit / "P1_Combination_Passport_Fields.csv").open(encoding="utf-8") as file:
    fields = list(csv.DictReader(file))

evidence_ids = {
    json.loads(path.read_text(encoding="utf-8"))["asset_id"]
    for path in (root / "06_Evidence" / "C10D").glob("*_Evidence.json")
}

checks = {
    "seven_assets": len(closure) == 7,
    "all_p1": {row["Priority"] for row in closure} == {"P1"},
    "seven_passports": len({row["Product Passport"] for row in closure}) == 7,
    "passport_fields_present": len(fields) >= 56,
    "fourteen_evidence_objects": evidence_ids
    == {f"CERT-EKS-{number:06d}" for number in range(269, 283)},
    "identity_gates_blocked": {row["Component Identity Gate"] for row in closure} == {"BLOCKED"},
    "ratio_gates_blocked": {row["Ratio Gate"] for row in closure} == {"BLOCKED"},
    "compatibility_gates_blocked": {row["Compatibility Gate"] for row in closure} == {"BLOCKED"},
    "direct_sale_blocked": {row["Direct Sale Gate"] for row in closure} == {"BLOCKED"},
    "no_platinum": {row["Platinum Status"] for row in closure} == {"NO"},
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0031D VALIDATION: PASS")
