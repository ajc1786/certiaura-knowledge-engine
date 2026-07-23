from __future__ import annotations
import csv,importlib.util,json,subprocess,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; S=ROOT/"13_Project_Genesis/Import/run_build_0055_import.py"; spec=importlib.util.spec_from_file_location('i',S); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def git(r,*a): return subprocess.run(['git','-C',str(r),*a],check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.strip()
class Tests(unittest.TestCase):
 def repo(self,td):
  r=Path(td)/'r'; r.mkdir(); git(r,'init'); git(r,'config','user.email','x@y'); git(r,'config','user.name','x'); g=r/'00_Governance'; g.mkdir();
  for n in ['CERTIAURA_LOCKED_BUILD_CONTINUITY_AND_CHECKPOINT.md','CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.md']: (g/n).write_text('# baseline\n',encoding='utf-8',newline='\n')
  (g/'CERTIAURA_LOCKED_ACCUMULATED_LESSONS_AND_CONTINUOUS_LEARNING_STANDARD.control.json').write_text('{"build_updates":[]}\n',encoding='utf-8',newline='\n')
  d=r/'Documentation'; d.mkdir();
  with (d/'Master_Asset_Register.csv').open('w',encoding='utf-8',newline='') as h: csv.writer(h,lineterminator='\n').writerows([['Universal Asset Identifier','Repository Path','Asset Title','Asset Type','Knowledge System','Version','Status','Owner','Build Provenance'],['CERT-SYS-000859','Standards/EXISTING.md','Existing','Standard','SYS','1.0.0','ACTIVE','Governance','0054']])
  b=d/'Build_Records/0054'; b.mkdir(parents=True); paths=[]
  for i in range(79):
   rel=f'Synthetic_Predecessor/Build_0054/path_{i:02d}.txt'; p=r/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(f'{i}\n',encoding='utf-8',newline='\n'); paths.append(rel)
  shared='13_Project_Genesis/Validators/verify_staged_byte_equality.py'; sp=r/shared; sp.parent.mkdir(parents=True,exist_ok=True); sp.write_bytes((ROOT/shared).read_bytes()); paths.append(shared)
  paths += ['Documentation/Build_Records/0054/ASSET_INTENT_MANIFEST.json','Documentation/Build_Records/0054/CANDIDATE_DELIVERY.json']; self.assertEqual(82,len(paths))
  (b/'ASSET_INTENT_MANIFEST.json').write_text(json.dumps({'build_number':'0054','candidate':'RC4','files':[{'repository_path':x} for x in paths]},indent=2)+'\n',encoding='utf-8',newline='\n'); (b/'CANDIDATE_DELIVERY.json').write_text(json.dumps({'candidate':'RC4'})+'\n',encoding='utf-8',newline='\n'); git(r,'add','.'); git(r,'commit','-m','baseline'); return r,git(r,'rev-parse','HEAD')
 def package(self,td):
  a=Path(td)/'b.zip'; man=json.loads((ROOT/'Documentation/Build_Records/0055/ASSET_INTENT_MANIFEST.json').read_text(encoding='utf-8'))
  with zipfile.ZipFile(a,'w',zipfile.ZIP_DEFLATED) as z:
   for x in man['files']: z.write(ROOT/x['repository_path'],x['repository_path'])
  return a
 def audit(self,td):
  root=Path(td)/'audit'; root.mkdir(exist_ok=True)
  records=[{'build_number':f'{i:04d}','classification':'NO_WORKFLOW_AT_COMMIT','capture_status':'RESOLVED_EXCEPTION','accounted':True} for i in range(1,55)]
  summary={'schema_version':'1.0.0','expected_build_count':54,'record_count':54,'accounted_count':54,'verified_run_id_count':0,'exception_count':54,'unresolved_count':0,'all_builds_accounted':True,'all_exact_run_ids_captured':False,'result':'HISTORICAL_ACTIONS_AUDIT_COMPLETE'}
  (root/'HISTORICAL_GITHUB_ACTIONS_AUDIT_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
  (root/'HISTORICAL_GITHUB_ACTIONS_EVIDENCE.json').write_text(json.dumps({'schema_version':'1.0.0','summary':summary,'records':records},indent=2)+'\n',encoding='utf-8',newline='\n')
  (root/'HISTORICAL_GITHUB_ACTIONS_EXCEPTIONS.json').write_text(json.dumps({'schema_version':'1.0.0','exception_count':54,'exceptions':records},indent=2)+'\n',encoding='utf-8',newline='\n')
  (root/'HISTORICAL_GITHUB_ACTIONS_EVIDENCE_REGISTER.csv').write_text('build_number,classification,accounted\n'+''.join(f'{i:04d},NO_WORKFLOW_AT_COMMIT,True\n' for i in range(1,55)),encoding='utf-8',newline='\n')
  return root
 def test_rollback_clean_reapply_and_staged_rollback(self):
  with tempfile.TemporaryDirectory() as td:
   r,h=self.repo(td); p=self.package(td); forced=m.run_import(p,r,Path(td)/'bk',Path(td)/'f.json',True,True,self.audit(td),expected_predecessor_commit=h); self.assertEqual('ROLLBACK_STATE_EXACT',forced['result']); self.assertEqual('',git(r,'status','--porcelain'))
   clean=m.run_import(p,r,Path(td)/'bk',Path(td)/'c.json',True,False,self.audit(td),expected_predecessor_commit=h); self.assertEqual('CLEAN_REAPPLY_VALIDATED',clean['result']); man=json.loads((r/'Documentation/Build_Records/0055/ASSET_INTENT_MANIFEST.json').read_text(encoding='utf-8')); owned=sorted({x['repository_path'] for x in man['files']+man['generated_files']}); subprocess.run(['git','-C',str(r),'add','--all','--',*owned],check=True); rb=m.rollback_from_backup(r,clean['backup_path'],Path(td)/'rb.json'); self.assertEqual('ROLLBACK_STATE_EXACT',rb['result']); self.assertEqual('',git(r,'status','--porcelain'))
 def test_byte_identical_approved_update_is_owned_but_not_staged(self):
  with tempfile.TemporaryDirectory() as td:
   r,h=self.repo(td); p=self.package(td); c=m.run_import(p,r,Path(td)/'bk',Path(td)/'c.json',True,False,self.audit(td),expected_predecessor_commit=h); self.assertEqual('CLEAN_REAPPLY_VALIDATED',c['result'])
   man=json.loads((r/'Documentation/Build_Records/0055/ASSET_INTENT_MANIFEST.json').read_text(encoding='utf-8')); owned=sorted({x['repository_path'] for x in man['files']+man['generated_files']}); subprocess.run(['git','-C',str(r),'add','--all','--',*owned],check=True)
   staged=git(r,'diff','--cached','--name-only').splitlines(); shared='13_Project_Genesis/Validators/verify_staged_byte_equality.py'; self.assertIn(shared,owned); self.assertNotIn(shared,staged); self.assertEqual(len(owned)-1,len(staged))
   changed=git(r,'diff','HEAD','--name-only').splitlines(); self.assertEqual(sorted(staged),sorted(changed))

 def test_generated_reports_lf(self):
  with tempfile.TemporaryDirectory() as td:
   r,h=self.repo(td); git(r,'config','core.autocrlf','true'); p=self.package(td); c=m.run_import(p,r,Path(td)/'bk',Path(td)/'c.json',True,False,self.audit(td),expected_predecessor_commit=h); self.assertEqual('CLEAN_REAPPLY_VALIDATED',c['result'])
   for rel in ['Documentation/Build_Records/0055/ASSET_REGISTER_CHANGE_REPORT.json','Documentation/Build_Records/0055/CANONICAL_IMPORT_REPORT.json','Documentation/Build_Records/0055/POST_IMPORT_REPOSITORY_VALIDATION.json','Documentation/Build_Records/0055/PREDECESSOR_CANONICAL_EVIDENCE.json','Documentation/Build_Records/0055/HISTORICAL_GITHUB_ACTIONS_EVIDENCE.json','Documentation/Build_Records/0055/HISTORICAL_GITHUB_ACTIONS_EVIDENCE_REGISTER.csv','Documentation/Build_Records/0055/HISTORICAL_GITHUB_ACTIONS_EXCEPTIONS.json','Documentation/Build_Records/0055/HISTORICAL_GITHUB_ACTIONS_AUDIT_SUMMARY.json']: self.assertNotIn(b'\r\n',(r/rel).read_bytes())
if __name__=='__main__': unittest.main()
