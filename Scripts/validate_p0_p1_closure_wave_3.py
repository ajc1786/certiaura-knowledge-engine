#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"

with (audit / "P0_P1_Closure_Wave_3_Register.csv").open(encoding="utf-8") as file:
    closure = list(csv.DictReader(file))

with (audit / "P0_P1_Passport_Wave_3.csv").open(encoding="utf-8") as file:
    fields = list(csv.DictReader(file))

evidence_ids = {
    json.loads(path.read_text(encoding="utf-8"))["asset_id"]
    for path in (root / "06_Evidence" / "C10C").glob("*_Evidence.json")
}

pe = json.loads(
    (root / "02_Peptides" / "C3A" / "CERT-PKS-000043_Flagship.json").read_text(
        encoding="utf-8"
    )
)
derm = json.loads(
    (root / "02_Peptides" / "C3B" / "CERT-PKS-000046_Flagship.json").read_text(
        encoding="utf-8"
    )
)

checks = {
    "six_assets": len(closure) == 6,
    "priority_mix": {row["Priority"] for row in closure} == {"P0", "P1"},
    "all_blocked": {row["Direct Sale Gate"] for row in closure} == {"BLOCKED"},
    "six_passports": len({row["Product Passport"] for row in closure}) == 6,
    "passport_fields_present": len(fields) >= 48,
    "twelve_evidence_objects": evidence_ids
    == {f"CERT-EKS-{number:06d}" for number in range(257, 269)},
    "pe_sequence": pe.get("canonical_reference_sequence")
    == "Gly-Val-Ser-Trp-Gly-Leu-Arg (GVSWGLR)",
    "pe_supplier_unverified": pe.get("supplier_sequence_verified") is False,
    "dermorphin_sequence": derm.get("canonical_literature_sequence")
    == "H-Tyr-D-Ala-Phe-Gly-Tyr-Pro-Ser-NH2",
    "no_platinum": {row["Platinum Status"] for row in closure} == {"NO"},
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0031C VALIDATION: PASS")
