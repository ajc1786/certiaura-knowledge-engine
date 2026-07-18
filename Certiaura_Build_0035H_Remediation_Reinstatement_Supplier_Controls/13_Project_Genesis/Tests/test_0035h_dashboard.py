import importlib.util, json, unittest
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
D=ROOT/'13_Project_Genesis'/'Dashboards'/'generate_supplier_dashboard.py'
spec=importlib.util.spec_from_file_location('dash',D); dash=importlib.util.module_from_spec(spec); spec.loader.exec_module(dash)
EX=ROOT/'08_Product_Passports'/'Examples'/'Output'
class Test0035HDashboard(unittest.TestCase):
 def test_dashboard_contains_core_sections(self):
  cases=[json.loads((EX/n).read_text(encoding='utf-8')) for n in ['valid_open_remediation.example.json','valid_reinstated_case.example.json','valid_supplier_escalation.example.json']]
  s=dash.build_dashboard(cases)
  self.assertIn('Portfolio KPIs',s); self.assertIn('Cases by state',s); self.assertIn('Supplier summary',s)
 def test_dashboard_reports_supplier(self):
  d=json.loads((EX/'valid_open_remediation.example.json').read_text(encoding='utf-8')); self.assertIn('PPS-SUP-ALPHA-001',dash.build_dashboard([d]))
if __name__=='__main__': unittest.main()
