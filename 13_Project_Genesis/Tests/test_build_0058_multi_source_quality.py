from __future__ import annotations
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; V=ROOT/"13_Project_Genesis/Validators"; sys.path.insert(0,str(V))
from tesamorelin_longitudinal_review_common import load_json,validate_record,validate_bundle
EX=ROOT/"05_Monitoring/Examples/Tesamorelin"
MANIFEST=json.loads((ROOT/"Documentation/Build_Records/0058/ASSET_INTENT_MANIFEST.json").read_text())
CURRENT=[ROOT/x["repository_path"] for x in MANIFEST["files"] if x.get("classification")=="EXAMPLE"]
class Tests(unittest.TestCase):
 def test_valid_and_conditional_examples(self):
  for p in CURRENT:
   if p.name.startswith(("valid_","conditional_")): self.assertEqual(validate_record(load_json(p)),[],p.name)
 def test_invalid_examples_fail(self):
  for p in CURRENT:
   if p.name.startswith("invalid_"): self.assertTrue(validate_record(load_json(p)),p.name)
 def test_valid_bundle(self):
  names=["valid_source_quality_assessment.example.json","valid_conflicting_evidence_resolution.example.json","valid_longitudinal_signal_review.example.json","valid_controlled_amendment.example.json","valid_pilot_continuation.example.json"]
  self.assertEqual(validate_bundle([load_json(EX/x) for x in names]),[])
 def test_bundle_hold_cannot_continue(self):
  names=["conditional_source_quality_hold.example.json","conditional_conflicting_evidence_hold.example.json","conditional_recurrent_signal_hold.example.json","conditional_amendment_hold.example.json","valid_pilot_continuation.example.json"]
  self.assertTrue(validate_bundle([load_json(EX/x) for x in names]))
if __name__=="__main__": unittest.main()
