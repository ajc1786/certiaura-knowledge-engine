import importlib.util, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]
def module(name,rel):
 p=ROOT/rel; s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
portfolio=module('portfolio_dashboard','13_Project_Genesis/Dashboards/generate_portfolio_dashboard.py')
scorecard=module('scorecard','13_Project_Genesis/Dashboards/generate_supplier_scorecard.py')
class Test0035JDashboards(unittest.TestCase):
 def test_portfolio_dashboard(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/'dash.md'; self.assertEqual(0,portfolio.main([str(ROOT/'10_Marketplace'/'Examples'),str(out)])); t=out.read_text(); self.assertIn('Supplier Portfolio Risk',t); self.assertIn('Core research supply portfolio',t)
 def test_supplier_scorecard(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/'score.md'; self.assertEqual(0,scorecard.main([str(ROOT/'10_Marketplace'/'Examples'/'valid_diversified_portfolio.example.json'),str(out)])); t=out.read_text(); self.assertIn('Comparative Supplier',t); self.assertIn('Aurelia Scientific',t)
if __name__=='__main__': unittest.main()
