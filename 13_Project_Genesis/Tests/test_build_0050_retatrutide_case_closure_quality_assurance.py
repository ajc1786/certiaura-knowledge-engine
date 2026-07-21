from __future__ import annotations
import csv, hashlib, json, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Tests(unittest.TestCase):
 def load(self,rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
 def run_validator(self):
  return subprocess.run([sys.executable,'-B',str(ROOT/'13_Project_Genesis/Validators/validate_retatrutide_case_closure_quality_assurance.py'),str(ROOT)],capture_output=True,text=True)
 def test_validator_accepts_and_rejects_fixtures(self):
  r=self.run_validator(); self.assertEqual(0,r.returncode,r.stdout+r.stderr)
 def test_valid_closure(self): self.assertEqual('CLOSURE_APPROVED',self.load('12_Reports/Retatrutide/Examples/valid_case_closure.example.json')['closure_state'])
 def test_urgent_closure_is_invalid(self):
  obj=self.load('12_Reports/Retatrutide/Examples/invalid_closure_with_urgent_routing.example.json'); self.assertTrue(obj['urgent_routing_active'])
 def test_direct_identifier_fixture_present(self): self.assertIn('Patient name',self.load('12_Reports/Retatrutide/Examples/invalid_direct_identifier_closure.example.json')['notes'])
 def test_autonomous_treatment_fixture_present(self): self.assertIn('Increase dose',self.load('12_Reports/Retatrutide/Examples/invalid_autonomous_treatment_closure.example.json')['notes'])
 def test_invalid_hash_fixture(self): self.assertEqual('NOT-A-SHA',self.load('12_Reports/Retatrutide/Examples/invalid_reconciliation_hash.example.json')['source_hashes'][0])

 def test_quality_assurance_role_separation(self):
  obj=self.load('12_Reports/Retatrutide/Examples/valid_quality_assurance_review.example.json'); self.assertNotEqual(obj['generator_actor_role'],obj['reviewer_actor_role'])
 def test_unresolved_action_escalation_state(self):
  obj=self.load('12_Reports/Retatrutide/Examples/valid_unresolved_action_escalation.example.json'); self.assertEqual('ESCALATION_REQUIRED',obj['status'])
 def test_generator_creates_bundle(self):
  gen=ROOT/'13_Project_Genesis/Reports/generate_retatrutide_case_closure_quality_assurance.py'
  with tempfile.TemporaryDirectory() as d:
   args=[sys.executable,'-B',str(gen),str(ROOT/'12_Reports/Retatrutide/Examples/valid_case_closure.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_unresolved_action_escalation.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_outcome_reconciliation.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_quality_assurance_review.example.json'),'--output-dir',d,'--now','2026-07-21T20:00:00Z']
   r=subprocess.run(args,capture_output=True,text=True); self.assertEqual(0,r.returncode,r.stdout+r.stderr); self.assertTrue((Path(d)/'bundle_manifest.json').is_file()); self.assertTrue((Path(d)/'closure_summary.md').is_file())
 def test_generator_blocks_urgent_closure(self):
  gen=ROOT/'13_Project_Genesis/Reports/generate_retatrutide_case_closure_quality_assurance.py'
  with tempfile.TemporaryDirectory() as d:
   args=[sys.executable,'-B',str(gen),str(ROOT/'12_Reports/Retatrutide/Examples/invalid_closure_with_urgent_routing.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_unresolved_action_escalation.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_outcome_reconciliation.example.json'),str(ROOT/'12_Reports/Retatrutide/Examples/valid_quality_assurance_review.example.json'),'--output-dir',d]
   self.assertNotEqual(0,subprocess.run(args,capture_output=True,text=True).returncode)
 def test_manifest_exact_provenance_and_six_assets(self):
  manifest=self.load('Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json'); self.assertTrue(all(x['build_provenance']=='CERT-BUILD-0050' for x in manifest['files'])); self.assertEqual(6,sum(x['classification']=='FORMAL_ASSET' for x in manifest['files']))
 def test_no_build_0049_paths_owned(self):
  paths={x['path'] for x in self.load('Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json')['files']}; self.assertNotIn('13_Project_Genesis/Validators/build_0049_asset_ownership.py',paths)
 def test_runner_uses_discovery_and_rollback(self):
  s=(ROOT/'Scripts/Run_Certiaura_Build_0050.ps1').read_text(encoding='ascii'); self.assertIn('-m unittest discover -s $TestRoot -p "test_build_0050_retatrutide_case_closure_quality_assurance.py"',s); self.assertIn('BUILD 0050 POST-APPLY ROLLBACK: PASS',s); self.assertNotIn('$Candidates.FullName',s)
 def test_collection_and_backup_alias_controls(self):
  for rel in ['Scripts/Run_Certiaura_Build_0050.ps1','Scripts/Invoke_Certiaura_Build_0050_Windows_PS51_Regression.ps1']:
   s=(ROOT/rel).read_text(encoding='ascii'); self.assertNotIn('$MatchesArray = @($Matches)',[x.strip() for x in s.splitlines()])
  r=(ROOT/'Scripts/Invoke_Certiaura_Build_0050_Windows_PS51_Regression.ps1').read_text(encoding='ascii'); self.assertNotIn('-BackupRoot $BackupRoot',r); self.assertEqual(2,r.count('-BackupRoot $ExternalBackupRoot'))
 def test_lessons_gates(self):
  s=(ROOT/'Documentation/Build_Records/0050/LESSONS_LEARNED_REVIEW.md').read_text(encoding='utf-8')
  for phrase in ['Accumulated prior-build lessons reviewed','Current-build lessons recorded','Lessons converted to regression controls','Continuity checkpoint updated']: self.assertIn(phrase,s)
 def test_manifest_scope_semantic_patterns(self):
  r=(ROOT/'Scripts/Invoke_Certiaura_Build_0050_Windows_PS51_Regression.ps1').read_text(encoding='ascii'); self.assertIn('$ManifestScopePattern',r); self.assertIn('$OwnedPathsPattern',r); self.assertNotIn('manifest=self.load("Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json")',r)
 def test_package_scripts_ascii_and_lf(self):
  manifest = self.load(
      "Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json"
  )
  owned_paths = [
      ROOT / item["path"] for item in manifest["files"]
  ]
  scripts=[p for p in owned_paths if p.suffix.lower() in {'.ps1','.cmd'}]; self.assertTrue(scripts)
  for p in scripts:
   data=p.read_bytes(); data.decode('ascii'); self.assertNotIn(b'\r',data)
 def test_no_runtime_artifacts(self):
  manifest=self.load('Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json'); self.assertFalse(any('__pycache__' in x['path'] or x['path'].endswith(('.pyc','.pyo')) for x in manifest['files']))
 def test_validator_scopes_examples_to_exact_manifest_paths(self):
  validator=ROOT/'13_Project_Genesis/Validators/validate_retatrutide_case_closure_quality_assurance.py'
  with tempfile.TemporaryDirectory() as td:
   repo=Path(td)
   manifest_path=repo/'Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json'
   owned_rel='12_Reports/Retatrutide/Examples/valid_case_closure.example.json'
   prior_rel='12_Reports/Retatrutide/Examples/historical_build_0049_scope_fixture.example.json'
   manifest_path.parent.mkdir(parents=True)
   manifest_path.write_text(json.dumps({'build_id':'CERT-BUILD-0050','files':[{'path':owned_rel,'classification':'EXAMPLE','build_provenance':'CERT-BUILD-0050'}]},indent=2)+'\n',encoding='utf-8',newline='\n')
   owned=repo/owned_rel; owned.parent.mkdir(parents=True)
   owned.write_text(json.dumps({'build_provenance':'CERT-BUILD-0050','closure_state':'CLOSURE_APPROVED','open_action_count':0,'urgent_routing_active':False,'decision_actor_role':'HUMAN_CLINICAL_REVIEWER'},indent=2)+'\n',encoding='utf-8',newline='\n')
   prior=repo/prior_rel
   prior.write_text(json.dumps({'build_provenance':'CERT-BUILD-0049','notes':'Patient name present. Increase dose.'},indent=2)+'\n',encoding='utf-8',newline='\n')
   report=repo/'validator.json'
   result=subprocess.run([sys.executable,'-B',str(validator),str(repo),'--report',str(report)],capture_output=True,text=True)
   self.assertEqual(0,result.returncode,result.stdout+result.stderr)
   payload=json.loads(report.read_text(encoding='utf-8'))
   self.assertEqual([owned_rel],payload['checked_paths'])
   self.assertEqual('EXACT_ASSET_INTENT_MANIFEST_PATHS',payload['ownership_scope'])
 def test_validator_source_prohibits_shared_folder_glob(self):
  source=(ROOT/'13_Project_Genesis/Validators/validate_retatrutide_case_closure_quality_assurance.py').read_text(encoding='utf-8')
  self.assertIn('MANIFEST_PATH = Path("Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json")',source)
  self.assertIn('item.get("classification") != "EXAMPLE"',source)
  self.assertNotIn("ex.glob('*.json')",source)
  self.assertNotIn('rglob(',source)
 def test_schemas_parse(self):
  for p in (ROOT/'Schemas').glob('retatrutide_*closure*.json'): json.loads(p.read_text(encoding='utf-8'))
 def test_dry_run_blocks_nonidentical_collision(self):
  manifest=self.load('Documentation/Build_Records/0050/ASSET_INTENT_MANIFEST.json'); importer=ROOT/'13_Project_Genesis/Import/build_0050_transactional_import.py'
  with tempfile.TemporaryDirectory() as td:
   t=Path(td); package=t/'p.zip'
   with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for i in manifest['files']: z.write(ROOT/i['path'],i['path'])
   repo=t/'repo'; repo.mkdir(); subprocess.run(['git','-C',str(repo),'init'],check=True,capture_output=True); subprocess.run(['git','-C',str(repo),'config','user.name','Test'],check=True); subprocess.run(['git','-C',str(repo),'config','user.email','test@example.invalid'],check=True)
   reg=repo/'Documentation/Master_Asset_Register.csv'; reg.parent.mkdir(parents=True); fields=['Universal Asset Identifier','Asset Name','Knowledge System','Asset Type','Status','Owner','Parent Assets','Last Review','Notes','Repository Path','Supporting Files','Version','Completion Percentage','Child Assets','Relationship List','Evidence Links','Report Links','Marketplace Links','Next Review','Change History','Build Provenance','Source Builds','Registration Basis','File SHA256','Last Updated'];
   with reg.open('w',encoding='utf-8',newline='') as h: csv.DictWriter(h,fieldnames=fields,lineterminator='\n').writeheader()
   c=repo/'Schemas/retatrutide_case_closure.schema.json'; c.parent.mkdir(parents=True); c.write_text('{}\n',encoding='utf-8',newline='\n'); subprocess.run(['git','-C',str(repo),'add','-A'],check=True); subprocess.run(['git','-C',str(repo),'commit','-m','baseline'],check=True,capture_output=True)
   report=t/'r.json'; r=subprocess.run([sys.executable,'-B',str(importer),'--repository',str(repo),'--package',str(package),'--report',str(report)],capture_output=True,text=True); payload=json.loads(report.read_text()); self.assertNotEqual(0,r.returncode); self.assertEqual('FAILED_CLOSED',payload['transaction_status']); self.assertTrue(payload['conflicts'])
if __name__=='__main__': unittest.main()
