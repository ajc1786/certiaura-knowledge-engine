from __future__ import annotations
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Tests(unittest.TestCase):
 def test_all_formal_assets_are_tesamorelin_or_reusable(self):
  m=json.loads((ROOT/"Documentation/Build_Records/0059/ASSET_INTENT_MANIFEST.json").read_text()); f=[x for x in m["files"] if x.get("classification")=="FORMAL_ASSET"]; self.assertEqual(len(f),7); self.assertTrue(all("TESAMORELIN" in x["repository_path"] or "REUSABLE" in x["repository_path"] or "CLOSURE_EVIDENCE" in x["repository_path"] for x in f))
 def test_review_board_model_roles(self):
  t=(ROOT/"Standards/TESAMORELIN_REVIEW_BOARD_GOVERNANCE_STANDARD.md").read_text();
  for r in ["chair","evidence reviewer","safety reviewer","governance reviewer"]: self.assertIn(r,t.lower())
 def test_evidence_pack_versioning_immutable(self): self.assertIn("immutable",(ROOT/"Standards/TESAMORELIN_EVIDENCE_PACK_VERSION_CONTROL_STANDARD.md").read_text().lower())
 def test_challenge_matrix_independent(self): self.assertTrue(json.loads((ROOT/"Standards/TESAMORELIN_CHALLENGE_AND_APPEAL_MATRIX.json").read_text())["same_decider_appeal_prohibited"])
 def test_transition_model_reusable(self): self.assertIn("governance mechanics",(ROOT/"Standards/REUSABLE_PEPTIDE_REVIEW_OPERATING_MODEL_STANDARD.md").read_text())
 def test_nonclinical(self):
  for p in (ROOT/"Standards").glob("*0059*"): self.assertNotIn("clinical recommendation authorised",p.read_text().lower())
