from __future__ import annotations
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class Tests(unittest.TestCase):
 def test_acceptance_matches_workflow_and_safety(self):
  a=json.loads((ROOT/"Standards/TESAMORELIN_SIMULATION_ACCEPTANCE_MATRIX.json").read_text()); w=json.loads((ROOT/"Standards/TESAMORELIN_MONITORING_WORKFLOW_SIMULATION_MODEL.json").read_text()); s=json.loads((ROOT/"Standards/TESAMORELIN_SAFETY_ESCALATION_ROUTING_MATRIX.json").read_text()); self.assertTrue(a["acceptance_requirements"]["audit_trail_complete"]); self.assertTrue(w["audit_replay_required"]); self.assertEqual("STOP_AND_ESCALATE",s["routes"][-1]["decision"])
 def test_nonclinical_boundary_present(self):
  text="\n".join(p.read_text(encoding="utf-8") for p in (ROOT/"Standards").glob("*TESAMORELIN*")); self.assertIn("clinical",text.lower()); self.assertIn("prohibited",text.lower())
 def test_git_standard_requires_restore(self):
  text=(ROOT/"Standards/CERTIAURA_NON_INTERACTIVE_GIT_MAINTENANCE_STANDARD.md").read_text(encoding="utf-8").lower(); self.assertIn("restore",text); self.assertIn("finally",text); self.assertIn("gc.auto",text)
if __name__=="__main__": unittest.main()
