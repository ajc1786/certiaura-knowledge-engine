from __future__ import annotations
import json, sys, tempfile, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'13_Project_Genesis'/'Validators'))

from validate_privacy_record import validate
class TestPrivacy(unittest.TestCase):
 def load(self,n): return json.loads((ROOT/'10_Marketplace'/'Examples'/n).read_text())
 def test_valid(self): self.assertEqual(validate(self.load('valid_privacy_request.example.json')),[])
 def test_invalid(self): self.assertGreaterEqual(len(validate(self.load('invalid_privacy_auto_close.example.json'))),7)
 def test_identity(self): self.assertTrue(any(x['code']=='PRV-020' for x in validate(self.load('invalid_privacy_auto_close.example.json'))))
 def test_human(self): self.assertTrue(any(x['code']=='PRV-021' for x in validate(self.load('invalid_privacy_auto_close.example.json'))))
 def test_legal_review(self): self.assertTrue(any(x['code']=='PRV-030' for x in validate(self.load('invalid_privacy_auto_close.example.json'))))
 def test_audit(self): self.assertTrue(any(x['code']=='PRV-040' for x in validate(self.load('invalid_privacy_auto_close.example.json'))))
 def test_due_date_valid(self): self.assertFalse(any(x['code']=='PRV-025' for x in validate(self.load('valid_privacy_request.example.json'))))
