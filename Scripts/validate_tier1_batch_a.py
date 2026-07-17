#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]

def rows(path):
    with (root / path).open(encoding="utf-8") as file:
        return list(csv.DictReader(file))

closure = rows("Documentation/Audit/Tier1_Batch_A_Source_Closure_Register.csv")
evidence = rows("Documentation/Audit/Tier1_Batch_A_Evidence_Register.csv")
gaps = rows("Documentation/Audit/Tier1_Batch_A_Platinum_Gap_Register.csv")

passport_ids = {row["Product Passport"] for row in closure}
evidence_ids = {row["EKS UAI"] for row in evidence}

checks = {
    "seven_assets": len(closure) == 7,
    "seven_passports": passport_ids
    == {f"CERT-PPS-{number:06d}" for number in range(52, 59)},
    "twenty_one_evidence": len(evidence) == 21,
    "contiguous_evidence": evidence_ids
    == {f"CERT-EKS-{number:06d}" for number in range(335, 356)},
    "three_evidence_per_asset": all(
        sum(row["Parent UAI"] == asset["UAI"] for row in evidence) == 3
        for asset in closure
    ),
    "defined_scope_closed": {
        row["Defined Scope Closed"] for row in evidence
    } == {"YES"},
    "not_exhaustive": {row["Exhaustive Review"] for row in evidence} == {"NO"},
    "living_evidence_active": {row["Living Evidence"] for row in evidence} == {"ACTIVE"},
    "direct_sale_blocked": {row["Direct Sale Gate"] for row in closure} == {"BLOCKED"},
    "no_platinum": {row["Platinum Certified"] for row in closure} == {"NO"},
    "passport_gaps_present": len(gaps) == 56,
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0035B VALIDATION: PASS")
