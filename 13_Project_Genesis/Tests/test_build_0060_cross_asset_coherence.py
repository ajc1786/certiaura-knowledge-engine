import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; S=ROOT/"Standards"
class Tests(unittest.TestCase):
 def j(self,n): return json.loads((S/n).read_text(encoding="utf-8"))
 def test_regulatory_matrix_marks_fda_as_proposal(self): self.assertEqual(self.j("BPC157_REGULATORY_AND_SPORT_BOUNDARY_MATRIX.json")["boundaries"][0]["state"],"PROPOSAL_PENDING")
 def test_wada_boundary_is_fail_closed(self): self.assertIn("S0_PROHIBITED_AT_ALL_TIMES",json.dumps(self.j("BPC157_REGULATORY_AND_SPORT_BOUNDARY_MATRIX.json")))
 def test_human_matrix_is_very_limited(self): self.assertEqual(self.j("BPC157_HUMAN_EVIDENCE_GAP_MATRIX.json")["human_evidence_state"],"VERY_LIMITED")
 def test_board_current_approval_ineligible(self): self.assertFalse(self.j("BPC157_REVIEW_BOARD_TRANSITION_DECISION_MATRIX.json")["decisions"][0]["current_baseline_eligible"])
 def test_safety_matrix_has_five_domains(self): self.assertGreaterEqual(len(self.j("BPC157_SAFETY_QUALITY_AND_UNCERTAINTY_BOUNDARY_MATRIX.json")["domains"]),5)
 def test_sources_have_authority_and_url(self):
  d=json.loads((ROOT/"Database/Registers/BPC157_Authoritative_Source_Register.json").read_text()); self.assertEqual(len(d["sources"]),5); self.assertTrue(all(x["authority"] and x["url"] for x in d["sources"]))
 def test_nonclinical_across_formal_json(self):
  for p in S.glob("BPC157_*.json"): self.assertIs(json.loads(p.read_text()).get("clinical_recommendation_authorised"),False,p.name)
 def test_reusable_standard_prohibits_transfer(self): self.assertIn("must not be transferred",(S/"REUSABLE_MULTI_PEPTIDE_ONBOARDING_READINESS_STANDARD.md").read_text())
if __name__=="__main__": unittest.main()
