from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
VAL=ROOT/'13_Project_Genesis'/'Validators'
sys.path.insert(0,str(VAL))

from validate_contract_order import validate
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.good=json.loads((ROOT/'10_Marketplace/Examples/valid_contract_order.example.json').read_text())
  cls.bad=json.loads((ROOT/'10_Marketplace/Examples/invalid_automatic_order_release.example.json').read_text())
 def test_01_good_passes(self): self.assertEqual(validate(self.good),[])
 def test_02_bad_fails(self): self.assertGreaterEqual(len(validate(self.bad)),20)
 def test_03_auto_contract_blocked(self): self.assertTrue(any('automation-approved' in x for x in validate(self.bad)))
 def test_04_gate_blocked(self): self.assertTrue(any('gate supplier_assurance' in x for x in validate(self.bad)))
 def test_05_legal_gate(self): self.assertTrue(any('legal route' in x for x in validate(self.bad)))
 def test_06_substitution(self): self.assertTrue(any('substitution' in x for x in validate(self.bad)))
 def test_07_human_release(self): self.assertTrue(any('release cannot' in x for x in validate(self.bad)))
 def test_08_contract_roles(self): self.assertTrue(any('commercial and quality' in x for x in validate(self.bad)))
