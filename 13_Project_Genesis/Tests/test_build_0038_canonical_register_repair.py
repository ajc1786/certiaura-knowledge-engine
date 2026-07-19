from __future__ import annotations
import csv, json, shutil, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve()
IMPORT_DIR = HERE.parents[1] / "Import"
if str(IMPORT_DIR) not in sys.path:
    sys.path.insert(0, str(IMPORT_DIR))
from asset_register_reconciler import CANONICAL_REGISTER_RELATIVE_PATH, UAI_RE, load_register
from repair_master_asset_register import run, verify

class CanonicalRegisterRepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        register = self.repo / CANONICAL_REGISTER_RELATIVE_PATH
        register.parent.mkdir(parents=True)
        with register.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["Universal Asset Identifier","Asset Name","Knowledge System","Asset Type","Status","Owner","Parent Assets","Last Review","Notes"])
            writer.writerow(["NO NEW UAI","Build 0035D Supplier Evidence & Product Passport Standard","SYSTEM","Governance and Submission Standard","COMPLETE","Aidan Coleman","","17/07/2026","No permanent UAI allocated."])
        (self.repo/"00_Governance").mkdir(parents=True)
        (self.repo/"00_Governance"/"RULE.md").write_text("# Rule\n", encoding="utf-8")
        for i in range(12):
            p=self.repo/"08_Product_Passports"/"Standards"/f"STANDARD_{i:02d}.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"# Standard {i}\n", encoding="utf-8")
        records=self.repo/"Documentation"/"Build_Records"/"0038"
        records.mkdir(parents=True)
        (records/"ASSET_INTENT_MANIFEST.json").write_text(json.dumps({"build_number":"0038","formal_assets":[]}), encoding="utf-8")
        (records/"HISTORICAL_ASSET_BACKFILL_POLICY.json").write_text(json.dumps({}), encoding="utf-8")
    def tearDown(self): self.tmp.cleanup()
    def test_exact_legacy_shape_is_repaired(self):
        result=run(self.repo, True, False)
        self.assertTrue(result.get("applied"), result)
        report=verify(self.repo)
        self.assertTrue(report["valid"], report)
        rows,_=load_register(self.repo/CANONICAL_REGISTER_RELATIVE_PATH)
        self.assertGreaterEqual(len(rows),10)
        self.assertFalse(any("NO NEW UAI" in r["Universal Asset Identifier"] for r in rows))
        self.assertTrue(all(UAI_RE.fullmatch(r["Universal Asset Identifier"]) for r in rows))
        self.assertTrue(all(r.get("Repository Path") for r in rows))
    def test_project_genesis_button_path_is_exact(self):
        self.assertEqual(CANONICAL_REGISTER_RELATIVE_PATH.as_posix(), "Documentation/Master_Asset_Register.csv")

if __name__ == "__main__": unittest.main()
