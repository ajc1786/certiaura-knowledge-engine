import importlib.util, json, unittest
from pathlib import Path
from datetime import datetime
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
P=ROOT/'13_Project_Genesis'/'Automation'/'schedule_supplier_assurance.py'
spec=importlib.util.spec_from_file_location('scheduler',P); scheduler=importlib.util.module_from_spec(spec); spec.loader.exec_module(scheduler)
EX=ROOT/'08_Product_Passports'/'Examples'/'Output'
def load(n): return json.loads((EX/n).read_text(encoding='utf-8'))
class Test0035IScheduler(unittest.TestCase):
 def test_clean_supplier_no_alerts_at_build_date(self): self.assertEqual([],scheduler.alerts_for(load('valid_qualified_supplier.example.json'),datetime.fromisoformat('2026-07-19T12:00:00+00:00')))
 def test_suspended_supplier_has_open_trigger_alert(self): self.assertTrue(any(x['alert_type']=='OPEN_ASSURANCE_TRIGGER' for x in scheduler.alerts_for(load('valid_suspended_supplier.example.json'),datetime.fromisoformat('2026-07-19T12:00:00+00:00'))))
 def test_expired_qualification_alert(self): self.assertTrue(any(x['alert_type']=='QUALIFICATION_EXPIRED' for x in scheduler.alerts_for(load('valid_qualified_supplier.example.json'),datetime.fromisoformat('2028-01-01T00:00:00+00:00'))))
 def test_alerts_never_positive(self): self.assertTrue(all(x['automatic_positive_action'] is False for x in scheduler.alerts_for(load('valid_suspended_supplier.example.json'),datetime.fromisoformat('2026-07-19T12:00:00+00:00'))))
if __name__=='__main__': unittest.main()
