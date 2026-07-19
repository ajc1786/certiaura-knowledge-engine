import importlib.util, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
P=ROOT/'13_Project_Genesis'/'Dashboards'/'generate_supplier_assurance_dashboard.py'
spec=importlib.util.spec_from_file_location('dash',P); dash=importlib.util.module_from_spec(spec); spec.loader.exec_module(dash)
class Test0035IDashboard(unittest.TestCase):
 def test_dashboard_generation(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/'dash.md'; rc=dash.main([str(ROOT/'08_Product_Passports'/'Examples'/'Output'),str(out)]); self.assertEqual(0,rc); t=out.read_text(); self.assertIn('Supplier Assurance Dashboard',t); self.assertIn('SUP-000001',t)
 def test_dashboard_separates_marketplace(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/'dash.md'; dash.main([str(ROOT/'08_Product_Passports'/'Examples'/'Output'),str(out)]); self.assertIn('Marketplace',out.read_text())
if __name__=='__main__': unittest.main()
