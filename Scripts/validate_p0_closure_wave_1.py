#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"

with (audit / "P0_Closure_Wave_1_Register.csv").open(encoding="utf-8") as file:
    closure = list(csv.DictReader(file))

with (audit / "P0_Product_Passport_Field_Register.csv").open(encoding="utf-8") as file:
    fields = list(csv.DictReader(file))

evidence_files = list((root / "06_Evidence" / "C10A").glob("*_Evidence.json"))
evidence_ids = {
    json.loads(path.read_text(encoding="utf-8"))["asset_id"]
    for path in evidence_files
}

checks = {
    "six_assets": len(closure) == 6,
    "all_p0": {row["Priority"] for row in closure} == {"P0"},
    "all_blocked": {row["Direct Sale Gate"] for row in closure} == {"BLOCKED"},
    "passport_fields_present": len(fields) >= 48,
    "twelve_evidence_objects": evidence_ids
    == {f"CERT-EKS-{number:06d}" for number in range(233, 245)},
    "new_passports": {
        "CERT-PPS-000013",
        "CERT-PPS-000014",
        "CERT-PPS-000015",
    }.issubset({row["Product Passport"] for row in closure}),
    "no_platinum": {row["Platinum Status"] for row in closure} == {"NO"},
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0031A VALIDATION: PASS")
