#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"
status = json.loads(
    (audit / "Catalogue_Coverage_Status_After_0030A.json").read_text(encoding="utf-8")
)

with (audit / "Catalogue_Coverage_Correction_0030A.csv").open(
    encoding="utf-8"
) as file:
    rows = list(csv.DictReader(file))

checks = {
    "three_gap_rows_closed": len(rows) == 3,
    "source_codes": {row["Build 0029 Gap Code"] for row in rows}
    == {"2S10", "2S50", "GP"},
    "ss31_mapping": {
        row["Final UAI"]
        for row in rows
        if row["Build 0029 Gap Code"] in {"2S10", "2S50"}
    } == {"CERT-PKS-000089"},
    "glp1_mapping": {
        row["Final UAI"]
        for row in rows
        if row["Build 0029 Gap Code"] == "GP"
    } == {"CERT-PKS-000090"},
    "sku_coverage": status["mapped_sku_rows"] == 196
    and status["unmapped_sku_rows"] == 0,
    "family_coverage": status["mapped_preliminary_families"] == 104
    and status["unmapped_preliminary_families"] == 0,
    "glp1_identity_block_retained": status["remaining_identity_block"][
        "scientific_identity_gap"
    ] is True,
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0030A VALIDATION: PASS")
