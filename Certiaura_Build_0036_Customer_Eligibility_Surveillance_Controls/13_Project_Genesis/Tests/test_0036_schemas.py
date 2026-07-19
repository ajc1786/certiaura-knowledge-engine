from __future__ import annotations
import json, sys, tempfile, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'13_Project_Genesis'/'Validators'))

class TestSchemas(unittest.TestCase):
 def test_all_json_parse(self):
  for p in ROOT.rglob('*.json'): json.loads(p.read_text())
 def test_customer_schema(self): self.assertEqual(json.loads((ROOT/'10_Marketplace'/'Schemas'/'customer_eligibility.schema.json').read_text())['type'],'object')
 def test_privacy_schema(self): self.assertIn('request_id',json.loads((ROOT/'10_Marketplace'/'Schemas'/'privacy_request.schema.json').read_text())['properties'])
 def test_surveillance_schema(self): self.assertIn('severity',json.loads((ROOT/'05_Monitoring'/'Schemas'/'surveillance_case.schema.json').read_text())['properties'])
 def test_reporting_schema(self): self.assertIn('reportability',json.loads((ROOT/'05_Monitoring'/'Schemas'/'reporting_assessment.schema.json').read_text())['properties'])
 def test_manifest_commit(self): self.assertTrue(json.loads((ROOT/'00_Build_Control'/'BUILD_MANIFEST.json').read_text())['commit_message'].startswith('Add Certiaura Build 0036'))
 def test_no_external_packages(self): self.assertEqual(json.loads((ROOT/'00_Build_Control'/'BUILD_MANIFEST.json').read_text())['external_python_packages'],[])
