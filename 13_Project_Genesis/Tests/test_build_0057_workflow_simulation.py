from __future__ import annotations
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/"13_Project_Genesis/Validators"))
from tesamorelin_workflow_simulation_common import load_json,validate_bundle,validate_record
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  m=json.loads((ROOT/"Documentation/Build_Records/0057/ASSET_INTENT_MANIFEST.json").read_text(encoding="utf-8")); cls.examples=[ROOT/i["repository_path"] for i in m["files"] if i.get("classification")=="EXAMPLE"]
 def test_valid_and_conditional(self):
  for p in [x for x in self.examples if x.name.startswith(("valid_","conditional_"))]: self.assertEqual([],validate_record(load_json(p)),p.name)
 def test_invalid_fail(self):
  for p in [x for x in self.examples if x.name.startswith("invalid_")]: self.assertTrue(validate_record(load_json(p)),p.name)
 def test_valid_bundle(self):
  names={"valid_evidence_ingestion.example.json","valid_monitoring_workflow_event.example.json","conditional_safety_hold.example.json","valid_simulation_acceptance.example.json"}; records=[load_json(p) for p in self.examples if p.name in names]; self.assertEqual([],validate_bundle(records))
 def test_paths_are_tesamorelin_only(self):
  for p in self.examples: self.assertIn("/Tesamorelin/",p.as_posix()); self.assertNotIn("/Retatrutide/",p.as_posix())
if __name__=="__main__": unittest.main()
