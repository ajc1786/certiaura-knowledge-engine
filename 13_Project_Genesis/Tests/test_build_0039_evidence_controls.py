from __future__ import annotations
import importlib.util, json, sys, unittest
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[2]; V=ROOT/"13_Project_Genesis"/"Validators"; F=Path(__file__).parent/"Fixtures"/"Build_0039"
sys.path.insert(0,str(V))
from validate_citation_provenance import validate as vc
from validate_evidence_ingestion import validate as vi
from validate_living_evidence_surveillance import validate as vs
from validate_retraction_correction_event import validate as vr
from validate_scientific_review import validate as vrev
from assess_evidence_update_impact import validate as vamp

def load(n): return json.loads((F/n).read_text(encoding="utf-8"))
class EvidenceControls(unittest.TestCase):
    def test_valid_records(self):
        for fn,validator in [("valid_citation.example.json",vc),("valid_evidence_ingestion.example.json",vi),("valid_surveillance_query.example.json",vs),("valid_surveillance_event.example.json",vs),("valid_retraction_event.example.json",vr),("valid_scientific_review.example.json",vrev),("valid_impact_assessment.example.json",vamp)]: self.assertTrue(validator(load(fn)).valid,fn)
    def test_invalid_records(self):
        for fn,validator in [("invalid_unreviewed_citation.example.json",vc),("invalid_full_text_rights.example.json",vi),("invalid_surveillance_query.example.json",vs),("invalid_retraction_no_action.example.json",vr),("invalid_ai_only_review.example.json",vrev)]: self.assertFalse(validator(load(fn)).valid,fn)
if __name__=="__main__": unittest.main()
