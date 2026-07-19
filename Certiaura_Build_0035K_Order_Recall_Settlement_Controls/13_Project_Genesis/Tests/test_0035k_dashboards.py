from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
VAL=ROOT/'13_Project_Genesis'/'Validators'
sys.path.insert(0,str(VAL))

class T(unittest.TestCase):
 def runpy(self,script,args): return subprocess.run([sys.executable,str(ROOT/'13_Project_Genesis/Dashboards'/script),*map(str,args)],capture_output=True,text=True)
 def test_01_ops_generated(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.md'; self.runpy('generate_operations_dashboard.py',[ROOT/'10_Marketplace/Examples',o]); self.assertTrue(o.exists())
 def test_02_ops_content(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.md'; self.runpy('generate_operations_dashboard.py',[ROOT/'10_Marketplace/Examples',o]); self.assertIn('Excursions',o.read_text())
 def test_03_ops_disclaimer(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.md'; self.runpy('generate_operations_dashboard.py',[ROOT/'10_Marketplace/Examples',o]); self.assertIn('creates no approval',o.read_text())
 def test_04_incident_generated(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'i.md'; self.runpy('generate_incident_dashboard.py',[ROOT/'10_Marketplace/Examples',o]); self.assertIn('INC-0035K-CRIT-001',o.read_text())
 def test_05_incident_authority(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'i.md'; self.runpy('generate_incident_dashboard.py',[ROOT/'10_Marketplace/Examples',o]); self.assertIn('Human incident command',o.read_text())
 def test_06_settlement_generated(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'s.md'; self.runpy('generate_settlement_dashboard.py',[ROOT/'09_Cost_Intelligence/Examples',o]); self.assertIn('SET-0035K-001',o.read_text())
 def test_07_settlement_hold(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'s.md'; self.runpy('generate_settlement_dashboard.py',[ROOT/'09_Cost_Intelligence/Examples',o]); self.assertIn('RELEASED',o.read_text())
 def test_08_settlement_disclaimer(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'s.md'; self.runpy('generate_settlement_dashboard.py',[ROOT/'09_Cost_Intelligence/Examples',o]); self.assertIn('cannot release holds',o.read_text())
