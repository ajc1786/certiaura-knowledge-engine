#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"

with (audit / "P1_Closure_Wave_6_Register.csv").open(encoding="utf-8") as file:
    closure = list(csv.DictReader(file))

with (audit / "P1_Passport_Wave_6_Fields.csv").open(encoding="utf-8") as file:
    fields = list(csv.DictReader(file))

evidence_ids = {
    json.loads(path.read_text(encoding="utf-8"))["asset_id"]
    for path in (root / "06_Evidence" / "C11B").glob("*_Evidence.json")
}

humanin = json.loads(
    (root / "02_Peptides" / "C5A" / "CERT-PKS-000063_Flagship.json").read_text(
        encoding="utf-8"
    )
)

checks = {
    "six_assets": len(closure) == 6,
    "all_p1": {row["Priority"] for row in closure} == {"P1"},
    "six_passports": len({row["Product Passport"] for row in closure}) == 6,
    "passport_fields_present": len(fields) >= 48,
    "twelve_evidence_objects": evidence_ids
    == {f"CERT-EKS-{number:06d}" for number in range(297, 309)},
    "all_identity_gates_blocked": {row["Identity Gate"] for row in closure} == {"BLOCKED"},
    "all_source_gates_blocked": {row["Source / Composition Gate"] for row in closure} == {"BLOCKED"},
    "all_potency_gates_blocked": {row["Potency Gate"] for row in closure} == {"BLOCKED"},
    "all_sterility_gates_blocked": {row["Sterility Gate"] for row in closure} == {"BLOCKED"},
    "all_direct_sale_blocked": {row["Direct Sale Gate"] for row in closure} == {"BLOCKED"},
    "humanin_sequence": humanin.get("canonical_reference_sequence")
    == "MAPRGFSCLLLLTSEIDLPVKRRA",
    "humanin_length": humanin.get("canonical_reference_length") == 24,
    "humanin_supplier_unverified": humanin.get("supplier_sequence_verified") is False,
    "no_platinum": {row["Platinum Status"] for row in closure} == {"NO"},
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0033B VALIDATION: PASS")
