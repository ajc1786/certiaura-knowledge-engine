import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; V=ROOT/"13_Project_Genesis/Validators"; sys.path.insert(0,str(V))
from bpc157_transition_common import validate_record
EX=ROOT/"05_Monitoring/Examples/BPC157"
class Tests(unittest.TestCase):
 def load(self,p): return json.loads(p.read_text(encoding="utf-8"))
 def test_valid_and_conditional_examples(self):
  for p in list(EX.glob("valid_*.json"))+list(EX.glob("conditional_*.json")): self.assertEqual(validate_record(self.load(p)),[],p.name)
 def test_invalid_examples_fail(self):
  for p in EX.glob("invalid_*.json"): self.assertTrue(validate_record(self.load(p)),p.name)
 def test_example_count(self): self.assertEqual(len(list(EX.glob("*.example.json"))),21)
 def test_no_tesamorelin_transfer(self):
  for p in list(EX.glob("valid_*.json"))+list(EX.glob("conditional_*.json")): self.assertIs(self.load(p).get("tesamorelin_assumptions_transferred"),False)
 def test_board_hold_is_valid(self): self.assertEqual(validate_record(self.load(EX/"valid_board.example.json")),[])
 def test_board_approval_with_critical_gap_fails(self): self.assertIn("transition approval violates fail-closed boundaries",validate_record(self.load(EX/"invalid_board.example.json")))
 def test_wada_mismatch_fails(self): self.assertIn("2026 WADA boundary mismatch",validate_record(self.load(EX/"invalid_regulatory.example.json")))
 def test_human_overclaim_fails(self): self.assertIn("human evidence overclaim",validate_record(self.load(EX/"invalid_human.example.json")))
 def test_appeal_independence(self): self.assertIn("appeal panel overlaps original deciders",validate_record(self.load(EX/"invalid_appeal.example.json")))
 def test_repeatable_hold_can_pass(self): self.assertEqual(self.load(EX/"valid_readiness.example.json")["readiness_state"],"REPEATABLE_WITH_HOLD")
if __name__=="__main__": unittest.main()
