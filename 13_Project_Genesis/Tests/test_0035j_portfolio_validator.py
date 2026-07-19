import importlib.util, json, unittest
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
P=ROOT/'13_Project_Genesis'/'Validators'/'validate_supplier_portfolio.py'
spec=importlib.util.spec_from_file_location('validator',P); validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
EX=ROOT/'10_Marketplace'/'Examples'
def load(n): return json.loads((EX/n).read_text(encoding='utf-8'))
class Test0035JPortfolioValidator(unittest.TestCase):
 def test_diversified_valid(self): self.assertEqual([],validator.validate(load('valid_diversified_portfolio.example.json')))
 def test_concentrated_mitigated_valid(self): self.assertEqual([],validator.validate(load('valid_concentrated_mitigated_portfolio.example.json')))
 def test_invalid_has_many_breaches(self): self.assertGreaterEqual(len(validator.validate(load('invalid_uncontrolled_portfolio.example.json'))),20)
 def test_spend_total(self):
  d=load('valid_diversified_portfolio.example.json'); d['suppliers'][0]['annual_spend']+=1; self.assertTrue(any('annual_spend' in x for x in validator.validate(d)))
 def test_percent_total(self):
  d=load('valid_diversified_portfolio.example.json'); d['suppliers'][0]['spend_percent']=40; self.assertTrue(any('spend_percent' in x for x in validator.validate(d)))
 def test_hhi_recalculation(self):
  d=load('valid_diversified_portfolio.example.json'); d['concentration']['hhi']=0; self.assertTrue(any('concentration.hhi' in x for x in validator.validate(d)))
 def test_top_three_recalculation(self):
  d=load('valid_diversified_portfolio.example.json'); d['concentration']['top_three_percent']=0; self.assertTrue(any('top_three' in x for x in validator.validate(d)))
 def test_critical_requires_alternative_or_mitigation(self):
  d=load('valid_diversified_portfolio.example.json'); c=d['categories'][0]; c['active_alternatives']=[]; c['mitigation']=None; self.assertTrue(any('mitigation' in x for x in validator.validate(d)))
 def test_marketplace_requires_qualified(self):
  d=load('valid_diversified_portfolio.example.json'); d['suppliers'][0]['assurance_status']='CONDITIONAL'; self.assertTrue(any('eligibility requires QUALIFIED' in x for x in validator.validate(d)))
 def test_marketplace_four_eyes(self):
  d=load('valid_diversified_portfolio.example.json'); d['suppliers'][0]['marketplace']['approver_id']='USR-COM-01'; self.assertTrue(any('reviewer and approver' in x for x in validator.validate(d)))
 def test_total_cost_recalculation(self):
  d=load('valid_diversified_portfolio.example.json'); d['suppliers'][0]['commercial']['total_cost']=1; self.assertTrue(any('commercial.total_cost' in x for x in validator.validate(d)))
 def test_performance_bounds(self):
  d=load('valid_diversified_portfolio.example.json'); d['suppliers'][0]['performance']['quality_score']=101; self.assertTrue(any('quality_score' in x for x in validator.validate(d)))
 def test_red_requires_actions(self):
  d=load('valid_concentrated_mitigated_portfolio.example.json'); d['resilience']['open_actions']=[]; self.assertTrue(any('RED rating requires actions' in x for x in validator.validate(d)))
 def test_automatic_award_false(self):
  d=load('valid_diversified_portfolio.example.json'); d['governance']['automatic_award']=True; self.assertTrue(any('automatic_award' in x for x in validator.validate(d)))
 def test_human_review_required(self):
  d=load('valid_diversified_portfolio.example.json'); d['governance']['human_review_required']=False; self.assertTrue(any('human_review_required' in x for x in validator.validate(d)))
 def test_conflicts_declared(self):
  d=load('valid_diversified_portfolio.example.json'); d['governance']['conflicts_declared']=False; self.assertTrue(any('conflicts_declared' in x for x in validator.validate(d)))
 def test_immutable_history(self):
  d=load('valid_diversified_portfolio.example.json'); d['audit_trail']['immutable_history']=False; self.assertTrue(any('immutable_history' in x for x in validator.validate(d)))
if __name__=='__main__': unittest.main()
