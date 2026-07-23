from __future__ import annotations
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Tests(unittest.TestCase):
 def test_all_formal_assets_are_tesamorelin_or_reusable(self):
  m=json.loads((ROOT/"Documentation/Build_Records/0058/ASSET_INTENT_MANIFEST.json").read_text())
  for x in m["files"]:
   if x.get("classification")=="FORMAL_ASSET": self.assertTrue("TESAMORELIN" in x["repository_path"] or "CERTIAURA" in x["repository_path"])
 def test_no_cross_peptide_equivalence(self):
  for p in list((ROOT/"Standards").glob("*0058*"))+list((ROOT/"Standards").glob("TESAMORELIN*")):
   if p.is_file(): self.assertNotIn("equivalent to retatrutide",p.read_text(encoding="utf-8").lower())
 def test_continuation_matrix_is_fail_closed(self):
  d=json.loads((ROOT/"Standards/TESAMORELIN_PILOT_CONTINUATION_AND_SUSPENSION_MATRIX.json").read_text()); self.assertGreaterEqual(len(d["suspension_triggers"]),5)
 def test_recurrence_model_has_mandatory_routes(self):
  d=json.loads((ROOT/"Standards/TESAMORELIN_LONGITUDINAL_SIGNAL_RECURRENCE_MODEL.json").read_text()); self.assertIn("CRITICAL_ANY",d["mandatory_routes"])
if __name__=="__main__": unittest.main()
