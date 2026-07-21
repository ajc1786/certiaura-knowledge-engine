from __future__ import annotations
import csv, hashlib, json, os, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"13_Project_Genesis/Validators"))
from validate_retatrutide_clinician_approval_handoff import validate_review, validate_chain
class Build0048Tests(unittest.TestCase):
    def load(self,rel):return json.loads((ROOT/rel).read_text(encoding="utf-8"))
    def test_valid_approval_passes(self):self.assertEqual([],validate_review(self.load("12_Reports/Retatrutide/Examples/valid_clinician_review_approval.example.json")))
    def test_changes_required_passes(self):self.assertEqual([],validate_review(self.load("12_Reports/Retatrutide/Examples/conditional_clinician_review_changes_required.example.json")))
    def test_self_approval_fails(self):self.assertTrue(any("different actors" in x for x in validate_review(self.load("12_Reports/Retatrutide/Examples/invalid_self_approval.example.json"))))
    def test_direct_identifier_fails(self):self.assertTrue(any("direct identifier" in x for x in validate_review(self.load("12_Reports/Retatrutide/Examples/invalid_direct_identifier_review.example.json"))))
    def test_valid_version_chain_passes(self):self.assertEqual([],validate_chain(self.load("12_Reports/Retatrutide/Examples/valid_export_version_chain.example.json")))
    def test_broken_version_chain_fails(self):self.assertTrue(validate_chain(self.load("12_Reports/Retatrutide/Examples/invalid_broken_supersession_chain.example.json")))
    def test_manifest_exact_path_and_provenance(self):
        m=self.load("Documentation/Build_Records/0048/ASSET_INTENT_MANIFEST.json"); paths=[x["path"] for x in m["files"]]
        self.assertEqual(len(paths),len(set(paths))); self.assertTrue(all(x["build_provenance"]=="CERT-BUILD-0048" for x in m["files"])); self.assertTrue(m["substring_matching_prohibited"])
    def test_no_build47_path_collision(self):
        paths={x["path"] for x in self.load("Documentation/Build_Records/0048/ASSET_INTENT_MANIFEST.json")["files"]}
        old={"12_Reports/Standards/RETATRUTIDE_CLINICIAN_EXPORT_BASELINE.md","Schemas/retatrutide_clinician_export.schema.json","13_Project_Genesis/Validators/build_0047_asset_ownership.py"}
        self.assertFalse(paths & old)
    def test_generator_creates_manifest_and_summary(self):
        g=ROOT/"13_Project_Genesis/Reports/generate_retatrutide_clinician_handoff.py"
        with tempfile.TemporaryDirectory() as t:
            r=subprocess.run([sys.executable,"-B",str(g),str(ROOT/"12_Reports/Retatrutide/Examples/approved_export_payload.example.json"),str(ROOT/"12_Reports/Retatrutide/Examples/valid_clinician_review_approval.example.json"),str(ROOT/"12_Reports/Retatrutide/Examples/valid_export_version_chain.example.json"),"--output-dir",t,"--now","2026-07-21T12:30:00Z"],capture_output=True,text=True)
            self.assertEqual(0,r.returncode,r.stdout+r.stderr); o=Path(t); self.assertTrue((o/"bundle_manifest.json").is_file()); self.assertTrue((o/"handoff_summary.md").is_file()); b=json.loads((o/"handoff_bundle.json").read_text()); self.assertEqual("READY_FOR_AUTHORISED_HANDOFF",b["state"])
    def test_generator_rejects_self_approval(self):
        g=ROOT/"13_Project_Genesis/Reports/generate_retatrutide_clinician_handoff.py"
        with tempfile.TemporaryDirectory() as t:
            r=subprocess.run([sys.executable,"-B",str(g),str(ROOT/"12_Reports/Retatrutide/Examples/approved_export_payload.example.json"),str(ROOT/"12_Reports/Retatrutide/Examples/invalid_self_approval.example.json"),str(ROOT/"12_Reports/Retatrutide/Examples/valid_export_version_chain.example.json"),"--output-dir",t],capture_output=True,text=True)
            self.assertNotEqual(0,r.returncode)
    def test_runner_uses_unittest_discovery_and_rollback(self):
        s=(ROOT/"Scripts/Run_Certiaura_Build_0048.ps1").read_text(encoding="ascii")
        self.assertIn('-m unittest discover -s $TestRoot -p "test_build_0048_retatrutide_clinician_approval_handoff.py"',s)
        self.assertIn("BUILD 0048 POST-APPLY ROLLBACK: PASS",s); self.assertNotIn("$Candidates.FullName",s)
    def test_ps51_collection_and_alias_controls(self):
        for rel in ["Scripts/Run_Certiaura_Build_0048.ps1","Scripts/Invoke_Certiaura_Build_0048_Windows_PS51_Regression.ps1"]:
            s=(ROOT/rel).read_text(encoding="ascii")
            self.assertNotIn("$MatchesArray = @($Matches)", [line.strip() for line in s.splitlines()])
        r=(ROOT/"Scripts/Invoke_Certiaura_Build_0048_Windows_PS51_Regression.ps1").read_text(encoding="ascii")
        self.assertNotIn("-BackupRoot $BackupRoot",r)
        self.assertEqual(2,r.count("-BackupRoot $ExternalBackupRoot"))
        runner=(ROOT/"Scripts/Run_Certiaura_Build_0048.ps1").read_text(encoding="ascii")
        self.assertIn("$MatchesArray = [object[]]$Matches.ToArray()",runner)
        self.assertNotIn("$Matches.Count",runner)
    def test_accumulated_lessons_gates_present(self):
        text=(ROOT/"Documentation/Build_Records/0048/LESSONS_LEARNED_REVIEW.md").read_text()
        for x in ["Accumulated prior-build lessons reviewed","Current-build lessons recorded","Lessons converted to regression controls","Continuity checkpoint updated"]:self.assertIn(x,text)
    def test_dry_run_blocks_nonidentical_collision(self):
        m=self.load("Documentation/Build_Records/0048/ASSET_INTENT_MANIFEST.json"); importer=ROOT/"13_Project_Genesis/Import/build_0048_transactional_import.py"
        with tempfile.TemporaryDirectory() as t:
            temp=Path(t); package=temp/"p.zip"
            with zipfile.ZipFile(package,"w",zipfile.ZIP_DEFLATED) as z:
                for item in m["files"]:z.write(ROOT/item["path"],item["path"])
            repo=temp/"repo";repo.mkdir();subprocess.run(["git","-C",str(repo),"init"],check=True,capture_output=True);subprocess.run(["git","-C",str(repo),"config","user.name","Test"],check=True);subprocess.run(["git","-C",str(repo),"config","user.email","t@example.invalid"],check=True)
            reg=repo/"Documentation/Master_Asset_Register.csv";reg.parent.mkdir(parents=True); fields=["Universal Asset Identifier","Asset Name","Knowledge System","Asset Type","Status","Owner","Parent Assets","Last Review","Notes","Repository Path","Supporting Files","Version","Completion Percentage","Child Assets","Relationship List","Evidence Links","Report Links","Marketplace Links","Next Review","Change History","Build Provenance","Source Builds","Registration Basis","File SHA256","Last Updated"]
            with reg.open("w",encoding="utf-8",newline="") as f:csv.DictWriter(f,fieldnames=fields,lineterminator="\n").writeheader()
            collision=repo/"Schemas/retatrutide_clinician_review_decision.schema.json";collision.parent.mkdir(parents=True);collision.write_text("{}\n",encoding="utf-8",newline="\n")
            subprocess.run(["git","-C",str(repo),"add","-A"],check=True);subprocess.run(["git","-C",str(repo),"commit","-m","baseline"],check=True,capture_output=True)
            report=temp/"r.json"; result=subprocess.run([sys.executable,"-B",str(importer),"--repository",str(repo),"--package",str(package),"--report",str(report)],capture_output=True,text=True)
            payload=json.loads(report.read_text());self.assertNotEqual(0,result.returncode);self.assertEqual("FAILED_CLOSED",payload["transaction_status"]);self.assertTrue(payload["conflicts"])
    def test_package_scripts_ascii_and_lf(self):
        manifest=self.load("Documentation/Build_Records/0048/ASSET_INTENT_MANIFEST.json")
        owned_paths=[ROOT/item["path"] for item in manifest["files"]]
        scripts=[p for p in owned_paths if p.suffix.lower() in {".ps1",".cmd"}]
        self.assertTrue(scripts)
        for p in scripts:
            data=p.read_bytes()
            data.decode("ascii")
            self.assertNotIn(b"\r",data)
    def test_hygiene_scope_uses_exact_manifest_paths(self):
        source=Path(__file__).read_text(encoding="utf-8")
        self.assertIn('manifest=self.load("Documentation/Build_Records/0048/ASSET_INTENT_MANIFEST.json")',source)
        self.assertIn('owned_paths=[ROOT/item["path"] for item in manifest["files"]]',source)
        broad_scan='for p in ROOT.'+'rglob("*")'
        self.assertNotIn(broad_scan,source)
if __name__=="__main__":unittest.main()
