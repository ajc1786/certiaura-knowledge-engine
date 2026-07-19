from __future__ import annotations
import json, sys, tempfile, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'13_Project_Genesis'/'Validators'))

class TestAutomation(unittest.TestCase):
 def exec_script(self,script,input_path,out):
  return subprocess.run([sys.executable,str(ROOT/'13_Project_Genesis'/'Automation'/script),str(input_path),str(out)],capture_output=True,text=True)
 def test_eligibility_gate(self):
  with tempfile.TemporaryDirectory() as td:
   o=Path(td)/'o.json'; r=self.exec_script('eligibility_gate.py',ROOT/'10_Marketplace'/'Examples'/'valid_individual_eligibility.example.json',o); self.assertEqual(r.returncode,0); self.assertTrue(o.exists())
 def test_gate_no_authority(self):
  with tempfile.TemporaryDirectory() as td:
   o=Path(td)/'o.json'; self.exec_script('eligibility_gate.py',ROOT/'10_Marketplace'/'Examples'/'valid_individual_eligibility.example.json',o); self.assertEqual(json.loads(o.read_text())['automation_authority'],'NO_APPROVAL_AUTHORITY')
 def test_jurisdiction_monitor(self):
  with tempfile.TemporaryDirectory() as td:
   o=Path(td)/'o.json'; r=self.exec_script('jurisdiction_access_monitor.py',ROOT/'10_Marketplace'/'Examples',o); self.assertEqual(r.returncode,0); self.assertGreaterEqual(json.loads(o.read_text())['alert_count'],1)
 def test_privacy_monitor(self):
  with tempfile.TemporaryDirectory() as td:
   o=Path(td)/'o.json'; self.exec_script('privacy_retention_monitor.py',ROOT/'10_Marketplace'/'Examples',o); self.assertGreater(json.loads(o.read_text())['alert_count'],0)
 def test_signal_aggregator(self):
  with tempfile.TemporaryDirectory() as td:
   o=Path(td)/'o.json'; self.exec_script('signal_aggregator.py',ROOT/'10_Marketplace'/'Examples',o); self.assertGreaterEqual(json.loads(o.read_text())['case_count'],3)
 def test_reporting_monitor(self):
  with tempfile.TemporaryDirectory() as td:
   o=Path(td)/'o.json'; self.exec_script('reporting_deadline_monitor.py',ROOT/'10_Marketplace'/'Examples',o); self.assertGreaterEqual(json.loads(o.read_text())['alert_count'],1)
 def test_escalation_boundary(self):
  with tempfile.TemporaryDirectory() as td:
   o=Path(td)/'o.json'; self.exec_script('surveillance_escalation_engine.py',ROOT/'10_Marketplace'/'Examples'/'valid_critical_signal.example.json',o); d=json.loads(o.read_text()); self.assertFalse(d['may_close_case']); self.assertFalse(d['may_decide_reportability'])
