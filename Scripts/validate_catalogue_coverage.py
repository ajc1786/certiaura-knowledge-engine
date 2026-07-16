#!/usr/bin/env python3
"""Validate the committed Build 0029 audit outputs."""

from pathlib import Path
import json
import pandas as pd
import sys

root = Path(__file__).resolve().parents[1]
audit = root / "Documentation" / "Audit"

crosswalk = pd.read_csv(audit / "Catalogue_Final_SKU_Crosswalk.csv")
families = pd.read_csv(audit / "Catalogue_Family_Reconciliation.csv")
metrics = json.loads((audit / "Catalogue_Audit_Metrics.json").read_text(encoding="utf-8"))
uai = pd.read_csv(audit / "UAI_Continuity_Audit.csv")

checks = {
    "source_rows": len(crosswalk) == 196,
    "mapped_rows": (crosswalk["Disposition"] != "UNMAPPED - COVERAGE GAP").sum() == 193,
    "unmapped_codes": set(
        crosswalk.loc[
            crosswalk["Disposition"] == "UNMAPPED - COVERAGE GAP",
            "Source Code",
        ].astype(str)
    ) == {"2S10", "2S50", "GP"},
    "source_families": len(families) == 104,
    "mapped_families": (families["Disposition"] != "UNMAPPED - COVERAGE GAP").sum() == 102,
    "metrics_product_assets": metrics["final_product_assets"] == 100,
    "metrics_pks": metrics["pks_assets"] == 88,
    "metrics_mps": metrics["mps_assets"] == 12,
    "uai_continuity": set(uai["Continuity Status"]) == {"PASS - CONTIGUOUS RANGE"},
}

for name, result in checks.items():
    print(f"{name}: {'PASS' if result else 'FAIL'}")

if not all(checks.values()):
    sys.exit(1)

print("BUILD 0029 AUDIT VALIDATION: PASS")
