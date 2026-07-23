from __future__ import annotations
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; V=ROOT/"13_Project_Genesis/Validators"; sys.path.insert(0,str(V))
from tesamorelin_review_board_common import load_json,validate_record
EX=ROOT/"05_Monitoring/Examples/Tesamorelin"
MANIFEST=json.loads((ROOT/"Documentation/Build_Records/0059/ASSET_INTENT_MANIFEST.json").read_text())
CURRENT=[ROOT/x["repository_path"] for x in MANIFEST["files"] if x.get("classification")=="EXAMPLE"]
class Tests(unittest.TestCase):
 def test_valid_and_conditional_examples(self):
  for p in CURRENT:
   if p.name.startswith(("valid_","conditional_")): self.assertEqual(validate_record(load_json(p)),[],p.name)
 def test_invalid_examples_fail(self):
  for p in CURRENT:
   if p.name.startswith("invalid_"): self.assertTrue(validate_record(load_json(p)),p.name)
 def test_valid_bundle(self): self.assertEqual(len(CURRENT),20)
 def test_approval_requires_roles(self): self.assertIn("mandatory review-board roles missing",";".join(validate_record(load_json(EX/"invalid_review_board_missing_roles.example.json"))))
 def test_appeal_independence(self): self.assertIn("appeal panel must be independent", ";".join(validate_record(load_json(EX/"invalid_appeal_same_decider.example.json"))))
 def test_recovery_fail_closed(self): self.assertIn("recovery requires every criterion", ";".join(validate_record(load_json(EX/"invalid_recovery_without_criteria.example.json"))))
 def test_reassessment_fail_closed(self): self.assertIn("active suspension must remain fail-closed", ";".join(validate_record(load_json(EX/"invalid_reassessment_ignored_suspension.example.json"))))
 def test_transition_no_cross_peptide(self): self.assertIn("cross-peptide clinical equivalence", ";".join(validate_record(load_json(EX/"invalid_transition_cross_peptide_assumption.example.json"))))
