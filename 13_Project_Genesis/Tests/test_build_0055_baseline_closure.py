from __future__ import annotations
import json,unittest
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
ROOT=Path(__file__).resolve().parents[2]; P=ROOT/'13_Project_Genesis/Validators/retatrutide_baseline_closure_common.py'; spec=spec_from_file_location('c',P); m=module_from_spec(spec); spec.loader.exec_module(m); EX=ROOT/'05_Monitoring/Examples/Retatrutide'; MANIFEST=ROOT/'Documentation/Build_Records/0055/ASSET_INTENT_MANIFEST.json'
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  manifest=json.loads(MANIFEST.read_text(encoding='utf-8')); c.example_paths=[ROOT/x['repository_path'] for x in manifest['files'] if x.get('classification')=='EXAMPLE']
 def test_valid_and_conditional(self):
  for p in [x for x in self.example_paths if x.name.startswith(('valid_','conditional_'))]: self.assertEqual([],m.validate_record(json.loads(p.read_text(encoding='utf-8'))),p.name)
 def test_invalid_fail(self):
  for p in [x for x in self.example_paths if x.name.startswith('invalid_')]: self.assertTrue(m.validate_record(json.loads(p.read_text(encoding='utf-8'))),p.name)
 def test_valid_bundle(self):
  names=['valid_operational_baseline_closure_decision.example.json','valid_controlled_release_authorisation.example.json','valid_reusable_architecture_handoff.example.json','valid_next_peptide_pilot_selection.example.json','valid_baseline_exception_reopening_decision.example.json']; self.assertEqual([],m.validate_bundle([json.loads((EX/n).read_text(encoding='utf-8')) for n in names]))
if __name__=='__main__': unittest.main()
