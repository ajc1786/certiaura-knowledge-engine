from __future__ import annotations
import ast,csv,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; MP=ROOT/"Documentation/Build_Records/0054/ASSET_INTENT_MANIFEST.json"; IP=ROOT/"Documentation/Build_Records/0054/PACKAGE_INVENTORY.csv"
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c): c.m=json.loads(MP.read_text(encoding="utf-8")); c.items=c.m["files"]; c.paths={x["repository_path"].replace("\\","/") for x in c.items}
 def test_inventory(self):
  with IP.open(encoding="utf-8",newline="") as h: inv={r["repository_path"] for r in csv.DictReader(h)}
  self.assertEqual(self.paths,inv); self.assertEqual(len(self.paths),self.m["package_file_count"])
 def test_allowed_roots(self):
  allowed={"00_Governance","01_Knowledge_Systems","02_Peptides","03_Biology","04_Conditions","05_Monitoring","06_Evidence","07_Goals","08_Product_Passports","09_Cost_Intelligence","10_Marketplace","11_Academy","12_Reports","13_Project_Genesis","Assets","Database","Documentation","Images","Schemas","Scripts","Standards","Templates"}
  for rel in self.paths: self.assertIn(Path(rel).parts[0],allowed)
 def test_no_runtime_artifacts(self): self.assertFalse([x for x in self.paths if x.endswith('.pyc') or '/__pycache__/' in '/'+x+'/'])
 def test_lf_writers(self):
  bad=[]
  for x in self.items:
   if x["repository_path"].endswith('.py') and x.get('classification')!='TEST':
    p=ROOT/x["repository_path"]; tree=ast.parse(p.read_text(encoding='utf-8'))
    for n in ast.walk(tree):
     if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='write_text':
      kw=next((k.value for k in n.keywords if k.arg=='newline'),None)
      if not (isinstance(kw,ast.Constant) and kw.value=='\n'): bad.append(f"{x['repository_path']}:{n.lineno}")
  self.assertEqual([],bad)
 def test_reused_staged_byte_validator_is_approved_update(self):
  item=next(x for x in self.items if x['repository_path']=='13_Project_Genesis/Validators/verify_staged_byte_equality.py')
  self.assertEqual('UPDATE',item['intended_action'])
  self.assertIs(True,item.get('approved_predecessor_overlap'))
  self.assertEqual('NO_CHANGE',item.get('master_asset_register_action'))
  self.assertEqual('2fb118441e31b7161869be1ba657615fb7705ad022e7ec19fd6e631d40ba8b08',__import__('hashlib').sha256((ROOT/item['repository_path']).read_bytes()).hexdigest())
 def test_no_op_update_staged_change_set_gate(self):
  for rel in ['Scripts/Invoke_Certiaura_Build_0054_Windows_PS51_Regression.ps1','Scripts/Run_Certiaura_Build_0054.ps1']:
   text=(ROOT/rel).read_text(encoding='utf-8')
   self.assertIn('BUILD_0054_STAGED_CHANGESET_VALIDATED',text)
   self.assertIn('approved_predecessor_overlap',text)
   self.assertIn('Compare-Object',text)
   self.assertIn('diff HEAD --name-only',text)

 def test_optional_overlap_property_is_strictmode_safe(self):
  for rel in ['Scripts/Invoke_Certiaura_Build_0054_Windows_PS51_Regression.ps1','Scripts/Run_Certiaura_Build_0054.ps1']:
   text=(ROOT/rel).read_text(encoding='utf-8')
   self.assertIn('function Test-ApprovedPredecessorUpdate',text)
   self.assertIn('PSObject.Properties["approved_predecessor_overlap"]',text)
   self.assertIn('BUILD_0054_OPTIONAL_PROPERTY_STRICTMODE_VALIDATED',text)
   self.assertNotIn('$_.approved_predecessor_overlap -eq $true',text)

 def test_actions_run_id_closure_requirement(self):
  d=json.loads((ROOT/"Documentation/Build_Records/0054/GITHUB_ACTIONS_CLOSURE_EVIDENCE_REQUIREMENTS.json").read_text(encoding='utf-8')); self.assertTrue(d['mandatory']); self.assertIn('run_id',d['fields']); self.assertTrue(d['must_match_canonical_commit'])
if __name__=='__main__': unittest.main()
