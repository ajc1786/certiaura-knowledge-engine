from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
VAL=ROOT/'13_Project_Genesis'/'Validators'
sys.path.insert(0,str(VAL))

from validate_incident_recall import validate
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.good=json.loads((ROOT/'10_Marketplace/Examples/valid_critical_recall.example.json').read_text())
  cls.bad=json.loads((ROOT/'10_Marketplace/Examples/invalid_recall_without_traceability.example.json').read_text())
 def test_01_good_passes(self): self.assertEqual(validate(self.good),[])
 def test_02_bad_fails(self): self.assertGreaterEqual(len(validate(self.bad)),15)
 def test_03_traceability(self): self.assertTrue(any('traceability' in x for x in validate(self.bad)))
 def test_04_protection(self): self.assertTrue(any('protective action' in x for x in validate(self.bad)))
 def test_05_auto_recall(self): self.assertTrue(any('automation' in x for x in validate(self.bad)))
 def test_06_notifications(self): self.assertTrue(any('notifications' in x for x in validate(self.bad)))
 def test_07_capa(self): self.assertTrue(any('corrective' in x for x in validate(self.bad)))
 def test_08_command(self): self.assertTrue(any('commander' in x for x in validate(self.bad)))
