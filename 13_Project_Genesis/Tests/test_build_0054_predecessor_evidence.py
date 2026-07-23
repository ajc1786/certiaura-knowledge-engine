from __future__ import annotations
import importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; S=ROOT/"13_Project_Genesis/Release/derive_build_0053_predecessor_evidence.py"; spec=importlib.util.spec_from_file_location('d',S); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def git(r,*a): return subprocess.run(['git','-C',str(r),*a],check=True,text=True,stdout=subprocess.PIPE).stdout.strip()
class Tests(unittest.TestCase):
 def repo(self,td):
  r=Path(td)/'r'; r.mkdir(); git(r,'init'); git(r,'config','user.email','x@y'); git(r,'config','user.name','x'); files=[]
  for i in range(83):
   rel=f'Standards/Build0053Fixture/file_{i:02d}.txt'; p=r/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(f'{i}\n',encoding='utf-8',newline='\n'); files.append({'repository_path':rel})
  b=r/'Documentation/Build_Records/0053'; b.mkdir(parents=True); (b/'ASSET_INTENT_MANIFEST.json').write_text(json.dumps({'build_number':'0053','candidate':'RC4','files':files})+'\n',encoding='utf-8',newline='\n'); (b/'CANDIDATE_DELIVERY.json').write_text(json.dumps({'candidate':'RC4'})+'\n',encoding='utf-8',newline='\n'); git(r,'add','.'); git(r,'commit','-m','p'); return r,git(r,'rev-parse','HEAD'),files
 def test_git_source_and_overlap(self):
  with tempfile.TemporaryDirectory() as td:
   r,h,f=self.repo(td); c=Path(td)/'c.json'; c.write_text(json.dumps({'build_number':'0054','files':[]})+'\n',encoding='utf-8',newline='\n'); z=m.derive(r,c,expected_commit=h,expected_count=83); self.assertEqual(83,z['predecessor_path_count']); c.write_text(json.dumps({'build_number':'0054','files':[{'repository_path':f[0]['repository_path']}]})+'\n',encoding='utf-8',newline='\n'); self.assertRaises(RuntimeError,m.derive,r,c,None,h,83)
 def test_explicit_overlap_is_allowed(self):
  with tempfile.TemporaryDirectory() as td:
   r,h,f=self.repo(td); c=Path(td)/'c.json'; c.write_text(json.dumps({'build_number':'0054','files':[{'repository_path':f[0]['repository_path'],'intended_action':'UPDATE','approved_predecessor_overlap':True}]})+'\n',encoding='utf-8',newline='\n'); z=m.derive(r,c,expected_commit=h,expected_count=83); self.assertEqual([f[0]['repository_path']],z['approved_intersection'])
if __name__=='__main__': unittest.main()
