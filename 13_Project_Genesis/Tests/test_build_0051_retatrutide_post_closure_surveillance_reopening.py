from __future__ import annotations
import csv, json, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Tests(unittest.TestCase):
 def load(self,rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
 def run_validator(self): return subprocess.run([sys.executable,'-B',str(ROOT/'13_Project_Genesis/Validators/validate_retatrutide_post_closure_surveillance_reopening.py'),str(ROOT)],capture_output=True,text=True)
 def test_01_validator_accepts_and_rejects_fixtures(self):
  r=self.run_validator(); self.assertEqual(0,r.returncode,r.stdout+r.stderr)
 def test_02_valid_surveillance(self): self.assertEqual('SURVEILLANCE_DUE',self.load('12_Reports/Retatrutide/Examples/valid_post_closure_surveillance.example.json')['surveillance_state'])
 def test_03_not_due_abstention(self): self.assertEqual([],self.load('12_Reports/Retatrutide/Examples/conditional_review_not_due.example.json')['trigger_ids'])
 def test_04_periodic_review(self): self.assertEqual('REVIEW_COMPLETED',self.load('12_Reports/Retatrutide/Examples/valid_periodic_review.example.json')['review_state'])
 def test_05_reopening_human_separation(self):
  o=self.load('12_Reports/Retatrutide/Examples/valid_reopening_decision.example.json'); self.assertNotEqual(o['reviewer_actor_role'],o['generator_actor_role'])
 def test_06_recurrence_requires_review(self): self.assertTrue(self.load('12_Reports/Retatrutide/Examples/valid_recurrence_analytics.example.json')['human_review_required'])
 def test_07_direct_identifier_fixture(self): self.assertIn('Patient name',self.load('12_Reports/Retatrutide/Examples/invalid_direct_identifier_surveillance.example.json')['notes'])
 def test_08_autonomous_treatment_fixture(self): self.assertIn('Increase dose',self.load('12_Reports/Retatrutide/Examples/invalid_autonomous_treatment_reopening.example.json')['reason'])
 def test_09_missing_trigger_fixture(self): self.assertEqual('',self.load('12_Reports/Retatrutide/Examples/invalid_reopen_without_trigger.example.json')['trigger_id'])
 def test_10_urgent_signal_fixture(self): self.assertTrue(self.load('12_Reports/Retatrutide/Examples/invalid_closed_case_with_urgent_signal.example.json')['urgent_routing_active'])
 def test_11_invalid_hash_fixture(self): self.assertEqual('NOT-A-SHA',self.load('12_Reports/Retatrutide/Examples/invalid_recurrence_hash.example.json')['source_hashes'][0])
 def test_12_generator_creates_bundle(self):
  g=ROOT/'13_Project_Genesis/Reports/generate_retatrutide_post_closure_surveillance_reopening.py'
  with tempfile.TemporaryDirectory() as d:
   args=[sys.executable,'-B',str(g),str(ROOT/'12_Reports/Retatrutide/Examples/valid_post_closure_surveillance.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_periodic_review.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_reopening_decision.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_recurrence_analytics.example.json'),'--output-dir',d,'--now','2026-07-21T21:00:00Z']
   r=subprocess.run(args,capture_output=True,text=True); self.assertEqual(0,r.returncode,r.stdout+r.stderr); self.assertTrue((Path(d)/'bundle_manifest.json').is_file()); self.assertTrue((Path(d)/'post_closure_summary.md').is_file())
 def test_13_generator_blocks_urgent_closed_state(self):
  g=ROOT/'13_Project_Genesis/Reports/generate_retatrutide_post_closure_surveillance_reopening.py'
  with tempfile.TemporaryDirectory() as d:
   args=[sys.executable,'-B',str(g),str(ROOT/'12_Reports/Retatrutide/Examples/invalid_closed_case_with_urgent_signal.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_periodic_review.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_reopening_decision.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_recurrence_analytics.example.json'),'--output-dir',d]
   self.assertNotEqual(0,subprocess.run(args,capture_output=True,text=True).returncode)
 def test_14_manifest_exact_provenance_and_six_assets(self):
  m=self.load('Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json'); self.assertTrue(all(x['build_provenance']=='CERT-BUILD-0051' for x in m['files'])); self.assertEqual(6,sum(x['classification']=='FORMAL_ASSET' for x in m['files']))
 def test_15_no_build_0050_paths_owned(self):
  p={x['path'] for x in self.load('Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json')['files']}; self.assertNotIn('13_Project_Genesis/Validators/build_0050_asset_ownership.py',p)
 def test_16_runner_uses_discovery_and_rollback(self):
  s=(ROOT/'Scripts/Run_Certiaura_Build_0051.ps1').read_text(encoding='ascii'); self.assertIn('-m unittest discover -s $TestRoot -p "test_build_0051_retatrutide_post_closure_surveillance_reopening.py"',s); self.assertIn('BUILD 0051 POST-APPLY ROLLBACK: PASS',s); self.assertNotIn('$Candidates.FullName',s)
 def test_17_collection_and_backup_alias_controls(self):
  for rel in ['Scripts/Run_Certiaura_Build_0051.ps1','Scripts/Invoke_Certiaura_Build_0051_Windows_PS51_Regression.ps1']:
   s=(ROOT/rel).read_text(encoding='ascii'); self.assertNotIn('$MatchesArray = @($Matches)',[x.strip() for x in s.splitlines()])
  r=(ROOT/'Scripts/Invoke_Certiaura_Build_0051_Windows_PS51_Regression.ps1').read_text(encoding='ascii'); self.assertNotIn('-BackupRoot $BackupRoot',r); self.assertEqual(2,r.count('-BackupRoot $ExternalBackupRoot'))
 def test_18_lessons_gates(self):
  s=(ROOT/'Documentation/Build_Records/0051/LESSONS_LEARNED_REVIEW.md').read_text(encoding='utf-8')
  for p in ['Accumulated prior-build lessons reviewed','Current-build lessons recorded','Lessons converted to regression controls','Continuity checkpoint updated']: self.assertIn(p,s)
 def test_19_manifest_scope_semantic_patterns(self):
  r=(ROOT/'Scripts/Invoke_Certiaura_Build_0051_Windows_PS51_Regression.ps1').read_text(encoding='ascii'); self.assertIn('$ManifestScopePattern',r); self.assertIn('$OwnedPathsPattern',r); self.assertNotIn('manifest=self.load("Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json")',r)
 def test_20_package_scripts_ascii_and_lf(self):
  manifest = self.load(
      "Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json"
  )
  owned_paths = [
      ROOT / item["path"] for item in manifest["files"]
  ]
  scripts=[p for p in owned_paths if p.suffix.lower() in {'.ps1','.cmd'}]; self.assertTrue(scripts)
  for p in scripts:
   data=p.read_bytes(); data.decode('ascii'); self.assertNotIn(b'\r',data)
 def test_21_no_runtime_artifacts(self):
  m=self.load('Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json'); self.assertFalse(any('__pycache__' in x['path'] or x['path'].endswith(('.pyc','.pyo')) for x in m['files']))
 def test_22_validator_scopes_examples_to_exact_manifest_paths(self):
  validator=ROOT/'13_Project_Genesis/Validators/validate_retatrutide_post_closure_surveillance_reopening.py'
  with tempfile.TemporaryDirectory() as td:
   repo=Path(td); mp=repo/'Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json'; owned_rel='12_Reports/Retatrutide/Examples/valid_post_closure_surveillance.example.json'; prior_rel='12_Reports/Retatrutide/Examples/historical_build_0050_scope_fixture.example.json'; mp.parent.mkdir(parents=True)
   mp.write_text(json.dumps({'build_id':'CERT-BUILD-0051','files':[{'path':owned_rel,'classification':'EXAMPLE','build_provenance':'CERT-BUILD-0051'}]},indent=2)+'\n',encoding='utf-8',newline='\n')
   owned=repo/owned_rel; owned.parent.mkdir(parents=True); owned.write_text(json.dumps({'build_provenance':'CERT-BUILD-0051','case_id':'CASE-X','closure_record_id':'C','surveillance_state':'SURVEILLANCE_DUE','review_due_at':'2026-01-01T00:00:00Z','urgent_routing_active':False,'trigger_ids':[],'generated_actor_role':'COORDINATOR'},indent=2)+'\n',encoding='utf-8',newline='\n')
   prior=repo/prior_rel; prior.write_text(json.dumps({'build_provenance':'CERT-BUILD-0050','notes':'Patient name present. Increase dose.'},indent=2)+'\n',encoding='utf-8',newline='\n')
   report=repo/'validator.json'; result=subprocess.run([sys.executable,'-B',str(validator),str(repo),'--report',str(report)],capture_output=True,text=True); self.assertEqual(0,result.returncode,result.stdout+result.stderr); payload=json.loads(report.read_text(encoding='utf-8')); self.assertEqual([owned_rel],payload['checked_paths']); self.assertEqual('EXACT_ASSET_INTENT_MANIFEST_PATHS',payload['ownership_scope'])
 def test_23_validator_source_prohibits_shared_folder_glob(self):
  s=(ROOT/'13_Project_Genesis/Validators/validate_retatrutide_post_closure_surveillance_reopening.py').read_text(encoding='utf-8'); self.assertIn('MANIFEST_PATH=Path("Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json")',s); self.assertIn('item.get("classification")!="EXAMPLE"',s); self.assertNotIn('.glob(',s); self.assertNotIn('rglob(',s)
 def test_24_dry_run_blocks_nonidentical_collision(self):
  m=self.load('Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json'); importer=ROOT/'13_Project_Genesis/Import/build_0051_transactional_import.py'
  with tempfile.TemporaryDirectory() as td:
   t=Path(td); package=t/'p.zip'
   with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for i in m['files']: z.write(ROOT/i['path'],i['path'])
   repo=t/'repo'; repo.mkdir(); subprocess.run(['git','-C',str(repo),'init'],check=True,capture_output=True); subprocess.run(['git','-C',str(repo),'config','user.name','Test'],check=True); subprocess.run(['git','-C',str(repo),'config','user.email','test@example.invalid'],check=True)
   reg=repo/'Documentation/Master_Asset_Register.csv'; reg.parent.mkdir(parents=True); fields=['Universal Asset Identifier','Asset Name','Knowledge System','Asset Type','Status','Owner','Parent Assets','Last Review','Notes','Repository Path','Supporting Files','Version','Completion Percentage','Child Assets','Relationship List','Evidence Links','Report Links','Marketplace Links','Next Review','Change History','Build Provenance','Source Builds','Registration Basis','File SHA256','Last Updated']
   with reg.open('w',encoding='utf-8',newline='') as h: csv.DictWriter(h,fieldnames=fields,lineterminator='\n').writeheader()
   c=repo/'Schemas/retatrutide_post_closure_surveillance.schema.json'; c.parent.mkdir(parents=True); c.write_text('{}\n',encoding='utf-8',newline='\n'); subprocess.run(['git','-C',str(repo),'add','-A'],check=True); subprocess.run(['git','-C',str(repo),'commit','-m','baseline'],check=True,capture_output=True)
   report=t/'r.json'; r=subprocess.run([sys.executable,'-B',str(importer),'--repository',str(repo),'--package',str(package),'--report',str(report)],capture_output=True,text=True); self.assertNotEqual(0,r.returncode); payload=json.loads(report.read_text(encoding='utf-8')); self.assertEqual('FAILED_CLOSED',payload['transaction_status']); self.assertTrue(payload['conflicts'])
 def test_25_synthetic_predecessor_paths_do_not_overlap_package(self):
  manifest_paths={x['path'] for x in self.load('Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json')['files']}
  predecessor_paths={
   'Documentation/Historical/HISTORICAL_CONTROL_000050.md',
   'Documentation/Build_Records/0050/CLOSURE_RECORD.json',
   '02_Peptides/CERT-PKS-000001_Retatrutide/Monitoring/RETATRUTIDE_CASE_REVIEW_CLOSURE_AND_OUTCOME_RECONCILIATION_STANDARD.md',
   '13_Project_Genesis/Validators/build_0050_asset_ownership.py',
   '12_Reports/Retatrutide/Examples/historical_build_0050_scope_fixture.example.json',
   'Scripts/Legacy/UNRELATED_HISTORICAL_CRLF.ps1',
  }
  self.assertFalse(manifest_paths & predecessor_paths)
  source=(ROOT/'Scripts/Invoke_Certiaura_Build_0051_Windows_PS51_Regression.ps1').read_text(encoding='ascii')
  for path in predecessor_paths: self.assertIn(path.replace('/','\\'),source) if path.startswith(('13_Project_Genesis/','12_Reports/','02_Peptides/','Documentation/')) else None
  self.assertNotIn('$PriorOwnershipHelperPath = Join-Path $SyntheticRepo "13_Project_Genesis\\Validators\\build_0051_asset_ownership.py"',source)
  self.assertIn('Synthetic predecessor fixture overlaps a Build 0051 package path',source)
 def test_26_predecessor_fixture_dry_run_is_collision_free(self):
  m=self.load('Documentation/Build_Records/0051/ASSET_INTENT_MANIFEST.json'); importer=ROOT/'13_Project_Genesis/Import/build_0051_transactional_import.py'
  with tempfile.TemporaryDirectory() as td:
   t=Path(td); package=t/'p.zip'
   with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for i in m['files']: z.write(ROOT/i['path'],i['path'])
   repo=t/'repo'; repo.mkdir(); subprocess.run(['git','-C',str(repo),'init'],check=True,capture_output=True); subprocess.run(['git','-C',str(repo),'config','user.name','Test'],check=True); subprocess.run(['git','-C',str(repo),'config','user.email','test@example.invalid'],check=True)
   fields=['Universal Asset Identifier','Asset Name','Knowledge System','Asset Type','Status','Owner','Parent Assets','Last Review','Notes','Repository Path','Supporting Files','Version','Completion Percentage','Child Assets','Relationship List','Evidence Links','Report Links','Marketplace Links','Next Review','Change History','Build Provenance','Source Builds','Registration Basis','File SHA256','Last Updated']
   reg=repo/'Documentation/Master_Asset_Register.csv'; reg.parent.mkdir(parents=True)
   with reg.open('w',encoding='utf-8',newline='') as h: csv.DictWriter(h,fieldnames=fields,lineterminator='\n').writeheader()
   predecessor={
    'Documentation/Historical/HISTORICAL_CONTROL_000050.md':'# Historical control\n',
    'Documentation/Build_Records/0050/CLOSURE_RECORD.json':'{"build":"0050","state":"ACTIONS_GREEN_CLOSED"}\n',
    '02_Peptides/CERT-PKS-000001_Retatrutide/Monitoring/RETATRUTIDE_CASE_REVIEW_CLOSURE_AND_OUTCOME_RECONCILIATION_STANDARD.md':'# Build 0050 predecessor\n',
    '13_Project_Genesis/Validators/build_0050_asset_ownership.py':'BUILD_PROVENANCE = "CERT-BUILD-0050"\n',
    '12_Reports/Retatrutide/Examples/historical_build_0050_scope_fixture.example.json':'{"build_provenance":"CERT-BUILD-0050"}\n',
   }
   for rel,content in predecessor.items(): p=repo/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding='utf-8',newline='\n')
   subprocess.run(['git','-C',str(repo),'add','-A'],check=True); subprocess.run(['git','-C',str(repo),'commit','-m','Add Certiaura Build 0050 retatrutide case review closure, unresolved-action escalation, longitudinal outcome reconciliation and quality assurance analytics baseline'],check=True,capture_output=True)
   report=t/'dry.json'; result=subprocess.run([sys.executable,'-B',str(importer),'--repository',str(repo),'--package',str(package),'--report',str(report)],capture_output=True,text=True)
   self.assertEqual(0,result.returncode,result.stdout+result.stderr); payload=json.loads(report.read_text(encoding='utf-8')); self.assertEqual('DRY_RUN_VALIDATED',payload['transaction_status']); self.assertEqual([],payload['conflicts'])
if __name__=='__main__': unittest.main()
