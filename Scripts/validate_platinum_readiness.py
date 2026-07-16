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

master = rows("Platinum_Readiness_Master.csv")
tiers = rows("Readiness_Tier_Summary.csv")
tier1 = rows("Tier_1_Source_Extraction_Queue.csv")
quarantine = rows("Identity_Quarantine_Register.csv")
heatmap = rows("Evidence_Gap_Heatmap.csv")
metrics = json.loads(
    (audit / "Platinum_Readiness_Metrics.json").read_text(encoding="utf-8")
)

checks = {
    "product_assets": len(master) == 102,
    "pks_assets": sum(row["System"] == "PKS" for row in master) == 90,
    "mps_assets": sum(row["System"] == "MPS" for row in master) == 12,
    "five_tiers": {row["Tier"] for row in tiers}
    == {"T1", "T2", "T3", "T4", "Q"},
    "tier_counts_total": sum(int(row["Asset Count"]) for row in tiers) == 102,
    "tier1_queue_matches": len(tier1)
    == sum(row["Readiness Tier"] == "T1" for row in master),
    "ten_quarantine_assets": len(quarantine) == 10,
    "heatmap_rows": len(heatmap) == 102 * 7,
    "direct_sale_blocked": {row["Direct Sale Gate"] for row in master} == {"BLOCKED"},
    "no_platinum": {row["Platinum Certified"] for row in master} == {"NO"},
    "metrics_consistent": metrics["product_assets_scored"] == 102
    and metrics["direct_sale_gates_opened"] == 0
    and metrics["platinum_certifications"] == 0,
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0035A VALIDATION: PASS")
