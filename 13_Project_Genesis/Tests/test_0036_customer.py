from __future__ import annotations
import json, sys, tempfile, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'13_Project_Genesis'/'Validators'))

from validate_customer_eligibility import validate
class TestCustomer(unittest.TestCase):
 def load(self,n): return json.loads((ROOT/'10_Marketplace'/'Examples'/n).read_text())
 def test_valid_individual(self): self.assertEqual(validate(self.load('valid_individual_eligibility.example.json')),[])
 def test_valid_org(self): self.assertEqual(validate(self.load('valid_organisation_conditional.example.json')),[])
 def test_invalid_auto(self): self.assertGreaterEqual(len(validate(self.load('invalid_automatic_eligibility.example.json'))),15)
 def test_invalid_prohibited(self): self.assertGreaterEqual(len(validate(self.load('invalid_prohibited_jurisdiction.example.json'))),2)
 def test_auto_decision_detected(self): self.assertTrue(any(x['code']=='ELG-070' for x in validate(self.load('invalid_automatic_eligibility.example.json'))))
 def test_mfa_detected(self): self.assertTrue(any(x['code']=='ELG-052' for x in validate(self.load('invalid_automatic_eligibility.example.json'))))
 def test_prohibited_detected(self): self.assertTrue(any(x['code']=='ELG-090' for x in validate(self.load('invalid_prohibited_jurisdiction.example.json'))))
