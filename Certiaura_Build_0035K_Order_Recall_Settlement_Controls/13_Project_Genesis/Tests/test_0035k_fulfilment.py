from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
VAL=ROOT/'13_Project_Genesis'/'Validators'
sys.path.insert(0,str(VAL))

from validate_fulfilment_receipt import validate
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.good=json.loads((ROOT/'10_Marketplace/Examples/valid_fulfilment_excursion.example.json').read_text())
 def test_01_good_passes(self): self.assertEqual(validate(self.good),[])
 def test_02_detects_excursion(self): self.assertTrue(self.good['storage']['excursion_detected'])
 def test_03_quarantined(self): self.assertTrue(self.good['disposition']['quarantined'])
 def test_04_human_disposition(self): self.assertFalse(self.good['disposition']['automation_approved'])
 def test_05_custody_sequence(self): self.assertEqual([1,2,3],[x['sequence'] for x in self.good['chain_of_custody']])
 def test_06_bad_identity(self): d=json.loads(json.dumps(self.good)); d['receipt']['identity_match']=False; self.assertTrue(any('identity' in x for x in validate(d)))
 def test_07_bad_quarantine(self): d=json.loads(json.dumps(self.good)); d['disposition']['quarantined']=False; self.assertTrue(any('quarantine' in x for x in validate(d)))
 def test_08_bad_auto(self): d=json.loads(json.dumps(self.good)); d['disposition']['automation_approved']=True; self.assertTrue(any('automation' in x for x in validate(d)))
