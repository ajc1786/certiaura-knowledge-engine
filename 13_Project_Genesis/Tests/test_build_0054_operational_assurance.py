from __future__ import annotations
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/"13_Project_Genesis/Validators"))
from retatrutide_operational_assurance_common import load_json,validate_bundle,validate_record
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  m=json.loads((ROOT/"Documentation/Build_Records/0054/ASSET_INTENT_MANIFEST.json").read_text(encoding="utf-8")); c.paths=[ROOT/x["repository_path"] for x in m["files"] if x.get("classification")=="EXAMPLE"]
 def test_valid_and_conditional(self):
  for p in [x for x in self.paths if x.name.startswith(("valid_","conditional_"))]: self.assertEqual([],validate_record(load_json(p)),p.name)
 def test_invalid_fail(self):
  for p in [x for x in self.paths if x.name.startswith("invalid_")]: self.assertTrue(validate_record(load_json(p)),p.name)
 def test_valid_bundle(self):
  names=["valid_operational_assurance_assessment.example.json","valid_failure_mode_coverage_assessment.example.json","valid_platinum_readiness_assessment.example.json","valid_controlled_release_readiness_decision.example.json","valid_architecture_reuse_decision.example.json"]
  base=ROOT/"05_Monitoring/Examples/Retatrutide"; self.assertEqual([],validate_bundle([load_json(base/n) for n in names]))
if __name__=="__main__": unittest.main()
