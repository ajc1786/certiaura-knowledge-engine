#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"

def rows(name):
    with (audit / name).open(encoding="utf-8") as file:
        return list(csv.DictReader(file))

assets = rows("Priority_Asset_Closure_Master.csv")
passports = rows("Priority_Product_Passport_Master.csv")
evidence = rows("Priority_Closure_Evidence_Master.csv")
builds = rows("Closure_Wave_Build_Register.csv")
unresolved = rows("Critical_Unresolved_Identity_Register.csv")
metrics = json.loads(
    (audit / "Priority_Closure_Completion_Metrics.json").read_text(encoding="utf-8")
)

checks = {
    "priority_assets": len(assets) == 51,
    "p0_assets": sum(row["Priority"] == "P0" for row in assets) == 13,
    "p1_assets": sum(row["Priority"] == "P1" for row in assets) == 38,
    "eight_builds": len(builds) == 8,
    "all_green": {row["Repository Validation"] for row in builds}
    == {"GREEN — USER CONFIRMED"},
    "fifty_one_passports": len({row["Product Passport"] for row in passports}) == 51,
    "one_hundred_two_evidence": len({row["Evidence UAI"] for row in evidence}) == 102,
    "direct_sale_blocked": {row["Direct Sale Gate"] for row in assets} == {"BLOCKED"},
    "no_platinum": {row["Platinum Status"] for row in assets} == {"NO"},
    "ten_unresolved": len(unresolved) == 10,
    "metrics_consistent": metrics["programme_scope"]["P0_assets"] == 13
    and metrics["programme_scope"]["P1_assets"] == 38
    and metrics["closure_objects"]["product_passports"] == 51
    and metrics["closure_objects"]["closure_evidence_objects"] == 102,
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0034 VALIDATION: PASS")
