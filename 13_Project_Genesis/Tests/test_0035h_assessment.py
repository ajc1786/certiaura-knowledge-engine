import importlib.util, json, unittest
from datetime import datetime
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
E=ROOT/'13_Project_Genesis'/'Automation'/'assess_remediation_case.py'
spec=importlib.util.spec_from_file_location('engine',E); engine=importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
EX=ROOT/'08_Product_Passports'/'Examples'/'Output'
def load(n): return json.loads((EX/n).read_text(encoding='utf-8'))
ASOF=datetime.fromisoformat('2026-07-22T16:05:00+00:00')

class Test0035HAssessment(unittest.TestCase):
 def test_open_case_not_ready(self): self.assertFalse(engine.calculate(load('valid_open_remediation.example.json'),ASOF)['readiness'])
 def test_reinstated_case_was_ready(self): self.assertTrue(engine.calculate(load('valid_reinstated_case.example.json'),ASOF)['readiness'])
 def test_integrity_hold_forces_suspension(self):
  r=engine.calculate(load('valid_supplier_escalation.example.json'),ASOF); self.assertIn('DATA_INTEGRITY_HOLD',r['blockers']); self.assertEqual('SUSPENDED',r['recommended_escalation'])
 def test_repeat_failures_reduce_score(self):
  d=load('valid_open_remediation.example.json'); a=engine.calculate(d,ASOF); d['case']['repeat_failure_count']=3; b=engine.calculate(d,ASOF); self.assertLess(b['calculated_supplier_score'],a['calculated_supplier_score'])
 def test_unverified_evidence_blocks(self): self.assertIn('CRITICAL_EVIDENCE_NOT_VERIFIED',engine.calculate(load('valid_open_remediation.example.json'),ASOF)['blockers'])
 def test_open_alert_blocks(self): self.assertIn('SOURCE_ALERT_OPEN',engine.calculate(load('valid_open_remediation.example.json'),ASOF)['blockers'])
 def test_engine_is_read_only(self):
  d=load('valid_open_remediation.example.json'); before=json.dumps(d,sort_keys=True); engine.calculate(d,ASOF); self.assertEqual(before,json.dumps(d,sort_keys=True))
 def test_automation_prohibition_always_true(self): self.assertTrue(engine.calculate(load('valid_reinstated_case.example.json'),ASOF)['automatic_reinstatement_prohibited'])
if __name__=='__main__': unittest.main()
