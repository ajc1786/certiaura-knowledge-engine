#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"

with (audit / "P1_Closure_Wave_7_Register.csv").open(encoding="utf-8") as file:
    closure = list(csv.DictReader(file))

with (audit / "P1_Passport_Wave_7_Fields.csv").open(encoding="utf-8") as file:
    fields = list(csv.DictReader(file))

evidence_ids = {
    json.loads(path.read_text(encoding="utf-8"))["asset_id"]
    for path in (root / "06_Evidence" / "C11C").glob("*_Evidence.json")
}

expected_sequences = {
    "CERT-PKS-000064": "ltlrkepaseiaqsileaysqngwanrrsggkrppprrrqrrkkrg",
    "CERT-PKS-000066": "KE",
    "CERT-PKS-000068": "AEDL",
    "CERT-PKS-000069": "AEDR",
    "CERT-PKS-000070": "AEDP",
    "CERT-PKS-000071": "KEDA",
}

actual_sequences = {
    row["UAI"]: row["Reference Sequence"]
    for row in closure
}

foxo = json.loads(
    (root / "02_Peptides" / "C5A" / "CERT-PKS-000064_Flagship.json").read_text(
        encoding="utf-8"
    )
)

checks = {
    "six_assets": len(closure) == 6,
    "all_p1": {row["Priority"] for row in closure} == {"P1"},
    "six_passports": len({row["Product Passport"] for row in closure}) == 6,
    "passport_fields_present": len(fields) >= 48,
    "twelve_evidence_objects": evidence_ids
    == {f"CERT-EKS-{number:06d}" for number in range(309, 321)},
    "reference_sequences": actual_sequences == expected_sequences,
    "foxo_length": foxo.get("canonical_reference_length") == 46,
    "foxo_all_d": foxo.get("canonical_reference_stereochemistry") == "All D-amino acids",
    "all_supplier_sequence_gates_blocked": {
        row["Supplier Sequence Gate"] for row in closure
    } == {"BLOCKED"},
    "all_terminal_gates_blocked": {
        row["Terminal Chemistry Gate"] for row in closure
    } == {"BLOCKED"},
    "all_human_gates_blocked": {
        row["Human Evidence Gate"] for row in closure
    } == {"BLOCKED"},
    "all_direct_sale_blocked": {
        row["Direct Sale Gate"] for row in closure
    } == {"BLOCKED"},
    "no_platinum": {row["Platinum Status"] for row in closure} == {"NO"},
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0033C VALIDATION: PASS")
