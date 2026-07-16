#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"

with (audit / "P1_Closure_Wave_8_Register.csv").open(encoding="utf-8") as file:
    closure = list(csv.DictReader(file))

with (audit / "P1_Passport_Wave_8_Fields.csv").open(encoding="utf-8") as file:
    fields = list(csv.DictReader(file))

evidence_ids = {
    json.loads(path.read_text(encoding="utf-8"))["asset_id"]
    for path in (root / "06_Evidence" / "C11D").glob("*_Evidence.json")
}

expected_reference = {
    "CERT-PKS-000072": "KEDW",
    "CERT-PKS-000073": "KEDP",
    "CERT-PKS-000074": "AED",
    "CERT-PKS-000075": "EDG",
    "CERT-PKS-000076": "UNRESOLVED: EDP / PQN conflict",
    "CERT-PKS-000077": "UNRESOLVED: commonly claimed EDL; conflicting/unverified",
    "CERT-PKS-000078": "KED",
}

actual_reference = {
    row["UAI"]: row["Reference Identity"]
    for row in closure
}

crystagen = json.loads(
    (root / "02_Peptides" / "C5B" / "CERT-PKS-000076_Flagship.json").read_text(
        encoding="utf-8"
    )
)
ovagen = json.loads(
    (root / "02_Peptides" / "C5B" / "CERT-PKS-000077_Flagship.json").read_text(
        encoding="utf-8"
    )
)

checks = {
    "seven_assets": len(closure) == 7,
    "all_p1": {row["Priority"] for row in closure} == {"P1"},
    "seven_passports": len({row["Product Passport"] for row in closure}) == 7,
    "passport_fields_present": len(fields) >= 56,
    "fourteen_evidence_objects": evidence_ids
    == {f"CERT-EKS-{number:06d}" for number in range(321, 335)},
    "controlled_reference_identities": actual_reference == expected_reference,
    "crystagen_quarantined": crystagen.get("identity_quarantine") is True
    and crystagen.get("canonical_identity_allocated") is False,
    "ovagen_quarantined": ovagen.get("identity_quarantine") is True
    and ovagen.get("canonical_identity_allocated") is False,
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

print("BUILD 0033D VALIDATION: PASS")
