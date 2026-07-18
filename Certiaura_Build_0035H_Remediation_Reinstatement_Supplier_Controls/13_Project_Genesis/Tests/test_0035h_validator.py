import importlib.util, json, unittest
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
V=ROOT/'13_Project_Genesis'/'Validators'/'validate_remediation_case.py'
spec=importlib.util.spec_from_file_location('validator',V); validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
EX=ROOT/'08_Product_Passports'/'Examples'/'Output'
def load(n): return json.loads((EX/n).read_text(encoding='utf-8'))

class Test0035HValidator(unittest.TestCase):
 def test_open_case_passes(self): self.assertEqual([],validator.validate(load('valid_open_remediation.example.json')))
 def test_reinstated_case_passes(self): self.assertEqual([],validator.validate(load('valid_reinstated_case.example.json')))
 def test_escalation_case_passes(self): self.assertEqual([],validator.validate(load('valid_supplier_escalation.example.json')))
 def test_invalid_case_fails_many_controls(self):
  e=validator.validate(load('invalid_auto_reinstatement.example.json')); self.assertGreaterEqual(len(e),20); self.assertTrue(any('automatic_positive_action' in x for x in e))
 def test_four_eyes_required(self):
  d=load('valid_reinstated_case.example.json'); d['review']['second_approver_id']=d['review']['primary_reviewer_id']; self.assertTrue(any('must differ' in x for x in validator.validate(d)))
 def test_marketplace_separate_transaction_required(self):
  d=load('valid_reinstated_case.example.json'); d['reinstatement']['marketplace']['transaction_id']=None; self.assertTrue(any('marketplace.transaction_id' in x for x in validator.validate(d)))
 def test_holds_block_reinstatement(self):
  d=load('valid_reinstated_case.example.json'); d['case']['legal_hold']=True; self.assertTrue(any('holds prohibit' in x for x in validator.validate(d)))
 def test_alerts_must_reconcile(self):
  d=load('valid_reinstated_case.example.json'); d['alert_closure']=[]; self.assertTrue(any('reconcile exactly' in x for x in validator.validate(d)))
 def test_critical_action_needs_effectiveness(self):
  d=load('valid_reinstated_case.example.json'); d['corrective_action_plan']['actions'][0]['effectiveness_result']='FAIL'; self.assertTrue(any('effectiveness PASS' in x for x in validator.validate(d)))
 def test_hash_required(self):
  d=load('valid_reinstated_case.example.json'); d['evidence_refresh']['evidence_items'][0]['sha256']='bad'; self.assertTrue(any('sha256' in x for x in validator.validate(d)))
 def test_score_reconciles(self):
  d=load('valid_reinstated_case.example.json'); d['supplier_performance']['score']=99; self.assertTrue(any('supplier_performance.score' in x for x in validator.validate(d)))
 def test_immutable_audit_required(self):
  d=load('valid_open_remediation.example.json'); d['audit']['immutable_history']=False; self.assertTrue(any('immutable_history' in x for x in validator.validate(d)))
if __name__=='__main__': unittest.main()
