import importlib.util, json, unittest
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
V=ROOT/'13_Project_Genesis'/'Validators'/'validate_supplier_assurance.py'
spec=importlib.util.spec_from_file_location('validator',V); validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
EX=ROOT/'08_Product_Passports'/'Examples'/'Output'
def load(n): return json.loads((EX/n).read_text(encoding='utf-8'))

class Test0035IValidator(unittest.TestCase):
 def test_qualified_passes(self): self.assertEqual([],validator.validate(load('valid_qualified_supplier.example.json')))
 def test_conditional_passes(self): self.assertEqual([],validator.validate(load('valid_conditional_supplier.example.json')))
 def test_suspended_passes(self): self.assertEqual([],validator.validate(load('valid_suspended_supplier.example.json')))
 def test_invalid_fails_many_controls(self): self.assertGreaterEqual(len(validator.validate(load('invalid_auto_qualified_supplier.example.json'))),35)
 def test_no_automatic_positive_action(self):
  d=load('valid_qualified_supplier.example.json'); d['qualification']['automatic_positive_action']=True; self.assertTrue(any('automatic_positive_action' in x for x in validator.validate(d)))
 def test_four_eyes_required(self):
  d=load('valid_qualified_supplier.example.json'); d['qualification']['second_approver_id']=d['qualification']['primary_reviewer_id']; self.assertTrue(any('must differ' in x for x in validator.validate(d)))
 def test_mandatory_evidence_required(self):
  d=load('valid_qualified_supplier.example.json'); d['due_diligence']['evidence_items']=d['due_diligence']['evidence_items'][:-1]; self.assertTrue(any('missing current mandatory' in x for x in validator.validate(d)))
 def test_hash_required(self):
  d=load('valid_qualified_supplier.example.json'); d['due_diligence']['evidence_items'][0]['sha256']='bad'; self.assertTrue(any('SHA-256' in x for x in validator.validate(d)))
 def test_critical_flag_blocks_positive(self):
  d=load('valid_qualified_supplier.example.json'); d['risk_assessment']['critical_flags']=['DATA_INTEGRITY_CONCERN']; self.assertTrue(any('critical risk prohibits' in x for x in validator.validate(d)))
 def test_score_must_reconcile(self):
  d=load('valid_qualified_supplier.example.json'); d['risk_assessment']['score']=100; self.assertTrue(any('risk_assessment.score' in x for x in validator.validate(d)))
 def test_audit_cadence_matches_tier(self):
  d=load('valid_conditional_supplier.example.json'); d['audit']['cadence_days']=365; self.assertTrue(any('cadence_days' in x for x in validator.validate(d)))
 def test_critical_findings_block_positive(self):
  d=load('valid_qualified_supplier.example.json'); d['audit']['critical_findings']=1; self.assertTrue(any('critical audit findings' in x for x in validator.validate(d)))
 def test_conditional_requires_conditions(self):
  d=load('valid_conditional_supplier.example.json'); d['qualification']['conditions']=[]; self.assertTrue(any('requires conditions' in x for x in validator.validate(d)))
 def test_conditional_marketplace_default_false(self):
  d=load('valid_conditional_supplier.example.json'); d['restrictions']['marketplace_supplier_eligible']=True; self.assertTrue(any('conditional supplier' in x for x in validator.validate(d)))
 def test_blocked_supplier_restrictions(self):
  d=load('valid_suspended_supplier.example.json'); d['restrictions']['passport_submission_allowed']=True; self.assertTrue(any('blocked or critical' in x for x in validator.validate(d)))
 def test_downstream_review_on_suspension(self):
  d=load('valid_suspended_supplier.example.json'); d['integration']['downstream_review_required']=False; self.assertTrue(any('downstream_review_required' in x for x in validator.validate(d)))
 def test_monitoring_watches_required(self):
  d=load('valid_qualified_supplier.example.json'); d['continuous_assurance']['laboratory_change_watch']=False; self.assertTrue(any('laboratory_change_watch' in x for x in validator.validate(d)))
 def test_immutable_audit_required(self):
  d=load('valid_qualified_supplier.example.json'); d['audit_trail']['immutable_history']=False; self.assertTrue(any('immutable_history' in x for x in validator.validate(d)))
if __name__=='__main__': unittest.main()
