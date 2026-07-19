from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
VAL=ROOT/'13_Project_Genesis'/'Validators'
sys.path.insert(0,str(VAL))

class T(unittest.TestCase):
 def runpy(self,script,args):
  return subprocess.run([sys.executable,str(ROOT/'13_Project_Genesis/Automation'/script),*map(str,args)],capture_output=True,text=True)
 def test_01_release_ready(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.json'; r=self.runpy('order_release_gate.py',[ROOT/'10_Marketplace/Examples/valid_contract_order.example.json',o]); self.assertEqual(r.returncode,0); self.assertEqual(json.loads(o.read_text())['generated_decision'],'READY_FOR_HUMAN_RELEASE')
 def test_02_release_blocked(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.json'; self.runpy('order_release_gate.py',[ROOT/'10_Marketplace/Examples/invalid_automatic_order_release.example.json',o]); self.assertEqual(json.loads(o.read_text())['generated_decision'],'BLOCKED')
 def test_03_no_release_authority(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.json'; self.runpy('order_release_gate.py',[ROOT/'10_Marketplace/Examples/valid_contract_order.example.json',o]); self.assertEqual(json.loads(o.read_text())['automation_authority'],'NO_RELEASE_AUTHORITY')
 def test_04_fulfilment_alert(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.json'; self.runpy('monitor_fulfilment.py',[ROOT/'10_Marketplace/Examples',o]); self.assertGreaterEqual(len(json.loads(o.read_text())['alerts']),1)
 def test_05_trace(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.json'; self.runpy('trace_recall.py',[ROOT/'10_Marketplace/Examples/valid_critical_recall.example.json',o]); self.assertEqual(json.loads(o.read_text())['population'],2)
 def test_06_trace_authority(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.json'; self.runpy('trace_recall.py',[ROOT/'10_Marketplace/Examples/valid_critical_recall.example.json',o]); self.assertIn('DRAFT',json.loads(o.read_text())['automation_authority'])
 def test_07_settlement_holds(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.json'; self.runpy('settlement_hold_engine.py',[ROOT/'09_Cost_Intelligence/Examples',o]); self.assertEqual(len(json.loads(o.read_text())['holds']),2)
 def test_08_no_hold_release(self):
  with tempfile.TemporaryDirectory() as x:
   o=Path(x)/'o.json'; self.runpy('settlement_hold_engine.py',[ROOT/'09_Cost_Intelligence/Examples',o]); self.assertTrue(all(h['automation_authority']=='NO_HOLD_RELEASE_AUTHORITY' for h in json.loads(o.read_text())['holds']))
