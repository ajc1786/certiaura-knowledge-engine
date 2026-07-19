from __future__ import annotations
import json, sys, tempfile, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'13_Project_Genesis'/'Validators'))

from validate_surveillance_case import validate
class TestSurveillance(unittest.TestCase):
 def load(self,n): return json.loads((ROOT/'10_Marketplace'/'Examples'/n).read_text())
 def test_valid_critical(self): self.assertEqual(validate(self.load('valid_critical_signal.example.json')),[])
 def test_valid_trend(self): self.assertEqual(validate(self.load('valid_trend_signal.example.json')),[])
 def test_invalid(self): self.assertGreaterEqual(len(validate(self.load('invalid_signal_auto_close.example.json'))),20)
 def test_privacy(self): self.assertTrue(any(x['code']=='SUR-020' for x in validate(self.load('invalid_signal_auto_close.example.json'))))
 def test_traceability(self): self.assertTrue(any(x['code']=='SUR-040' for x in validate(self.load('invalid_signal_auto_close.example.json'))))
 def test_protective(self): self.assertTrue(any(x['code'].startswith('SUR-050') for x in validate(self.load('invalid_signal_auto_close.example.json'))))
 def test_auto_close(self): self.assertTrue(any(x['code']=='SUR-070' for x in validate(self.load('invalid_signal_auto_close.example.json'))))
