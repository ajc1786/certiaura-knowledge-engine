from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
VAL=ROOT/'13_Project_Genesis'/'Validators'
sys.path.insert(0,str(VAL))

from validate_settlement import validate
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.good=json.loads((ROOT/'09_Cost_Intelligence/Examples/valid_settlement.example.json').read_text())
  cls.bad=json.loads((ROOT/'09_Cost_Intelligence/Examples/invalid_settlement_open_incident.example.json').read_text())
 def test_01_good_passes(self): self.assertEqual(validate(self.good),[])
 def test_02_bad_fails(self): self.assertGreaterEqual(len(validate(self.bad)),14)
 def test_03_open_incident(self): self.assertTrue(any('incident_closed' in x for x in validate(self.bad)))
 def test_04_auto_release(self): self.assertTrue(any('released by automation' in x for x in validate(self.bad)))
 def test_05_reconcile(self): self.assertTrue(any('does not reconcile' in x for x in validate(self.bad)))
 def test_06_tax(self): self.assertTrue(any('tax' in x for x in validate(self.bad)))
 def test_07_approvals(self): self.assertTrue(any('commercial and finance' in x for x in validate(self.bad)))
 def test_08_closed_at(self): self.assertTrue(any('closed_at' in x for x in validate(self.bad)))
