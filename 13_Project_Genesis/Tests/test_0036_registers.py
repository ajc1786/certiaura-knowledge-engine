from __future__ import annotations
import json, sys, tempfile, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'13_Project_Genesis'/'Validators'))

import csv
class TestRegisters(unittest.TestCase):
 def headers(self,p):
  with (ROOT/p).open(newline='') as f:return next(csv.reader(f))
 def test_eligibility_register(self): self.assertIn('eligibility_id',self.headers('10_Marketplace/Registers/CUSTOMER_ELIGIBILITY_REGISTER.csv'))
 def test_jurisdiction_matrix(self): self.assertIn('route_status',self.headers('10_Marketplace/Registers/JURISDICTION_ROUTE_MATRIX.csv'))
 def test_privacy_register(self): self.assertIn('legal_basis',self.headers('10_Marketplace/Registers/CONSENT_PRIVACY_REGISTER.csv'))
 def test_rights_register(self): self.assertIn('request_type',self.headers('10_Marketplace/Registers/PRIVACY_RIGHTS_REQUEST_REGISTER.csv'))
 def test_surveillance_register(self): self.assertIn('severity',self.headers('05_Monitoring/Registers/SURVEILLANCE_CASE_REGISTER.csv'))
 def test_reporting_register(self): self.assertIn('reportability',self.headers('05_Monitoring/Registers/REGULATORY_REPORTING_REGISTER.csv'))
 def test_audit_register(self): self.assertIn('before_hash',self.headers('13_Project_Genesis/Registers/AUDIT_EVENT_REGISTER.csv'))
