#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"

with (audit / "Priority_Closure_Current_Register.csv").open(encoding="utf-8") as file:
    current = list(csv.DictReader(file))

with (audit / "Remaining_P1_Closure_Queue.csv").open(encoding="utf-8") as file:
    remaining = list(csv.DictReader(file))

with (audit / "Next_Wave_Build_Plan.csv").open(encoding="utf-8") as file:
    plan = list(csv.DictReader(file))

with (audit / "Closure_Wave_Metrics.csv").open(encoding="utf-8") as file:
    waves = list(csv.DictReader(file))

metrics = json.loads(
    (audit / "Priority_Closure_Programme_Metrics.json").read_text(encoding="utf-8")
)

checks = {
    "priority_assets": len(current) == 51,
    "p0_assets": sum(row["Priority"] == "P0" for row in current) == 13,
    "p1_assets": sum(row["Priority"] == "P1" for row in current) == 38,
    "wave_applied": sum(
        row["Programme Status"].startswith("CLOSURE WAVE APPLIED")
        for row in current
    ) == 25,
    "remaining_queue": len(remaining) == 26,
    "four_next_builds": {row["Recommended Build"] for row in plan}
    == {"0033A", "0033B", "0033C", "0033D"},
    "next_build_asset_total": sum(int(row["Asset Count"]) for row in plan) == 26,
    "wave_evidence_total": sum(int(row["Evidence Objects Added"]) for row in waves) == 50,
    "metrics_p0_complete": metrics["closure_wave_coverage"]["P0_wave_applied"] == 13,
    "metrics_no_platinum": metrics["commercial_and_certification"]["platinum_certifications"] == 0,
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0032 VALIDATION: PASS")
