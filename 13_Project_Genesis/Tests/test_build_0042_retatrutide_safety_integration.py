from __future__ import annotations
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("v",ROOT/"13_Project_Genesis/Validators/validate_retatrutide_safety_integration.py")
V=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(V)
class Build0042Tests(unittest.TestCase):
 def test_valid_package(self): self.assertEqual(V.validate(ROOT),[])
 def test_signal_count(self):
  o=json.loads((ROOT/"06_Evidence/Retatrutide/RETATRUTIDE_SAFETY_SIGNAL_MATRIX.json").read_text());self.assertEqual(len(o["signals"]),8)
 def test_no_approved_label(self):
  o=json.loads((ROOT/"01_Knowledge_Systems/SKS/Retatrutide/RETATRUTIDE_CONTRAINDICATION_PRECAUTION_MATRIX.json").read_text());self.assertFalse(o["approved_label_exists"])
 def test_monitoring_is_non_prescriptive(self):
  o=json.loads((ROOT/"05_Monitoring/Retatrutide/RETATRUTIDE_MONITORING_EVENT_MODEL.json").read_text());self.assertIn("personal dose recommendation",o["prohibited_fields"])
 def test_outcome_uncertainty(self):
  o=json.loads((ROOT/"06_Evidence/Retatrutide/RETATRUTIDE_CLINICAL_OUTCOME_INTEGRATION.json").read_text());self.assertTrue(any(x["evidence_status"]=="UNRESOLVED_ONGOING_TRIALS" for x in o["outcomes"]))
 def test_invalid_contra_fixture(self):
  o=json.loads((ROOT/"13_Project_Genesis/Tests/Fixtures/Build_0042/invalid_approved_contraindication.example.json").read_text());self.assertTrue(o["approved_label_exists"])
 def test_invalid_evidence_fixture(self):
  o=json.loads((ROOT/"13_Project_Genesis/Tests/Fixtures/Build_0042/invalid_missing_evidence.example.json").read_text());self.assertNotIn(o["evidence_refs"][0],V.ALLOWED_EVIDENCE)
 def test_invalid_prescriptive_fixture(self):
  text=(ROOT/"13_Project_Genesis/Tests/Fixtures/Build_0042/invalid_prescriptive_monitoring.example.json").read_text().lower();self.assertIn("increase the dose",text)
if __name__=="__main__":unittest.main()
