import importlib.util, json, unittest
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
P=ROOT/'13_Project_Genesis'/'Validators'/'validate_sourcing_decision.py'
spec=importlib.util.spec_from_file_location('validator',P); validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
EX=ROOT/'10_Marketplace'/'Examples'
def load(n): return json.loads((EX/n).read_text(encoding='utf-8'))
class Test0035JSourcingValidator(unittest.TestCase):
 def test_valid_decision(self): self.assertEqual([],validator.validate(load('valid_sourcing_decision.example.json')))
 def test_invalid_many_breaches(self): self.assertGreaterEqual(len(validator.validate(load('invalid_automatic_sole_source_award.example.json'))),15)
 def test_weights_sum(self):
  d=load('valid_sourcing_decision.example.json'); d['criteria_weights']['service']=6; self.assertTrue(any('sum to 100' in x for x in validator.validate(d)))
 def test_exact_criteria(self):
  d=load('valid_sourcing_decision.example.json'); del d['criteria_weights']['service']; self.assertTrue(any('exact criteria' in x for x in validator.validate(d)))
 def test_candidate_score_recalc(self):
  d=load('valid_sourcing_decision.example.json'); d['candidates'][0]['weighted_score']=0; self.assertTrue(any('weighted_score' in x for x in validator.validate(d)))
 def test_recommendation_nonbinding(self):
  d=load('valid_sourcing_decision.example.json'); d['calculated_recommendation']['recommendation_only']=False; self.assertTrue(any('recommendation_only' in x for x in validator.validate(d)))
 def test_automatic_award_blocked(self):
  d=load('valid_sourcing_decision.example.json'); d['decision']['automatic_award']=True; self.assertTrue(any('automatic_award' in x for x in validator.validate(d)))
 def test_price_only_blocked(self):
  d=load('valid_sourcing_decision.example.json'); d['decision']['price_only']=True; self.assertTrue(any('price_only' in x for x in validator.validate(d)))
 def test_independent_approval(self):
  d=load('valid_sourcing_decision.example.json'); d['decision']['approver_id']=d['decision']['reviewer_id']; self.assertTrue(any('reviewer and approver' in x for x in validator.validate(d)))
 def test_selected_supplier_current(self):
  d=load('valid_sourcing_decision.example.json'); d['candidates'][1]['assurance_status']='SUSPENDED'; self.assertTrue(any('selected supplier must be current' in x for x in validator.validate(d)))
 def test_sole_source_exception_required(self):
  d=load('valid_sourcing_decision.example.json'); d['candidates']=d['candidates'][:1]; d['calculated_recommendation']['supplier_id']='SUP-000001'; d['calculated_recommendation']['weighted_score']=90.1; self.assertTrue(any('at least two required' in x for x in validator.validate(d)))
 def test_conflicts_required(self):
  d=load('valid_sourcing_decision.example.json'); d['conflicts']=[]; self.assertTrue(any('declarations required' in x for x in validator.validate(d)))
 def test_assurance_separation(self):
  d=load('valid_sourcing_decision.example.json'); d['assurance_checks']['product_evidence_separate']=False; self.assertTrue(any('product_evidence_separate' in x for x in validator.validate(d)))
 def test_immutable_history(self):
  d=load('valid_sourcing_decision.example.json'); d['audit_trail']['immutable_history']=False; self.assertTrue(any('immutable_history' in x for x in validator.validate(d)))
if __name__=='__main__': unittest.main()
