from __future__ import annotations
import csv, importlib.util, json, tempfile, unittest, zipfile
from pathlib import Path, PurePosixPath
MODULE=Path(__file__).resolve().parents[1]/"Import"/"transactional_build_import.py"
spec=importlib.util.spec_from_file_location("tbi_compat",MODULE); tbi=importlib.util.module_from_spec(spec); spec.loader.exec_module(tbi)
class ImporterCompatibility(unittest.TestCase):
    def make_repo(self,base):
        repo=base/"repo"; (repo/"Documentation").mkdir(parents=True); (repo/"00_Governance").mkdir(); (repo/"13_Project_Genesis/Import").mkdir(parents=True)
        fields=["Universal Asset Identifier","Asset Name","Knowledge System","Asset Type","Status","Owner","Repository Path","Version","Completion Percentage","Last Review","Next Review","Build Provenance","Source Builds","Registration Basis"]
        rows=[{"Universal Asset Identifier":"CERT-SYS-000009","Repository Path":"00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md"},{"Universal Asset Identifier":"CERT-SYS-000082","Repository Path":"13_Project_Genesis/Import/transactional_build_import.py"}]
        with (repo/"Documentation/Master_Asset_Register.csv").open("w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
        (repo/rows[0]["Repository Path"]).write_text("old checkpoint"); (repo/rows[1]["Repository Path"]).write_text("old importer")
        sibling=repo/"06_Evidence/Standards"; sibling.mkdir(parents=True); (sibling/"pre-existing.md").write_text("keep")
        return repo
    def make_zip(self,base):
        z=base/"mini.zip"; files={"00_Governance/CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md":"new checkpoint","13_Project_Genesis/Import/transactional_build_import.py":"new importer","Documentation/Build_Records/0039/ASSET_INTENT_MANIFEST.json":""}
        manifest={"package_version":"1.3.2","files":[{"repository_path":p,"classification":"FORMAL_ASSET" if not p.endswith("ASSET_INTENT_MANIFEST.json") else "BUILD_RECORD","intended_action":"UPDATE","existing_uai":"CERT-SYS-000009" if p.startswith("00_") else "CERT-SYS-000082","asset_title":p,"asset_type":"Platform Component","knowledge_system":"SYS","proposed_version":"1.3.2","proposed_status":"ACTIVE","owner":"Certiaura"} for p in files]}
        files["Documentation/Build_Records/0039/ASSET_INTENT_MANIFEST.json"]=json.dumps(manifest)
        with zipfile.ZipFile(z,"w") as zf:
            for p,c in files.items(): zf.writestr(p,c)
        return z
    def test_dry_run_cli_contract(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); repo=self.make_repo(base); z=self.make_zip(base)
            code=tbi.main([str(z),str(repo),"--asset-register","Documentation/Master_Asset_Register.csv","--report","Documentation/Build_Records/0039/test_report.json"])
            self.assertEqual(code,0); report=json.loads((repo/"Documentation/Build_Records/0039/test_report.json").read_text()); self.assertTrue(report["apply_allowed"]); self.assertFalse(report["applied"])
            self.assertEqual((repo/"06_Evidence/Standards/pre-existing.md").read_text(),"keep")
if __name__=="__main__": unittest.main()
