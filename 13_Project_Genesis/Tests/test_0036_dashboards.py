from __future__ import annotations
import json, sys, tempfile, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'13_Project_Genesis'/'Validators'))

class TestDashboards(unittest.TestCase):
 def gen(self,script):
  td=tempfile.TemporaryDirectory(); o=Path(td.name)/'d.md'; r=subprocess.run([sys.executable,str(ROOT/'13_Project_Genesis'/'Dashboards'/script),str(ROOT/'10_Marketplace'/'Examples'),str(o)],capture_output=True,text=True); return td,o,r
 def test_eligibility(self):
  td,o,r=self.gen('generate_eligibility_dashboard.py'); self.assertEqual(r.returncode,0); self.assertIn('Customer Eligibility Dashboard',o.read_text()); td.cleanup()
 def test_eligibility_boundary(self):
  td,o,r=self.gen('generate_eligibility_dashboard.py'); self.assertIn('grants no eligibility',o.read_text()); td.cleanup()
 def test_privacy(self):
  td,o,r=self.gen('generate_privacy_dashboard.py'); self.assertIn('Privacy Operations Dashboard',o.read_text()); td.cleanup()
 def test_privacy_boundary(self):
  td,o,r=self.gen('generate_privacy_dashboard.py'); self.assertIn('cannot close or refuse',o.read_text()); td.cleanup()
 def test_surveillance(self):
  td,o,r=self.gen('generate_surveillance_dashboard.py'); self.assertIn('Post-Market Surveillance Dashboard',o.read_text()); td.cleanup()
 def test_reporting(self):
  td,o,r=self.gen('generate_reporting_dashboard.py'); self.assertIn('Regulatory Reporting Assessment Dashboard',o.read_text()); td.cleanup()
 def test_reporting_boundary(self):
  td,o,r=self.gen('generate_reporting_dashboard.py'); self.assertIn('cannot determine legal reportability',o.read_text()); td.cleanup()
