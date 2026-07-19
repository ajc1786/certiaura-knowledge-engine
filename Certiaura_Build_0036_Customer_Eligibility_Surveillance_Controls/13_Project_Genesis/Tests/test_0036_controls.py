from __future__ import annotations
import json, sys, tempfile, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'13_Project_Genesis'/'Validators'))

class TestControls(unittest.TestCase):
 def text(self,p): return (ROOT/p).read_text()
 def test_readme_boundary(self): self.assertIn('may not determine legal eligibility',self.text('BUILD_0036_READ_ME_FIRST.md'))
 def test_no_parallel(self): self.assertIn('Do not create a parallel',self.text('BUILD_0036_READ_ME_FIRST.md'))
 def test_numbering_decision(self): self.assertIn('Close the 0035 lettered sequence',self.text('00_Build_Control/DECISION_RECORD_0036.md'))
 def test_privacy_standard(self): self.assertIn('data minimisation',self.text('10_Marketplace/Standards/CONSENT_PRIVACY_ACCESS_STANDARD.md'))
 def test_surveillance_standard(self): self.assertIn('Automation may aggregate and escalate',self.text('05_Monitoring/Standards/POST_MARKET_SURVEILLANCE_STANDARD.md'))
 def test_reporting_standard(self): self.assertIn('may not decide reportability',self.text('05_Monitoring/Standards/REGULATORY_REPORTING_ASSESSMENT_STANDARD.md'))
 def test_filename_length(self): self.assertLessEqual(len(ROOT.name+'.zip'),80)
