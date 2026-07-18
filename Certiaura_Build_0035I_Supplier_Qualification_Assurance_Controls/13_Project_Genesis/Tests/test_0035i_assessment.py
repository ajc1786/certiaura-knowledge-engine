import importlib.util, json, unittest
from pathlib import Path
from datetime import datetime
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
P=ROOT/'13_Project_Genesis'/'Automation'/'assess_supplier_assurance.py'
spec=importlib.util.spec_from_file_location('engine',P); engine=importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
EX=ROOT/'08_Product_Passports'/'Examples'/'Output'
def load(n): return json.loads((EX/n).read_text(encoding='utf-8'))
ASOF=datetime.fromisoformat('2026-07-19T12:00:00+00:00')
class Test0035IAssessment(unittest.TestCase):
 def test_low_risk_score(self): self.assertEqual((92,'LOW'),engine.score_and_tier(load('valid_qualified_supplier.example.json')))
 def test_high_risk_score(self): self.assertEqual((62,'HIGH'),engine.score_and_tier(load('valid_conditional_supplier.example.json')))
 def test_critical_flag_overrides_score(self):
  d=load('valid_qualified_supplier.example.json'); d['risk_assessment']['critical_flags']=['X']; self.assertEqual('CRITICAL',engine.score_and_tier(d)[1])
 def test_qualified_recommendation(self): self.assertEqual('QUALIFIED',engine.calculate(load('valid_qualified_supplier.example.json'),ASOF)['recommended_qualification_status'])
 def test_conditional_recommendation(self): self.assertEqual('CONDITIONAL',engine.calculate(load('valid_conditional_supplier.example.json'),ASOF)['recommended_qualification_status'])
 def test_suspension_recommendation(self): self.assertEqual('SUSPENDED',engine.calculate(load('valid_suspended_supplier.example.json'),ASOF)['recommended_qualification_status'])
 def test_marketplace_only_for_clean_qualified(self):
  self.assertTrue(engine.calculate(load('valid_qualified_supplier.example.json'),ASOF)['recommended_marketplace_supplier_eligible']); self.assertFalse(engine.calculate(load('valid_conditional_supplier.example.json'),ASOF)['recommended_marketplace_supplier_eligible'])
 def test_automatic_approval_always_prohibited(self): self.assertTrue(engine.calculate(load('valid_qualified_supplier.example.json'),ASOF)['automatic_approval_prohibited'])
if __name__=='__main__': unittest.main()
